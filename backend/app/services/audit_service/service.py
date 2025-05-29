import json
import traceback

from agents.audit_agent import AuditAgent
from arq import create_pool


class AuditDialogService:
    def __init__(self, websocket, redis_service, session_id):
        self.websocket = websocket
        self.redis_service = redis_service
        self.session_id = session_id
        self.agent = AuditAgent()

    async def send_session_info(self):
        messages = await self.redis_service.get_messages(self.session_id)
        reset_count = await self.redis_service.get_reset_count(self.session_id)
        await self.websocket.send_text(
            json.dumps(
                {
                    "type": "session_info",
                    "session_id": self.session_id,
                    "messages": messages,
                    "reset_count": reset_count,
                }
            )
        )

    async def handle_reset_chat(self):
        await self.redis_service.clear_messages(self.session_id)
        await self.redis_service.increment_reset_count(self.session_id)
        await self.send_session_info()
        await self.websocket.close()

    async def run_dialog(self):
        # 1. Восстанавливаем историю, если она есть
        messages = await self.redis_service.get_messages(self.session_id)
        if messages:
            # Проверяем, завершён ли опрос
            if any(m.get("type") in ("system", "audit_done") for m in messages):
                return  # Опрос уже завершён, ничего не делаем

        all_questions = []
        all_answers = []
        history = "Вопрос: Здравствуйте! Опишите вашу цель (чему хотите научиться?)\n"
        user_msg_obj = None

        # 2. Восстанавливаем историю, если она есть
        messages = await self.redis_service.get_messages(self.session_id)
        if messages:
            for msg in messages:
                if msg["who"] == "user" and not all_questions:
                    # Первый пользовательский ввод — это client_prompt
                    user_msg_obj = msg
                    history += f"Ответ: {msg['text']}\n"
                elif msg["who"] == "bot" and msg.get("type") == "chat":
                    all_questions.append(msg["text"])
                elif msg["who"] == "user" and all_questions:
                    all_answers.append(msg["text"])
                    history += f"\nВопрос: {all_questions[-1]}\nОтвет: {msg['text']}"
        else:
            user_msg = await self.websocket.receive_text()
            try:
                user_msg_obj = json.loads(user_msg)
            except Exception:
                user_msg_obj = {"text": user_msg, "who": "user", "type": "chat"}
            await self.redis_service.add_message(self.session_id, user_msg_obj)
            history += f"Ответ: {user_msg_obj['text']}\n"

        # 3. Если не было вопросов — задаём первый
        if not all_questions:
            question = self.agent.call_llm(
                self.agent.get_initial_question(user_msg_obj["text"])
            )
            bot_msg = {"who": "bot", "text": question, "type": "chat"}
            await self.redis_service.add_message(self.session_id, bot_msg)
            await self.websocket.send_text(json.dumps(bot_msg))
            all_questions.append(question)

        # 4. Продолжаем опрос с нужного шага
        for question_num in range(len(all_answers) + 1, self.agent.max_questions + 1):
            user_answer_raw = await self.websocket.receive_text()
            try:
                user_answer = json.loads(user_answer_raw)
            except Exception:
                user_answer = {"text": user_answer_raw, "who": "user", "type": "chat"}
            await self.redis_service.add_message(self.session_id, user_answer)
            all_answers.append(user_answer["text"])
            history += f"\nВопрос: {all_questions[-1]}\nОтвет: {user_answer['text']}"

            if question_num == self.agent.max_questions:
                break

            question = self.agent.call_llm(self.agent.next_question_prompt(history))
            bot_msg = {"who": "bot", "text": question, "type": "chat"}
            await self.redis_service.add_message(self.session_id, bot_msg)
            await self.websocket.send_text(json.dumps(bot_msg))
            all_questions.append(question)

        # 5. Завершаем опрос, если дошли до конца
        system_msg = {
            "who": "system",
            "text": "Аудит завершён. Сейчас начнётся подготовка профиля и курса.",
            "type": "system",
        }
        await self.redis_service.add_message(self.session_id, system_msg)
        await self.websocket.send_text(json.dumps(system_msg))
        arq_pool = self.websocket.app.state.arq_pool
        await arq_pool.enqueue_job(
            "audit_full_pipeline_task", self.session_id, history, user_msg_obj["text"]
        )
