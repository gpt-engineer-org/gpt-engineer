from abc import ABC, abstractmethod
from gpt_engineer.core.files_dict import FilesDict
from typing import Union
from pathlib import Path


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
    def __init__(self, path: Union[str, Path]):
        pass

    @abstractmethod
    def snapshot(self, files_dict: FilesDict) -> str:
        pass
