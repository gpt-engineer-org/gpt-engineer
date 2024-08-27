import importlib
import os.path
import sys

from typing import Annotated, Optional

import typer

from langchain.globals import set_llm_cache
from langchain_community.cache import SQLiteCache
from gpt_engineer.applications.cli.main import load_env_if_needed
from gpt_engineer.benchmark.bench_config import BenchConfig
from gpt_engineer.benchmark.benchmarks.load import get_benchmark
from gpt_engineer.benchmark.run import export_yaml_results, print_results, run
from gpt_engineer.ai_features import AIAnalyzer, DynamicConfigLoader, EnhancedErrorHandling

app = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]}
)  # creates a CLI app


def get_agent(path):
    """
    Dynamically imports and returns the default configuration agent from the given path.

    Parameters
    ----------
    path : str
        The file path to the module containing the default configuration agent.

    Returns
    -------
    BaseAgent
        An instance of the imported default configuration agent.
    """
    sys.path.append(os.path.dirname(path))
    agent_module = importlib.import_module(path.replace("/", ".").replace(".py", ""))
    return agent_module.default_config_agent()


@app.command(
    help="""
        Run any benchmark(s) against the specified agent.

        \b
        Currently available benchmarks are: apps and mbpp
    """
)
def main(
    path_to_agent: Annotated[
        str,
        typer.Argument(
            help="python file that contains a function called 'default_config_agent'"
        ),
    ],
    bench_config: Annotated[
        str, typer.Argument(help="optional task name in benchmark")
    ] = os.path.join(os.path.dirname(__file__), "default_bench_config.toml"),
    yaml_output: Annotated[
        Optional[str],
        typer.Option(help="print results for each task", show_default=False),
    ] = None,
    verbose: Annotated[
        Optional[bool],
        typer.Option(help="print results for each task", show_default=False),
    ] = False,
    use_cache: Annotated[
        Optional[bool],
        typer.Option(
            help="Speeds up computations and saves tokens when running the same prompt multiple times by caching the LLM response.",
            show_default=False,
        ),
    ] = True,
    enable_ai_features: Annotated[
        Optional[bool],
        typer.Option(
            help="Enables advanced AI-driven features like dynamic configuration and enhanced error analysis.",
            show_default=True,
        ),
    ] = False,
):
    """
    The main function that runs the specified benchmarks with the given agent and outputs the results to the console.

    Parameters
    ----------
    path_to_agent : str
        The file path to the Python module that contains a function called 'default_config_agent'.
    bench_config : str, default=default_bench_config.toml
        Configuration file for choosing which benchmark problems to run. See default config for more details.
    yaml_output: Optional[str], default=None
        Pass a path to a yaml file to have results written to file.
    verbose : Optional[bool], default=False
        A flag to indicate whether to print results for each task.
    use_cache : Optional[bool], default=True
        Speeds up computations and saves tokens when running the same prompt multiple times by caching the LLM response.
    enable_ai_features: Optional[bool], default=False
        Enables advanced AI-driven features like dynamic configuration and enhanced error analysis.
    Returns
    -------
    None
    """
    if use_cache:
        set_llm_cache(SQLiteCache(database_path=".langchain.db"))
    
    if enable_ai_features:
        # Apply AI-driven dynamic configuration loading
        bench_config = DynamicConfigLoader.load(bench_config)
        # AI-enhanced error handling
        EnhancedErrorHandling.activate()

    load_env_if_needed()
    config = BenchConfig.from_toml(bench_config)
    print("using config file: " + bench_config)
    
    benchmarks = list()
    benchmark_results = dict()
    for specific_config_name in vars(config):
        specific_config = getattr(config, specific_config_name)
        if hasattr(specific_config, "active") and specific_config.active:
            benchmarks.append(specific_config_name)

    for benchmark_name in benchmarks:
        benchmark = get_benchmark(benchmark_name, config)
        if len(benchmark.tasks) == 0:
            print(
                benchmark_name
                + " was skipped, since no tasks are specified. Increase the number of tasks in the config file at: "
                + bench_config
            )
            continue
        agent = get_agent(path_to_agent)

        results = run(agent, benchmark, verbose=verbose)
        if enable_ai_features:
            AIAnalyzer.analyze_results(results)  # AI-driven results analysis

        print(
            f"\n--- Results for agent {path_to_agent}, benchmark: {benchmark_name} ---"
        )
        print_results(results)
        print()
        benchmark_results[benchmark_name] = {
            "detailed": [result.to_dict() for result in results]
        }
    if yaml_output is not None:
        export_yaml_results(yaml_output, benchmark_results, config.to_dict())


if __name__ == "__main__":
    typer.run(main)
