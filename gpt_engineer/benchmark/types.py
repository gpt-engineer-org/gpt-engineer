from dataclasses import dataclass
from subprocess import Popen
from typing import Callable

from gpt_engineer.core.files_dict import FilesDict
from gpt_engineer.core.base_execution_env import BaseExecutionEnv


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
    process: Popen | None
    stdout: str | None
    stderr: str | None


Assertion = Callable[[Assertable], bool]


@dataclass
class Task:
    name: str
    initial_code: FilesDict | None
    command: str | None
    prompt: str
    assertions: dict[str, Assertion] | None


@dataclass
class Benchmark:
    """A benchmark is a collection of tasks that evaluate a model's performance."""

    name: str
    tasks: list[Task]
    timeout: int | None = None


@dataclass
class TaskResult:
    task_name: str
    assertion_results: dict[str, bool]
    duration: float
