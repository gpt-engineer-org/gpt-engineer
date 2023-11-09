from abc import ABC, abstractmethod
from gpt_engineer.core.code import Code
from subprocess import Popen
class BaseExecutionEnv(ABC):

    #ToDo: Figure out long term solution to the return variable (potentially a status class?), for now, return a process
    @abstractmethod
    def execute_program(self, code: Code) -> Popen:
        pass

