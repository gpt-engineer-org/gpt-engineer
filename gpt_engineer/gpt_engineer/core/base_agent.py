from gpt_engineer.core.code import Code
from gpt_engineer.core.base_version_manager import BaseVersionManager
from gpt_engineer.core.ai import AI
from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """
    Abstract base class for an agent that interacts with the AI model.

    This class defines the interface for initializing and improving code
    based on a given prompt. Implementations of this class are expected to
    provide concrete methods for these actions.
    """
    @abstractmethod
    def init(self, prompt: str) -> Code:
        pass

    @abstractmethod
    def improve(self, prompt: str, code: Code) -> Code:
        pass
