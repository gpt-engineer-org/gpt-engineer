"""
Module for loading gptengineer.app evaluation tasks.

This module provides functionality to load tasks for evaluating GPT-based models
on smaller, more focused tasks. It defines a set of tasks with predefined prompts
and assertions to benchmark the performance of AI models.

Functions
---------
load : function
    Loads the benchmark, which consists of a series of tasks for evaluation.
"""

from gpt_engineer.benchmark.types import Benchmark, Task

from .template import create_template


def load():
    """
    Loads the benchmark, which consists of a series of tasks for evaluation.

    Returns
    -------
    Benchmark
        A Benchmark object containing a list of Task objects for the evaluation.
    """
    return Benchmark(
        name="gptengineer.app",
        tasks=[
            Task(
                name="create todo app",
                initial_code=create_template(),
                command="true",
                prompt="Implement a todo app",
                assertions={
                    # TODO: Add assertions
                    #       But which? Vision? Linter? JS errors at runtime?
                },
            ),
        ],
    )
