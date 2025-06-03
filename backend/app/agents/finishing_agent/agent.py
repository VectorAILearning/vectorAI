from agents.base_agent import BaseAgent
from core.config import openai_settings
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from .prompts import SYSTEM_PROMPT


class FinishingAgent(BaseAgent):
    def __init__(self):
        llm = ChatOpenAI(
            api_key=openai_settings.OPENAI_API_KEY,
            model=openai_settings.OPENAI_MODEL_FINISHER,
            temperature=openai_settings.OPENAI_TEMPERATURE_FINISHER,
        )
        super().__init__(llm=llm)

    def get_system_message(self):
        return SystemMessage(content=SYSTEM_PROMPT)

    def get_human_message(self, prompt: str):
        return HumanMessage(content=prompt)

    def finish_course(self, course_summary: str) -> str:
        prompt = f"Кратко подведи итог курса на основе описания:\n{course_summary}"
        return self.call_llm(prompt)
