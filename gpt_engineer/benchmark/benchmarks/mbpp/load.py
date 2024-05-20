"""
Module for loading MBPP evaluation tasks.

This module provides functionality to load tasks for evaluating GPT-based models
on smaller, more focused tasks. It defines a set of tasks with predefined prompts
and assertions to benchmark the performance of AI models.

Functions
---------
load_mbpp : function
    Loads the MBPP benchmark, which consists of a series coding problems.
"""
from pathlib import Path
from subprocess import TimeoutExpired
from typing import Union

from datasets import Dataset, DatasetDict, load_dataset, load_from_disk

from gpt_engineer.benchmark.bench_config import MbppConfig
from gpt_engineer.benchmark.benchmarks.mbpp.problem import Problem
from gpt_engineer.benchmark.types import Assertable, Benchmark, Task
from gpt_engineer.core.default.disk_execution_env import DiskExecutionEnv
from gpt_engineer.core.files_dict import FilesDict
from gpt_engineer.core.prompt import Prompt

DATASET_PATH = Path(__file__).parent / "dataset"


class MbppAssertion:
    def __init__(self, assertion: str):
        self.assertion = assertion

    def evaluate(self, assertable: Assertable) -> bool:
        generated_code = assertable.files["main.py"]
        code_with_assertion = f"{generated_code}\n{self.assertion}"

        # Create new execution environment for every run to avoid side effects
        env = DiskExecutionEnv()
        env.upload(FilesDict({"main.py": code_with_assertion}))
        pro = env.popen("python main.py")

        try:
            stdout, stderr = pro.communicate(timeout=2)
            stdout, stderr = stdout.decode("utf-8"), stderr.decode("utf-8")
        except TimeoutExpired:
            print("Execution Timeout")
            return False

        return not stderr


def _get_dataset() -> Union[Dataset, DatasetDict]:
    try:
        return load_from_disk(str(DATASET_PATH))
    except FileNotFoundError:
        print("Dataset not found locally, downloading...")

    dataset = load_dataset("mbpp", "sanitized", trust_remote_code=True)
    dataset.save_to_disk(str(DATASET_PATH))

    return dataset


def load_mbpp(config: MbppConfig) -> Benchmark:
    """
    Loads the MBPP benchmark, which consists of a series coding problems.

    Returns
    -------
    Benchmark
        A Benchmark object containing a list of Task objects for the MBPP evaluation.
    """
    dataset = _get_dataset()
    tasks = []
    problems = []
    for dataset_type in ["test", "train"]:
        problems += [
            Problem(
                source_file=problem["source_file"],
                task_id=problem["task_id"],
                prompt=problem["prompt"],
                code=problem["code"],
                test_imports=problem["test_imports"],
                test_list=problem["test_list"],
            )
            for index, problem in enumerate(dataset[dataset_type])
            if index < config.__getattribute__(dataset_type + "_len")
        ]

    for problem in problems:
        prompt = Prompt(
            problem.prompt
            + "Please extend given function without changing it's declaration including arguments."
        )

        tasks.append(
            Task(
                name=str(problem.task_id),
                initial_code=FilesDict({"main.py": problem.starting_code}),
                command=None,  # Explicitly setting `None` because each assertion runs code
                prompt=prompt,
                assertions={
                    f"correct assertion {i}": MbppAssertion(
                        assertion=assertion
                    ).evaluate
                    for i, assertion in enumerate(problem.test_list)
                },
            )
        )

    return Benchmark(
        name="mbpp",
        tasks=tasks,
    )
