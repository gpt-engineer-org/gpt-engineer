from dataclasses import dataclass
from subprocess import Popen
from typing import Callable, Dict, Optional

from gpt_engineer.core.base_execution_env import BaseExecutionEnv
from gpt_engineer.core.files_dict import FilesDict


@dataclass
class Assertable:
    """
    A class representing an object which can be asserted against.

    Attributes:
        files (FilesDict): The code files involved in the assertion.
        env (BaseExecutionEnv): The execution environment in which the code is run.
        process (Popen): The subprocess in which the code is run.
        stdout (str): The standard output from the code execution.
        stderr (str): The standard error from the code execution.
    """

    files: FilesDict
    env: BaseExecutionEnv
    process: Optional[Popen]
    stdout: Optional[str]
    stderr: Optional[str]


Assertion = Callable[[Assertable], bool]


@dataclass
class Task:
    name: str
    initial_code: Optional[FilesDict]
    command: Optional[str]
    prompt: str
    assertions: Optional[Dict[str, Assertion]]


@dataclass
class Benchmark:
    """A benchmark is a collection of tasks that evaluate a model's performance."""

    name: str
    tasks: list[Task]
    timeout: Optional[int] = None


@dataclass
class TaskResult:
    task_name: str
    assertion_results: dict[str, bool]
    duration: float
