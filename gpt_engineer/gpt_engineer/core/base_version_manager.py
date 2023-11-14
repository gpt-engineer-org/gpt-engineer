from abc import ABC, abstractmethod
from gpt_engineer.core.code import Code


class BaseVersionManager(ABC):
    """
    Abstract base class for a version manager.

    This class defines the interface for version managers that handle the creation
    and management of code snapshots. Implementations of this class should provide
    methods to create and retrieve snapshots of code at various stages.
    """
    @abstractmethod
    def snapshot(self, code: Code) -> str:
        pass
