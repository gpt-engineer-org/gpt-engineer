from gpt_engineer.benchmark.types import Benchmark

BENCHMARKS = {
    "default": load_gpte_eval,
}


def get_benchmark(name: str) -> Benchmark:
    if name not in BENCHMARKS:
        raise ValueError(f"Unknown benchmark {name}.")
    return BENCHMARKS[name]()
