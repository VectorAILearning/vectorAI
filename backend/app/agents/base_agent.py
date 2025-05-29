import re
from abc import ABC, abstractmethod


class BaseAgent(ABC):
    def __init__(self, llm=None, **kwargs):
        """
        llm — любой объект (например, ChatOpenAI, HuggingFace, LocalLLM, etc.)
        kwargs — дополнительные параметры (можно сохранять их как self.config)
        """
        self.llm = llm
        self.config = kwargs

    @staticmethod
    def remove_surrogates(text: str) -> str:
        """Удаляет суррогатные пары unicode (например, эмодзи, сломанные символы)."""
        return re.sub(r"[\ud800-\udfff]", "", text)

    def call_llm(self, prompt: str) -> str:
        messages = [self.get_system_message(), self.get_human_message(prompt)]
        result = self.llm.invoke(messages).content
        return self.remove_surrogates(result)

    @abstractmethod
    def get_system_message(self):
        pass

    @abstractmethod
    def get_human_message(self, prompt: str):
        pass
