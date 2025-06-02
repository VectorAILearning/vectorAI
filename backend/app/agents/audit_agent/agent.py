from agents.base_agent import BaseAgent
from core.config import openai_settings
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from .prompts import SYSTEM_PROMPT


class AuditAgent(BaseAgent):
    def __init__(self):
        llm = ChatOpenAI(
            api_key=openai_settings.OPENAI_API_KEY,
            model=openai_settings.OPENAI_MODEL_AUDIT,
            temperature=openai_settings.OPENAI_TEMPERATURE_AUDIT,
        )
        super().__init__(llm=llm)
        self.max_questions = openai_settings.AUDIT_MAX_QUESTIONS

    def get_system_message(self):
        return SystemMessage(content=SYSTEM_PROMPT.format(n=self.max_questions))

    def get_human_message(self, prompt: str):
        return HumanMessage(content=prompt)

    def call_llm(self, prompt: str) -> str:
        messages = [self.get_system_message(), self.get_human_message(prompt)]
        return self.llm.invoke(messages).content

    @staticmethod
    def get_initial_question(client_prompt: str) -> str:
        return (
            f"Пользователь хочет изучить: {client_prompt}\n"
            "Задай первый ключевой вопрос, чтобы уточнить цель или опыт."
        )

    @staticmethod
    def next_question_prompt(history: str) -> str:
        return (
            f"История диалога:\n{history}\n"
            "Предложи СЛЕДУЮЩИЙ единственный вопрос, который уточнит недостающий аспект. "
        )

    def summarize_profile_prompt(self, history: str) -> str:
        prompt = (
            f"История вопросов и ответов:\n{history}\n"
            "Сделай краткое, но информативное описание пользователя, его цели, уровня и мотивации в одном абзаце для персонализации онлайн-курса. "
        )
        return self.call_llm(prompt)
