from agents.base_agent import BaseAgent
from core.config import openai_settings
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from .prompts import HUMAN_PROMPT, SYSTEM_PROMPT


class ContentPlanAgent(BaseAgent):
    def __init__(self):
        llm = ChatOpenAI(
            api_key=SecretStr(openai_settings.OPENAI_API_KEY),
            model=openai_settings.OPENAI_MODEL_LESSON_CONTENT,
            temperature=openai_settings.OPENAI_TEMPERATURE_LESSON_CONTENT,
        )
        prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT),
                ("human", HUMAN_PROMPT),
            ]
        )
        super().__init__(llm=llm, prompt_template=prompt_template)

    def generate_content(
        self,
        type_: str,
        description: str,
        goal: str,
        course_context: str = "",
        lesson_context: str = "",
    ) -> dict:
        input_data = {
            "type_": type_,
            "description": description,
            "goal": goal,
            "course_context": course_context,
            "lesson_context": lesson_context,
        }
        return self.call_json_llm(input_data)
