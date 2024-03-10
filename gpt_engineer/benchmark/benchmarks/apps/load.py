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
from collections import OrderedDict
from typing import Union

from gpt_engineer.benchmark.benchmarks.apps.problem import Problem
from gpt_engineer.benchmark.benchmarks.apps.problems import PROBLEM_IDS
from gpt_engineer.benchmark.types import Benchmark, Task
from gpt_engineer.core.files_dict import FilesDict
from datasets import load_dataset, load_from_disk, Dataset, DatasetDict

DATASET_PATH = "gpt_engineer/benchmark/benchmarks/apps/dataset"
MAX_N_TEST_EXAMPLES = 10


class AppsAssertion:
    def __init__(self, reference):
        self.reference = reference.replace(" ", "").replace("\n", "")

    def evaluate(self, assertable):
        return self.reference in assertable.stdout.replace(" ", "").replace("\n", "")


def _get_dataset() -> Union[Dataset, DatasetDict]:
    try:
        return load_from_disk(DATASET_PATH)
    except FileNotFoundError:
        print('Dataset not found locally, downloading...')

    dataset = load_dataset("codeparrot/apps")
    dataset.save_to_disk(DATASET_PATH)

    return dataset


def load_apps():
    """
    Loads the APPS benchmark, which consists of a series coding problems.

    Returns
    -------
    Benchmark
        A Benchmark object containing a list of Task objects for the APPS evaluation.
    """
    dataset = _get_dataset()
    tasks = []

    problems = [Problem(
        id=problem['problem_id'],
        question=problem['question'],
        input_output=problem['input_output'],
        starter_code=problem['starter_code'],
    ) for problem in dataset['test'] if problem['problem_id'] in PROBLEM_IDS]

    for problem in problems:
        tasks.append(
            Task(
                name=str(problem.id),
                initial_code=FilesDict({"main.py": problem.starter_code}),
                command="python main.py",
                prompt=problem.question + "\nThe program, including its inputs, should be run from the command "
                                          "line like 'python main \"input1 input2 etc \"', with all inputs inside "
                                          "the quotation marks. The program should not read inputs from stdin.",
                inputs=problem.inputs[0:MAX_N_TEST_EXAMPLES],
                assertions=[
                    OrderedDict(
                        {"correct output": AppsAssertion(problem.outputs[i]).evaluate}
                    )
                    for i in range(min(len(problem.outputs), MAX_N_TEST_EXAMPLES))
                ],
            )
        )

    return Benchmark(
        name="APPS",
        tasks=tasks,
        timeout=2
    )
