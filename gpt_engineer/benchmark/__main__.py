"""
Main entry point for the benchmarking tool.

This module provides a command-line interface for running benchmarks using Typer.
It allows users to specify the path to an agent, the benchmark(s) to run, and other
options such as verbosity.

Functions:
    get_agent(path: str) -> BaseAgent:
        Dynamically imports and returns the default configuration agent from the given path.

    main(path_to_agent: str, benchmarks: str, task_name: Optional[str], verbose: bool) -> None:
        The main function that runs the specified benchmarks with the given agent.
        Outputs the results to the console.

    if __name__ == "__main__":
        The standard boilerplate for invoking the main function when the script is executed.
"""
import importlib

from typing import Annotated, Optional

import typer

from langchain.cache import SQLiteCache
from langchain.globals import set_llm_cache

from gpt_engineer.benchmark.benchmarks.load import get_benchmark
from gpt_engineer.benchmark.run import print_results, run


def get_agent(path):
    # Dynamically import the python module at path
    agent_module = importlib.import_module(path.replace("/", ".").replace(".py", ""))
    return agent_module.default_config_agent()


def main(
    path_to_agent: Annotated[
        str,
        typer.Argument(
            help="python file that contains a function called 'default_config_agent'"
        ),
    ],
    benchmarks: Annotated[
        str, typer.Argument(help="benchmark name(s) separated by ','")
    ],
    task_name: Annotated[
        Optional[str], typer.Argument(help="optional task name in benchmark")
    ] = None,
    verbose: Annotated[
        bool, typer.Option(help="print results for each task", show_default=False)
    ] = False,
):
    set_llm_cache(SQLiteCache(database_path=".langchain.db"))

    benchmarks = benchmarks.split(",")
    for benchmark_name in benchmarks:
        benchmark = get_benchmark(benchmark_name)
        agent = get_agent(path_to_agent)

        results = run(agent, benchmark, task_name, verbose=verbose)
        print(
            f"\n--- Results for agent {path_to_agent}, benchmark: {benchmark_name} ---"
        )
        print_results(results)
        print()


if __name__ == "__main__":
    typer.run(main)
