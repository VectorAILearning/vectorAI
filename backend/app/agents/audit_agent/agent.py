import logging
from agents.base_agent import BaseAgent
from core.config import openai_settings
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from .prompts import (
    HUMAN_AUDIT_PROMPT,
    SYSTEM_AUDIT_PROMPT,
    SYSTEM_SUMMARY_PROMPT,
    HUMAN_SUMMARY_PROMPT,
)

log = logging.getLogger(__name__)


class AuditAgent(BaseAgent):
    def __init__(self):
        llm = ChatOpenAI(
            api_key=openai_settings.OPENAI_API_KEY,
            model=openai_settings.OPENAI_MODEL_AUDIT,
            temperature=openai_settings.OPENAI_TEMPERATURE_AUDIT,
        )
        self.max_questions = openai_settings.AUDIT_MAX_QUESTIONS
        prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_AUDIT_PROMPT),
                ("human", HUMAN_AUDIT_PROMPT),
            ]
        )
        super().__init__(llm=llm, prompt_template=prompt_template)

    def build_question_prompt(self, client_prompt: str, history: str | None = None) -> dict:
        return self.call_json_llm(input_data={
            "max_questions": self.max_questions, 
            "client_prompt": client_prompt, 
            "history": history
        })

    def summarize_profile_prompt(self, history: str, client_prompt: str) -> str:
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_SUMMARY_PROMPT),
                ("human", HUMAN_SUMMARY_PROMPT),
            ]
        )
        return self.call_llm(input_data={"history": history, "client_prompt": client_prompt}, prompt=prompt)
