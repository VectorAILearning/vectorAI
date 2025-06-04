from agents.base_agent import BaseAgent
from core.config import openai_settings
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from .prompts import HUMAN_PROMPT, SYSTEM_PROMPT


class CoursePlanAgent(BaseAgent):
    def __init__(self):
        llm = ChatOpenAI(
            api_key=openai_settings.OPENAI_API_KEY,
            model=openai_settings.OPENAI_MODEL_COURSE_PLAN,
            temperature=openai_settings.OPENAI_TEMPERATURE_COURSE_PLAN,
        )
        prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT),
                ("human", HUMAN_PROMPT),
            ]
        )
        super().__init__(llm=llm, prompt_template=prompt_template)

    def generate_course(self, profile_summary: str) -> dict:
        return self.call_json_llm({"profile_summary": profile_summary})
