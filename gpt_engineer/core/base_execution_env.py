from abc import ABC, abstractmethod
from gpt_engineer.core.files_dict import FilesDict
from subprocess import Popen


class BaseExecutionEnv(ABC):
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
    def run(self, command: str, timeout: int | None = None) -> tuple[str, str, int]:
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
