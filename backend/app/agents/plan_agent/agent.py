import json
from typing import List

from agents.base_agent import BaseAgent
from core.config import openai_settings
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from .prompts import SYSTEM_PROMPT


class CoursePlanAgent(BaseAgent):
    def __init__(self):
        llm = ChatOpenAI(
            api_key=openai_settings.OPENAI_API_KEY,
            model=openai_settings.OPENAI_MODEL_AUDIT,
            temperature=0.2,
        )
        super().__init__(llm=llm)

    def generate_course(self, profile_summary: str) -> dict:
        prompt = (
            f"Описание пользователя и его целей:\n{profile_summary}\n"
            "Составь подробную и практико-ориентированную структуру курса строго по формату, полностью под задачи этого человека."
        )
        messages = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)]
        response = self.llm.invoke(messages).content
        try:
            data = json.loads(response)
        except Exception:
            data = {"raw": response}
        return data

    def get_system_message(self):
        return SystemMessage(content=SYSTEM_PROMPT)

    def get_human_message(self, prompt: str):
        return HumanMessage(content=prompt)
