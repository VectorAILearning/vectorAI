import json
import time
import uuid

from agents.audit_agent.agent import AuditAgent
from models import PreferenceModel
from models.task import TaskTypeEnum
from services import RedisCacheService, get_cache_service
from services.message_bus import push_and_publish
from workers.generate_tasks.audit_tasks import _msg
from starlette.websockets import WebSocket
from utils.uow import UnitOfWork
from workers.generate_tasks.generate_tasks import GenerateDeepEnum


class AuditDialogService:
    def __init__(
        self,
        uow: UnitOfWork | None = None,
        cache_service: RedisCacheService | None = None,
        agent: AuditAgent | None = None,
    ):
        self.cache_service = cache_service or get_cache_service()
        self.agent = agent or AuditAgent()
        self.uow = uow

    @staticmethod
    def _history_str(q: list[str], a: list[str], first: str) -> str:
        blocks = [f"Вопрос: Здравствуйте! Опишите вашу цель?\nОтвет: {first}"]
        for qi, ai in zip(q, a):
            blocks.append(f"Вопрос: {qi}\nОтвет: {ai}")
        return "\n".join(blocks)

    async def send_session_info(self, ws: WebSocket, sid: str) -> None:
        await ws.send_text(
            json.dumps(
                {
                    "type": "session_info",
                    "session_id": sid,
                    "messages": await self.cache_service.get_messages(sid),
                    "reset_count": await self.cache_service.get_reset_count(sid),
                }
            )
        )

    async def get_messages(self, sid: str):
        return await self.cache_service.get_messages(str(sid))

    async def run_dialog(self, ws: WebSocket, sid: str):
        stored = await self.get_messages(sid)

        if any(m.get("type") in ("system", "audit_done") for m in stored):
            return

        q, a = [], []
        first_user: dict | None = None

        for m in stored:
            if m["who"] == "user" and first_user is None:
                first_user = m
            elif m["who"] == "bot" and m["type"] == "chat":
                q.append(m["text"])
            elif m["who"] == "user" and q:
                a.append(m["text"])

        if first_user is None:
            raw = await ws.receive_text()
            try:
                first_user = json.loads(raw)
            except Exception:
                first_user = {"text": raw, "who": "user", "type": "chat"}
            await self.cache_service.add_message(str(sid), first_user)

        if not q:
            ask = self.agent.call_llm(
                {"prompt": self.agent.get_initial_question(first_user.get("text"))}
            )
            await push_and_publish(_msg("bot", ask), sid)
            q.append(ask)

        for step in range(len(a) + 1, self.agent.max_questions + 1):
            raw = await ws.receive_text()
            try:
                u_ans = json.loads(raw)
            except Exception:
                u_ans = {"text": raw, "who": "user", "type": "chat"}
            await self.cache_service.add_message(sid, u_ans)
            a.append(u_ans["text"])

            if step == self.agent.max_questions:
                break

            history = self._history_str(q, a, first_user["text"])
            ask = self.agent.call_llm(
                {
                    "prompt": self.agent.get_initial_question(
                        self.agent.next_question_prompt(history)
                    )
                }
            )
            await push_and_publish(_msg("bot", ask), sid)
            q.append(ask)

        await self.cache_service.set_session_status(sid, "course_creating")
        await push_and_publish(
            _msg(
                "system",
                "Аудит завершён. Сейчас начнётся подготовка профиля и курса.",
                "course_created_start",
            ),
            sid,
        )

        history_full = self._history_str(q, a, first_user["text"])
        await ws.app.state.arq_pool.enqueue_job(
            "generate",
            _queue_name="course_generation",
            task_type=TaskTypeEnum.generate_course,
            audit_history=history_full,
            sid=sid,
            deep=GenerateDeepEnum.first_lesson.value,
        )

    async def create_user_preference_by_audit_history(
        self, audit_history: str, sid: str | None = None, user_id: str | None = None
    ) -> PreferenceModel:
        summary = self.agent.summarize_profile_prompt(audit_history)
        return await self.uow.audit_repo.create_user_preference(
            summary, sid=sid, user_id=user_id
        )
