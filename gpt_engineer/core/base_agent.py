from gpt_engineer.core.code import Code
from gpt_engineer.core.base_version_manager import BaseVersionManager
from gpt_engineer.core.ai import AI
from abc import ABC, abstractmethod


class BaseAgent(ABC):
    @abstractmethod
    def init(self, prompt: str) -> Code:
        pass

    @abstractmethod
    def improve(self, prompt: str, code: Code) -> Code:
        pass
