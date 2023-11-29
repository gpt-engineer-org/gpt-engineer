from gpt_engineer.core.code import Code
from gpt_engineer.core.base_version_manager import BaseVersionManager
from gpt_engineer.core.ai import AI
from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """
    Abstract base class for an agent that interacts with code.

    This class defines the interface for agents capable of initializing and improving code
    based on a given prompt. Implementations of this class are expected to provide concrete
    methods for these actions.

    Methods
    -------
    init(prompt: str) -> Code:
        Initialize a new piece of code based on the given prompt.
    improve(prompt: str, code: Code) -> Code:
        Improve an existing piece of code based on the given prompt.
    """

    @abstractmethod
    def init(self, prompt: str) -> Code:
        pass

    @abstractmethod
    def improve(
        self, code: Code, prompt: str, execution_command: str | None = None
    ) -> Code:
        pass
