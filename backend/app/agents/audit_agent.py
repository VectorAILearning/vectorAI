from agents.base_agent import BaseAgent
from core.config import openai_settings
from langchain_openai import ChatOpenAI

SYSTEM_PROMPT = (
    "Ты — ассистент по опросу для создания персонального онлайн-курса."
    f"Твоя задача — за {openai_settings.AUDIT_MAX_QUESTIONS} вопросов составить портрет пользователя."
    "Учитывай ВСЮ историю вопросов и ответов."
    "НЕ задавай вопросы, если уже получил ответ на этот аспект."
    "Если уже понятно, не трать вопросы на уточнение того, что уже известно."
    "Задавай только по ОДНОМУ самому важному вопросу за раз. "
    "Если всё уже понятно для курса, напиши 'Конец опроса'. "
    "Формат курса на который ты создаёшь портрет пользователя - онлайн курс состоящий из теории, тестов и изображений"
    "Пиши только на русском, без эмодзи."
)


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
        from langchain_core.messages import SystemMessage

        return SystemMessage(content=SYSTEM_PROMPT)

    def get_human_message(self, prompt: str):
        from langchain_core.messages import HumanMessage

        return HumanMessage(content=prompt)

    def call_llm(self, prompt: str) -> str:
        messages = [self.get_system_message(), self.get_human_message(prompt)]
        return self.llm.invoke(messages).content

    @staticmethod
    def get_initial_question(client_prompt: str) -> str:
        return (
            f"Пользователь хочет изучить: {client_prompt}. "
            f"Сформулируй первый важный вопрос, который поможет понять его цели, уровень или мотивацию."
        )

    @staticmethod
    def next_question_prompt(history: str) -> str:
        return (
            f"Вот вся история диалога:\n{history}\n"
            "Сформулируй только следующий вопрос, который поможет лучше понять цели, уровень и мотивацию пользователя. "
            "Не задавай вопросы, на которые уже был получен чёткий ответ. "
        )

    @staticmethod
    def summarize_profile_prompt(history: str, client_prompt: str) -> str:
        return (
            f"История вопросов и ответов:\n{history}\n"
            "Сделай краткое, но информативное описание пользователя, его цели, уровня и мотивации в одном абзаце для персонализации онлайн-курса. "
        )
