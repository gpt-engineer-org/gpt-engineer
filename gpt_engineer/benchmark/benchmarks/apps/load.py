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
from typing import Union

from gpt_engineer.benchmark.benchmarks.apps.problem import Problem
from gpt_engineer.benchmark.benchmarks.apps.problems import PROBLEM_IDS
from gpt_engineer.benchmark.types import Benchmark, Task
from gpt_engineer.core.files_dict import FilesDict
from datasets import load_dataset, load_from_disk, Dataset, DatasetDict

DATASET_PATH = "gpt_engineer/benchmark/benchmarks/apps/dataset"


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
        if len(problem.starter_code):  # TODO: Temporary skip; Handle these too
            continue

        command_line_arguments = problem.inputs[0].replace('\n', ' ').strip()

        print(f"python main.py {command_line_arguments}")
        print(f"expected output {problem.outputs[0].replace(' ', '')}")
        tasks.append(
            Task(
                name=str(problem.id),
                initial_code=FilesDict({"main.py": ''}),
                command=f"python main.py {command_line_arguments}",
                prompt=problem.question,
                assertions={
                    "correct output": lambda
                        assertable: problem.outputs[0].replace(' ', '') in assertable.stdout.replace(' ', ''),
                },
                retries=1,  # TODO: Fix other benchmarks
            ),
        )

    return Benchmark(
        name="APPS",
        tasks=tasks
    )
