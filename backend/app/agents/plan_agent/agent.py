from agents.base_agent import BaseAgent
from core.config import generation_settings, openai_settings
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from .prompts import (
    HUMAN_PROMPT_COURSE,
    HUMAN_PROMPT_LESSON,
    HUMAN_PROMPT_LESSON_CONTENT,
    HUMAN_PROMPT_MODULE,
    SYSTEM_PROMPT_COURSE,
    SYSTEM_PROMPT_LESSON,
    SYSTEM_PROMPT_LESSON_CONTENT,
    SYSTEM_PROMPT_MODULE,
)


class CoursePlanAgent(BaseAgent):
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=openai_settings.OPENAI_API_KEY,
            model=openai_settings.OPENAI_MODEL_COURSE_PLAN,
            temperature=openai_settings.OPENAI_TEMPERATURE_COURSE_PLAN,
        )
        prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT_COURSE),
                ("human", HUMAN_PROMPT_COURSE),
            ]
        )
        super().__init__(llm=self.llm, prompt_template=prompt_template)

    def generate_course_plan(self, profile_summary: str) -> dict:
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT_COURSE),
                ("human", HUMAN_PROMPT_COURSE),
            ]
        )
        return self.call_json_llm({"profile_summary": profile_summary}, prompt=prompt)

    def generate_module_plan(
        self, course_structure_json: str, user_preferences: str
    ) -> list[dict]:
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT_MODULE),
                ("human", HUMAN_PROMPT_MODULE),
            ]
        )
        return self.call_json_llm(
            {
                "course_structure_json": course_structure_json,
                "user_preferences": user_preferences,
                "max_modules": generation_settings.GENERATION_MAX_MODULES,
            },
            prompt=prompt,
        )

    def generate_lesson_plan(
        self,
        course_structure_json: str,
        module_structure_json: str,
        user_preferences: str,
    ) -> list[dict]:
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT_LESSON),
                ("human", HUMAN_PROMPT_LESSON),
            ]
        )
        return self.call_json_llm(
            {
                "module_structure_json": module_structure_json,
                "course_structure_json": course_structure_json,
                "user_preferences": user_preferences,
                "max_lessons": generation_settings.GENERATION_MAX_LESSONS,
            },
            prompt=prompt,
        )

    def generate_lesson_content_plan(
        self,
        course_structure_json: str,
        module_structure_json: str,
        lesson_structure_json: str,
        user_preferences: str,
    ) -> list[dict]:
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT_LESSON_CONTENT),
                ("human", HUMAN_PROMPT_LESSON_CONTENT),
            ]
        )
        return self.call_json_llm(
            {
                "course_structure_json": course_structure_json,
                "module_structure_json": module_structure_json,
                "lesson_structure_json": lesson_structure_json,
                "user_preferences": user_preferences,
                "max_contents": generation_settings.GENERATION_MAX_CONTENTS,
            },
            prompt=prompt,
        )
