"""
Module for running benchmarks.

This module defines functions to run benchmarks using a given agent and to print
the results of the benchmark tasks.

Functions
---------
run : function
    Runs the benchmark tasks using the provided agent and returns a list of TaskResult objects.

print_results : function
    Prints the results of the benchmark tasks to the console.
"""
import time

from typing import List

import yaml

from gpt_engineer.benchmark.types import Assertable, Benchmark, TaskResult
from gpt_engineer.core.base_agent import BaseAgent
from gpt_engineer.core.default.disk_execution_env import DiskExecutionEnv


def run(
    agent: BaseAgent,
    benchmark: Benchmark,
    verbose=False,
) -> List[TaskResult]:
    """
    Runs the benchmark tasks using the provided agent and returns a list of TaskResult objects.

    Parameters
    ----------
    agent : BaseAgent
        The agent to use for running the benchmark tasks.
    benchmark : Benchmark
        The benchmark containing the tasks to run.
    verbose : bool, default=False
        A flag to indicate whether to print verbose output during the benchmark.

    Returns
    -------
    List[TaskResult]
        A list of TaskResult objects representing the results of the benchmark tasks.
    """
    task_results = []
    for task in benchmark.tasks:
        print(f"--> Running task: {task.name}\n")

        t0 = time.time()
        files_dict = agent.improve(task.initial_code, task.prompt)
        t1 = time.time()

        env = DiskExecutionEnv()
        env.upload(files_dict)

        if task.command:
            p = env.popen(task.command)
            stdout, stderr = p.communicate(benchmark.timeout)
            stdout, stderr = stdout.decode("utf-8"), stderr.decode("utf-8")
        else:
            p, stdout, stderr = None, None, None

        exec_result = Assertable(
            files=files_dict,
            env=env,
            process=p,
            stdout=stdout,
            stderr=stderr,
        )

        task_results.append(
            TaskResult(
                task_name=task.name,
                assertion_results={
                    assertion_name: assertion(exec_result)
                    for assertion_name, assertion in task.assertions.items()
                },
                duration=t1 - t0,
            )
        )

        if verbose:
            print_results(task_results)
    return task_results


def print_results(results: list[TaskResult]):
    """
    Prints the results of the benchmark tasks to the console.

    Parameters
    ----------
    results : list[TaskResult]
        A list of TaskResult objects representing the results of the benchmark tasks.

    Returns
    -------
    None
    """
    for task_result in results:
        print(f"\n--- Results for {task_result.task_name} ---")
        print(f"{task_result.task_name} ({task_result.duration:.2f}s)")
        for assertion_name, assertion_result in task_result.assertion_results.items():
            checkmark = "✅" if assertion_result else "❌"
            print(f"  {checkmark} {assertion_name}")
        print()

    success_rates = [task_result.success_rate for task_result in results]
    avg_success_rate = sum(success_rates) / len(results)

    total_time = sum(task_result.duration for task_result in results)

    correct_assertions = sum(
        sum(
            assertion_result
            for assertion_result in task_result.assertion_results.values()
        )
        for task_result in results
    )
    total_assertions = sum(
        len(task_result.assertion_results) for task_result in results
    )
    correct_tasks = [
        task_result for task_result in results if task_result.success_rate == 1
    ]

    print("--- Results ---")
    print(f"Total time: {total_time:.2f}s")
    print(f"Completely correct tasks: {len(correct_tasks)}/{len(results)}")
    print(f"Total correct assertions: {correct_assertions}/{total_assertions}")
    print(f"Average success rate: {avg_success_rate * 100}% on {len(results)} tasks")
    print("--- Results ---")
    print()


def export_yaml_results(yaml_path, complete_results, config):
    for results in complete_results.values():
        correct_tasks = [
            task_result
            for task_result in results["detailed"]
            if task_result["solved"] == 1.0
        ]
        fraction_correct = len(correct_tasks) / len(results["detailed"])
        results["fully_solved"] = fraction_correct
    complete_results["config"] = config
    with open(yaml_path, "w") as f:
        yaml.dump(complete_results, f, indent=4)
