from abc import ABC, abstractmethod
from gpt_engineer.core.code import Code
from subprocess import Popen


class BaseExecutionEnv(ABC):
    """
    Abstract base class for an execution environment.

    This class defines the interface for execution environments where code can be run.
    Implementations of this class should provide a method to execute code and return
    the process handle.
    """

    # ToDo: Figure out long term solution to the return variable (potentially a status class?), for now, return a process
    @abstractmethod
    def execute_program(self, code: Code) -> Popen:
        pass
