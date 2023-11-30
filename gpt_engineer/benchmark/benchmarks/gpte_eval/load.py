from gpt_engineer.benchmark.benchmarks.default.eval_tools import (
    load_evaluations_from_file,
)
from gpt_engineer.benchmark.types import Benchmark


def load_gpte_eval():
    evals = load_evaluations_from_file("new_code_eval.yaml")
    evals = load_evaluations_from_file("existing_code_eval.yaml")

    return Benchmark(
        "gpte_eval",
    )
