import typer

from gpt_engineer.benchmark.benchmark import Benchmark, TaskResult
from gpt_engineer.core.base_agent import Agent
from gpt_engineer.core.default.on_disk_execution_env import OnDiskExecutionEnv


def eval(benchmark: Benchmark, agent: Agent, task_name: str | None = None):
    env = OnDiskExecutionEnv()

    task_results = []
    for task in benchmark.tasks:
        code = agent.improve(task.initial_code, task.prompt, task.command)
        task_results.append(
            TaskResult(
                task_name=task.name,
                assertion_results={
                    assertion_name: assertion(code, env)
                    for assertion_name, assertion in task.assertions.items()
                },
            )
        )
    return task_results
