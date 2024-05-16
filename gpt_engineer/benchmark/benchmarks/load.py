"""
Module for loading benchmarks.

This module provides a central point to access different benchmarks by name.
It maps benchmark names to their respective loading functions.

Functions
---------
get_benchmark : function
    Retrieves a Benchmark object by name. Raises ValueError if the benchmark is unknown.
"""
from gpt_engineer.benchmark.bench_config import BenchConfig
from gpt_engineer.benchmark.benchmarks.apps.load import load_apps
from gpt_engineer.benchmark.benchmarks.gptme.load import load_gptme
from gpt_engineer.benchmark.benchmarks.mbpp.load import load_mbpp
from gpt_engineer.benchmark.types import Benchmark

BENCHMARKS = {
    "gptme": load_gptme,
    "apps": load_apps,
    "mbpp": load_mbpp,
}


def get_benchmark(name: str, config: BenchConfig) -> Benchmark:
    """
    Retrieves a Benchmark object by name. Raises ValueError if the benchmark is unknown.

    Parameters
    ----------
    name : str
        The name of the benchmark to retrieve.
    config : BenchConfig
        Configuration object for the benchmarks.

    Returns
    -------
    Benchmark
        The Benchmark object corresponding to the given name.

    Raises
    ------
    ValueError
        If the benchmark name is not found in the BENCHMARKS mapping.
    """
    if name not in BENCHMARKS:
        raise ValueError(f"Unknown benchmark {name}.")
    return BENCHMARKS[name](config.__getattribute__(name))
