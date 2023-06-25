import contextlib
import os
import subprocess

from itertools import islice
from pathlib import Path
from typing import Iterable, Union

from typer import run

from gpt_engineer.main import main as gpt_main


def main(n_benchmarks: Union[int, None] = None):
    path = Path("benchmark")
    folders: Iterable[Path] = path.iterdir()

    if n_benchmarks:
        folders = islice(folders, n_benchmarks)

    benchmarks = []
    for bench_folder in folders:
        if os.path.isdir(bench_folder):
            print(f"Running benchmark for {bench_folder}")

            log_path = bench_folder / "log.txt"
            log_file = open(log_path, "w")
            gpt_main(bench_folder, "--steps", "benchmark")
            benchmarks.append((bench_folder, log_file))

            print("You can stream the log file by running:")
            print(f"tail -f {log_path}")
            print()

    for bench_folder, file in benchmarks:
        file.close()

        print("process", bench_folder.name, "finished")
        print("Running it. Original benchmark prompt:")
        print()
        with open(bench_folder / "prompt") as f:
            print(f.read())
        print()

        with contextlib.suppress(KeyboardInterrupt):
            gpt_main(bench_folder, "--steps", "execute_only")


if __name__ == "__main__":
    run(main)