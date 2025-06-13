import json
import logging
import re
from abc import ABC

from langchain_core.prompts import ChatPromptTemplate

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    def __init__(self, llm, prompt_template: ChatPromptTemplate, **kwargs):
        """
        llm — объект модели (например, ChatOpenAI)
        prompt_template — ChatPromptTemplate (включает и system, и human части)
        kwargs — доп. параметры
        """
        self.llm = llm
        self.prompt_template = prompt_template
        self.config = kwargs

    @staticmethod
    def remove_surrogates(text: str) -> str:
        """Удаляет суррогатные пары unicode (например, эмодзи, сломанные символы)."""
        return re.sub(r"[\ud800-\udfff]", "", text)

    def call_llm(
        self, input_data: dict, prompt: ChatPromptTemplate | None = None
    ) -> str:
        """
        Выполняет prompt → llm → str (без json)
        """
        try:
            if prompt:
                format_prompt = prompt.format_messages(**input_data)
            else:
                format_prompt = self.prompt_template.format_messages(**input_data)
            result = self.llm.invoke(format_prompt).content
            logger.info(result)
            return self.remove_surrogates(result)
        except Exception as e:
            logger.exception("Ошибка при вызове LLM:")
            return "Произошла ошибка генерации."

    def call_json_llm(
        self, input_data: dict, prompt: ChatPromptTemplate | None = None
    ) -> dict:
        """
        prompt → llm → json (через безопасный парсинг)
        """
        try:
            if prompt:
                format_prompt = prompt.format_messages(**input_data)
            else:
                format_prompt = self.prompt_template.format_messages(**input_data)

            logger.info(f"Prompt: {format_prompt}")
            result = self.llm.invoke(format_prompt).content
            clear_result = self.remove_surrogates(result)
            logger.info(clear_result)
            return json.loads(clear_result)
        except Exception as e:
            logger.exception(f"Ошибка вызова или разбора JSON: {e}")
            return {"raw": "Произошла ошибка генерации."}
