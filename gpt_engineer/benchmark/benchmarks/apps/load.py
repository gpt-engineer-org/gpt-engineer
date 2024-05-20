"""
Module for loading APPS evaluation tasks.

This module provides functionality to load tasks for evaluating GPT-based models
on smaller, more focused tasks. It defines a set of tasks with predefined prompts
and assertions to benchmark the performance of AI models.

Functions
---------
load_apps : function
    Loads the APPS benchmark, which consists of a series coding problems.
"""
from pathlib import Path
from subprocess import TimeoutExpired
from typing import Union

from datasets import Dataset, DatasetDict, load_dataset, load_from_disk

from gpt_engineer.benchmark.bench_config import AppsConfig
from gpt_engineer.benchmark.benchmarks.apps.problem import Problem
from gpt_engineer.benchmark.types import Assertable, Benchmark, Task
from gpt_engineer.core.default.disk_execution_env import DiskExecutionEnv
from gpt_engineer.core.files_dict import FilesDict
from gpt_engineer.core.prompt import Prompt

DATASET_PATH = Path(__file__).parent / "dataset"


class AppsAssertion:
    def __init__(self, expected: str, command: str):
        self.expected_output = self._format(expected)
        self.command = command

    def evaluate(self, assertable: Assertable) -> bool:
        # Create new execution environment for every run to avoid side effects
        env = DiskExecutionEnv()
        env.upload(assertable.files)
        pro = env.popen(self.command)
        try:
            stdout, stderr = pro.communicate(timeout=2)
            stdout, stderr = stdout.decode("utf-8"), stderr.decode("utf-8")
        except TimeoutExpired:
            print("Execution Timeout")
            return False

        return self.expected_output in self._format(stdout)

    def _format(self, string: str) -> str:
        return string.replace(" ", "").replace("\n", "")


def _get_dataset() -> Union[Dataset, DatasetDict]:
    try:
        return load_from_disk(str(DATASET_PATH))
    except FileNotFoundError:
        print("Dataset not found locally, downloading...")

    dataset = load_dataset("codeparrot/apps", trust_remote_code=True)
    dataset.save_to_disk(str(DATASET_PATH))

    return dataset


def load_apps(config: AppsConfig) -> Benchmark:
    """
    Loads the APPS benchmark, which consists of a series coding problems.

    Returns
    -------
    Benchmark
        A Benchmark object containing a list of Task objects for the APPS evaluation.
    """
    dataset = _get_dataset()
    tasks = []
    problems = list()
    for dataset_type in ["test", "train"]:
        problems += [
            Problem(
                id=problem["problem_id"],
                question=problem["question"],
                input_output=problem["input_output"],
                starter_code=problem["starter_code"],
            )
            for index, problem in enumerate(dataset[dataset_type])
            if (index < config.__getattribute__(dataset_type + "_end_index"))
            and (index >= config.__getattribute__(dataset_type + "_start_index"))
        ]

    for problem in problems:
        prompt = Prompt(
            problem.question
            + "\nThe program, including its inputs, should be run from the command "
            "line like 'python main \"input1 input2 etc \"', with all inputs inside "
            "the quotation marks. The program should not read inputs from stdin."
        )

        tasks.append(
            Task(
                name=str(problem.id),
                initial_code=FilesDict({"main.py": problem.starter_code}),
                command=None,  # Explicitly setting `None` because each assertion specifies its command
                prompt=prompt,
                assertions={
                    f"correct output {i}": AppsAssertion(
                        expected=problem.outputs[i],
                        command="python main.py" + ' "' + problem.inputs[i] + '"',
                    ).evaluate
                    for i in range(
                        min(len(problem.outputs), config.examples_per_problem)
                    )
                },
            )
        )

    return Benchmark(
        name="apps",
        tasks=tasks,
    )
