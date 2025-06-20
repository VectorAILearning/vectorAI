import json
import logging
import uuid

from agents.audit_agent.agent import AuditAgent
from core.database import get_async_session_generator
from models.base import PreferenceModel
from models.task import TaskTypeEnum
from schemas.task import TaskIn
from services import RedisCacheService, get_cache_service
from services.audit_service.repository import AuditRepository
from services.message_bus import push_and_publish
from services.task_service.service import get_task_service
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocket
from utils.ws_msg import _msg
from workers.generate_tasks.course_tasks import GenerateDeepEnum

log = logging.getLogger(__name__)


def get_audit_service(session: AsyncSession) -> "AuditService":
    """
    Фабричный метод для создания AuditService
    """
    audit_repo = AuditRepository(session)
    return AuditService(session, audit_repo)


class AuditService:
    def __init__(
        self,
        session: AsyncSession,
        audit_repo: AuditRepository,
    ):
        self.session = session
        self.audit_repo = audit_repo

    async def create_user_preference_by_audit_history(
        self,
        audit_history: str,
        sid: uuid.UUID | None = None,
        user_id: uuid.UUID | None = None,
    ) -> PreferenceModel:
        summary = AuditAgent().summarize_profile_by_audit_history(audit_history)
        return await self.audit_repo.create_user_preference(
            summary, sid=sid, user_id=user_id
        )


class AuditDialogService:
    def __init__(
        self,
        cache_service: RedisCacheService | None = None,
        agent: AuditAgent | None = None,
    ):
        self.cache = cache_service or get_cache_service()
        self.agent = agent or AuditAgent()

    async def _msgs(self, sid: str) -> list[dict]:
        return await self.cache.get_messages(str(sid))

    async def _save(self, sid: str, msg: dict) -> None:
        await self.cache.add_message(str(sid), msg)

    async def _bot_send(
        self, sid: str, question: str, options: list[str] | None = None
    ) -> dict:
        payload = {"question": question, "options": options or []}
        msg_obj = {
            "who": "bot",
            "type": "chat",
            "text": json.dumps(payload, ensure_ascii=False),
        }
        await push_and_publish(_msg("bot", msg_obj["text"], msg_obj["type"]), sid)
        return msg_obj

    @staticmethod
    def _history_str(msgs: list[dict]) -> str:
        out: list[str] = []
        for m in msgs:
            if m["who"] == "bot":
                q = json.loads(m["text"])["question"]
                out.append(f"Вопрос: {q}")
            elif m["who"] == "user":
                out.append(f"Ответ: {m['text']}")
        return "\n".join(out)

    async def _wait_user(self, ws: WebSocket) -> dict:
        raw = await ws.receive_text()
        try:
            msg = json.loads(raw)
            if not isinstance(msg, dict):
                raise ValueError
        except Exception:
            msg = {"who": "user", "type": "chat", "text": raw}
        return msg

    async def run_dialog(self, ws: WebSocket, sid: str, user_id: str | None = None):
        msgs = await self._msgs(sid)

        while True:
            user_answers = [m for m in msgs if m["who"] == "user"]
            if len(user_answers) >= self.agent.max_questions + 1:
                break

            if not msgs or msgs[-1]["who"] == "bot":
                user_msg = await self._wait_user(ws)
                await self._save(sid, user_msg)
                msgs.append(user_msg)
                continue

            first_prompt = user_answers[0]["text"]
            history = self._history_str(msgs)
            ask = self.agent.build_question_prompt(
                client_prompt=first_prompt,
                history=history if len(user_answers) > 1 else None,
            )
            await self._bot_send(sid, ask["question"], ask.get("options", []))
            msgs.append(
                {
                    "who": "bot",
                    "type": "chat_question",
                    "text": json.dumps(ask, ensure_ascii=False),
                }
            )

        await self.cache.set_session_status(sid, "course_creating")
        await push_and_publish(
            _msg(
                "system",
                "Аудит завершён. Сейчас начнётся подготовка профиля и курса.",
                "course_created_start",
            ),
            sid,
        )

        history_full = self._history_str(msgs)
        job = await ws.app.state.arq_pool.enqueue_job(
            "generate_course",
            _queue_name="course_generation",
            deep=GenerateDeepEnum.first_lesson_content.value,
            audit_history=history_full,
            session_id=sid,
            user_id=user_id,
        )

        async with get_async_session_generator() as async_session:
            task_service = get_task_service(async_session)
            await task_service.create_task(
                TaskIn(
                    id=job.job_id,
                    task_type=TaskTypeEnum.generate_course,
                    params={
                        "deep": GenerateDeepEnum.first_lesson_content.value,
                        "audit_history": history_full,
                    },
                    user_id=uuid.UUID(user_id) if user_id else None,
                    session_id=uuid.UUID(sid) if sid else None,
                )
            )
