import json

from agents.base_agent import BaseAgent
from core.config import openai_settings
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from .prompts import HUMAN_PROMPT, SYSTEM_PROMPT


class LessonPlanAgent(BaseAgent):
    def __init__(self):
        llm = ChatOpenAI(
            api_key=SecretStr(openai_settings.OPENAI_API_KEY),
            model=openai_settings.OPENAI_MODEL_LESSON_PLAN,
            temperature=openai_settings.OPENAI_TEMPERATURE_LESSON_PLAN,
        )
        prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT),
                ("human", HUMAN_PROMPT),
            ]
        )
        super().__init__(llm=llm, prompt_template=prompt_template)

    def generate_lesson_content_plan(
        self,
        lesson_description: str,
        user_preferences: str = "",
        course_structure_json: str = "",
    ) -> list:
        input_data = {
            "course_structure_json": course_structure_json,
            "lesson_description": lesson_description,
            "user_preferences": user_preferences,
        }
        data = self.call_json_llm(input_data)
        if isinstance(data, list):
            return data
        return [data]
