from abc import ABC, abstractmethod
from gpt_engineer.core.code import Code


class BaseVersionManager(ABC):
    """
    Abstract base class for a version manager.

    This class defines the interface for managing versions of code, including
    creating snapshots of the code state. Implementations of this class are
    expected to provide concrete methods for these versioning actions.
    """
    @abstractmethod
    def snapshot(self, code: Code) -> str:
        pass
