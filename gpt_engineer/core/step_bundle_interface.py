from abc import ABC, abstractmethod
from gpt_engineer.core.code import Code
from gpt_engineer.core.ai import AI


class StepBundleInterface(ABC):
    @abstractmethod
    def init(self, ai: AI, prompt: str) -> Code:
        pass

    @abstractmethod
    def improve(self, ai: AI, prompt: str) -> Code:
        pass
