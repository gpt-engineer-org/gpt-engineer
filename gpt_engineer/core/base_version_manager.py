from abc import ABC, abstractmethod
from gpt_engineer.core.code import Code


class BaseVersionManager(ABC):
    """
    Abstract base class for a version manager.

    This class defines the interface for version managers that handle the creation
    of snapshots for code. Implementations of this class are expected to provide
    a method to create a snapshot of the given code.

    Methods
    -------
    snapshot(code: Code) -> str:
        Create a snapshot of the given code and return a reference to it.
    """

    @abstractmethod
    def snapshot(self, code: Code) -> str:
        pass
