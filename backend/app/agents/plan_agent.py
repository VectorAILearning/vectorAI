import json
from typing import List

from agents.base_agent import BaseAgent
from core.config import openai_settings
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

SYSTEM_PROMPT = """Ты — профессиональный методист и эксперт в создании индивидуальных онлайн-курсов. 
Тебе поступает краткое, но информативное описание пользователя, его уровень, опыт, цели и мотивация. 
Сгенерируй программу онлайн-курса, максимально адаптированную под конкретного человека. 
Обязательно делай следующее:
— Учитывай цели, уровень и пожелания пользователя из описания.
— Не включай темы, которые пользователь уже хорошо знает (упоминай только кратко или исключай).
— Структурируй курс так, чтобы по завершении пользователь гарантированно достиг свою цель.
— Разбей курс на логичные модули (не менее 3), в каждом по 2-4 урока, с чёткой прогрессией и связью с целью пользователя.
— Для каждого курса, модуля и урока обязательно указывай:
    - title (короткое, ёмкое название)
    - description (чёткое, но короткое описание, зачем этот блок нужен и чему научится пользователь)
    - estimated_time_hours (целое или дробное число часов)
— В estimated_time_hours оценивай реально необходимое время исходя из уровня пользователя.
— Не добавляй "воду", делай акцент на темах, которые нужны для достижения индивидуальной цели пользователя.
— Курс должен быть практикоориентированным, современным, с примерами для самостоятельной работы.
— Все тексты только на русском языке, без лишних комментариев, строго в формате JSON, как в примере ниже.
Пример:
{
  "course_title": "Название курса",
  "course_description": "Описание курса",
  "estimated_time_hours": 24,
  "modules": [
    {
      "title": "Название модуля",
      "description": "Описание модуля",
      "estimated_time_hours": 6,
      "lessons": [
        {
          "title": "Название урока",
          "description": "Описание урока",
          "estimated_time_hours": 1.5
        },
        ...
      ]
    },
    ...
  ]
}"""


class CoursePlanAgent(BaseAgent):
    def __init__(self):
        llm = ChatOpenAI(
            api_key=openai_settings.OPENAI_API_KEY,
            model=openai_settings.OPENAI_MODEL_AUDIT,
            temperature=0.2,
            max_tokens=2000,
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
