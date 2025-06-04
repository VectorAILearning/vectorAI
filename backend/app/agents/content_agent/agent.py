import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from core.config import openai_settings
from .prompts import SYSTEM_PROMPT

class ContentAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=openai_settings.OPENAI_API_KEY,
            model=openai_settings.OPENAI_MODEL_LESSON_CONTENT,
            temperature=openai_settings.OPENAI_TEMPERATURE_LESSON_CONTENT,
        )
        self.system_message = SystemMessage(content=SYSTEM_PROMPT)

    def generate_content(self, type_: str, description: str, goal: str, course_context: str = "", lesson_context: str = "") -> dict:
        prompt = (
            f"Контекст курса (JSON):\n{course_context}\n"
            f"Контекст урока (JSON):\n{lesson_context}\n"
            f"Тип блока: {type_}\n"
            f"Описание: {description}\n"
            f"Цель: {goal}\n"
        )
        messages = [self.system_message, HumanMessage(content=prompt)]
        response = self.llm.invoke(messages).content
        try:
            return json.loads(response)
        except Exception:
            return {"raw": response} 