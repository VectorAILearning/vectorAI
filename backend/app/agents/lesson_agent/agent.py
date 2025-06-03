import json

from agents.base_agent import BaseAgent
from core.config import openai_settings
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from .prompts import SYSTEM_PROMPT


class LessonPlanAgent(BaseAgent):
    def __init__(self):
        llm = ChatOpenAI(
            api_key=openai_settings.OPENAI_API_KEY,
            model=openai_settings.OPENAI_MODEL_LESSON_PLAN,
            temperature=openai_settings.OPENAI_TEMPERATURE_LESSON_PLAN,
        )
        super().__init__(llm=llm)

    def get_system_message(self):
        return SystemMessage(content=SYSTEM_PROMPT)

    def get_human_message(self, prompt: str):
        return HumanMessage(content=prompt)

    def generate_lesson_content_plan(
        self, lesson_description: str, user_preferences: str = "", course_structure_json: str = ""
    ) -> list:
        prompt = (
            (f"Структура курса и контент предыдущих уроков (JSON):\n{course_structure_json}\n") +
            f"Описание урока:\n{lesson_description}\n"
            f"Предпочтения пользователя:\n{user_preferences}\n"
            "Сгенерируй разнообразный план контента для этого урока строго по формату."
        )
        messages = [self.get_system_message(), self.get_human_message(prompt)]
        response = self.llm.invoke(messages).content
        try:
            data = json.loads(response)
        except Exception:
            data = [{"raw": response}]
        return data
