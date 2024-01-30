from abc import ABC, abstractmethod
from subprocess import Popen
from typing import Optional, Tuple

from gpt_engineer.core.files_dict import FilesDict


class BaseExecutionEnv(ABC):
    """
    Abstract base class for an execution environment capable of running code.

    This class defines the interface for execution environments that can execute commands,
    handle processes, and manage file uploads and downloads.

    Methods
    -------
    run(command: str, timeout: Optional[int]) -> Tuple[str, str, int]
        Abstract method to run a command in the execution environment.
    popen(command: str) -> Popen
        Abstract method to start a process for a command in the execution environment.
    upload(files: FilesDict) -> BaseExecutionEnv
        Abstract method to upload files to the execution environment.
    download() -> FilesDict
        Abstract method to download files from the execution environment.
    """

    """
    Abstract base class for an execution environment.

    This class defines the interface for execution environments that can run code.
    Implementations of this class are expected to provide a method to execute code
    and potentially handle the execution process.

    Methods
    -------
    execute_program(code: Code) -> Popen:
        Execute the given code and return the process handle.
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
