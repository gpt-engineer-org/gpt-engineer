from gpt_engineer.core.files_dict import FilesDict
from gpt_engineer.core.version_manager import BaseVersionManager
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
    def init(self, prompt: str) -> FilesDict:
        pass

    @abstractmethod
    def improve(self, files_dict: FilesDict, prompt: str) -> FilesDict:
        pass
