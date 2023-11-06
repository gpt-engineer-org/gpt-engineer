from abc import ABC, abstractmethod
from gpt_engineer.core.domain import Code


class StepsInterface(ABC):

    @abstractmethod
    def gen_code(self, prompt: str) -> Code:
        pass

    @abstractmethod
    def improve(self, prompt: str) -> Code:
        pass
