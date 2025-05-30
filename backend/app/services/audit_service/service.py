import json
import time
import uuid

from agents.audit_agent import AuditAgent
from services.message_bus import push_and_publish


class AuditDialogService:
    def __init__(self, websocket, redis_service, session_id: str):
        self.ws = websocket
        self.redis = redis_service
        self.sid = session_id
        self.agent = AuditAgent()

    @staticmethod
    def _history_str(q: list[str], a: list[str], first: str) -> str:
        """Превращаем Q/A списки в строку для prompt."""
        blocks = [f"Вопрос: Здравствуйте! Опишите вашу цель?\nОтвет: {first}"]
        for qi, ai in zip(q, a):
            blocks.append(f"Вопрос: {qi}\nОтвет: {ai}")
        return "\n".join(blocks)

    async def send_session_info(self):
        await self.ws.send_text(
            json.dumps(
                {
                    "type": "session_info",
                    "session_id": self.sid,
                    "messages": await self.redis.get_messages(self.sid),
                    "reset_count": await self.redis.get_reset_count(self.sid),
                }
            )
        )

    async def run_dialog(self):
        stored = await self.redis.get_messages(self.sid) or []

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
            raw = await self.ws.receive_text()
            try:
                first_user = json.loads(raw)
            except Exception:
                first_user = {"text": raw, "who": "user", "type": "chat"}
            await self.redis.add_message(self.sid, first_user)

        if not q:
            ask = self.agent.call_llm(
                self.agent.get_initial_question(first_user["text"])
            )
            await push_and_publish(
                self.sid,
                {
                    "id": str(uuid.uuid4()),
                    "ts": time.time(),
                    "who": "bot",
                    "type": "chat",
                    "text": ask,
                },
            )
            q.append(ask)

        for step in range(len(a) + 1, self.agent.max_questions + 1):
            raw = await self.ws.receive_text()
            try:
                u_ans = json.loads(raw)
            except Exception:
                u_ans = {"text": raw, "who": "user", "type": "chat"}
            await self.redis.add_message(self.sid, u_ans)
            a.append(u_ans["text"])

            if step == self.agent.max_questions:
                break

            history = self._history_str(q, a, first_user["text"])
            ask = self.agent.call_llm(self.agent.next_question_prompt(history))
            await push_and_publish(
                self.sid,
                {
                    "id": str(uuid.uuid4()),
                    "ts": time.time(),
                    "who": "bot",
                    "type": "chat",
                    "text": ask,
                },
            )
            q.append(ask)

        await push_and_publish(
            self.sid,
            {
                "id": str(uuid.uuid4()),
                "ts": time.time(),
                "who": "system",
                "type": "system",
                "text": "Аудит завершён. Сейчас начнётся подготовка профиля и курса.",
            },
        )

        history_full = self._history_str(q, a, first_user["text"])
        await self.ws.app.state.arq_pool.enqueue_job(
            "audit_full_pipeline_task", self.sid, history_full, first_user["text"]
        )
