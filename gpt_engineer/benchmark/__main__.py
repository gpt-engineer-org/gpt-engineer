import importlib
from typing import Optional, Annotated
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
    benchmarks: Annotated[str, typer.Argument(help="benchmark name(s) separated by ','")],
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
        print(f"\n--- Results for agent {path_to_agent}, benchmark: {benchmark_name} ---")
        print_results(results)
        print()


if __name__ == "__main__":
    typer.run(main)
