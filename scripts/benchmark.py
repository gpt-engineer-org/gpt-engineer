import logging
import os
from pathlib import Path

from gpt_engineer.main import main as gpt_main
from typer import run

logging.basicConfig(filename='benchmark.log', level=logging.INFO)


def run_benchmark(bench_folder, steps):
    try:
        gpt_main(bench_folder, steps)
    except Exception as e:
        logging.error(f"Error running benchmark for {bench_folder}: {e}")


def main(n_benchmarks: int = None):
    path = Path("benchmark")
    folders = path.iterdir()

    if n_benchmarks:
        folders = list(folders)[:n_benchmarks]

    for bench_folder in folders:
        if bench_folder.is_dir():
            logging.info(f"Running benchmark for {bench_folder}")
            run_benchmark(bench_folder, "benchmark")

            logging.info("You can stream the log file by running:")
            logging.info(f"tail -f benchmark.log")
            logging.info()

            logging.info("process", bench_folder.name, "finished with code")
            logging.info("Running it. Original benchmark prompt:")
            logging.info()
            with open(bench_folder / "prompt") as f:
                logging.info(f.read())
            logging.info()

            run_benchmark(bench_folder, "execute_only")


if __name__ == "__main__":
    run(main)