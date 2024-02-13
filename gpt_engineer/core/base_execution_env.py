from abc import ABC, abstractmethod
from subprocess import Popen
from typing import Optional, Tuple

from gpt_engineer.core.files_dict import FilesDict


class BaseExecutionEnv(ABC):
    """
    Abstract base class for an execution environment capable of running code.

    This class defines the interface for execution environments that can execute commands,
    handle processes, and manage file uploads and downloads.
    """

    @abstractmethod
    def run(self, command: str, timeout: Optional[int] = None) -> Tuple[str, str, int]:
        """
        Runs a command in the execution environment.
        """
        raise NotImplementedError

    @abstractmethod
    def popen(self, command: str) -> Popen:
        """
        Runs a command in the execution environment.
        """
        raise NotImplementedError

    @abstractmethod
    def upload(self, files: FilesDict) -> "BaseExecutionEnv":
        """
        Uploads files to the execution environment.
        """
        raise NotImplementedError

    @abstractmethod
    def download(self) -> FilesDict:
        """
        Downloads files from the execution environment.
        """
        raise NotImplementedError
