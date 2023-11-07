from abc import ABC, abstractmethod
from gpt_engineer.core.code import Code

class VersionManagerInterface(ABC):

    @abstractmethod
    def snapshot(self, code: Code) -> str:
        pass