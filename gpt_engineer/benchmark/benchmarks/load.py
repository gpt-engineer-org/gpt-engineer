from gpt_engineer.benchmark.benchmarks.gpteng.load import load_gpteng
from gpt_engineer.benchmark.benchmarks.gptme.load import load_gptme
from gpt_engineer.benchmark.types import Benchmark

BENCHMARKS = {
    "gptme": load_gptme,
    "gpteng": load_gpteng,
}


def get_benchmark(name: str) -> Benchmark:
    if name not in BENCHMARKS:
        raise ValueError(f"Unknown benchmark {name}.")
    return BENCHMARKS[name]()
