from dataclasses import dataclass
from typing import Callable

from gpt_engineer.core.base_execution_env import ExecutionEnv
from gpt_engineer.core.code import Files

Assertion = Callable[[Files, ExecutionEnv], bool]


@dataclass
class Task:
    name: str
    initial_code: Files | None
    command: str | None
    prompt: str
    assertions: dict[str, Assertion] | None


@dataclass
class Benchmark:
    """A benchmark is a collection of tasks that evaluate a model's performance."""

    name: str
    tasks: list[Task]


@dataclass
class TaskResult:
    task_name: str
    assertion_results: dict[str, bool]
    duration: float
