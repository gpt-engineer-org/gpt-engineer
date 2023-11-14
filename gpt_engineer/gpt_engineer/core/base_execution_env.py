from abc import ABC, abstractmethod
from gpt_engineer.core.code import Code
from subprocess import Popen


class BaseExecutionEnv(ABC):
    """
    Abstract base class for an execution environment.

    This class defines the interface for executing a program represented by
    a `Code` object. Implementations of this class are expected to provide
    a concrete method for executing the code and handling the execution process.
    """
    # ToDo: Figure out long term solution to the return variable (potentially a status class?), for now, return a process
    @abstractmethod
    def execute_program(self, code: Code) -> Popen:
        pass
