import contextlib
import os
import subprocess

from itertools import islice
from pathlib import Path
from typing import Iterable, Union

from typer import run


def main(
    n_benchmarks: Union[int, None] = None,
):
    path = Path("benchmark")

    folders: Iterable[Path] = path.iterdir()

    if n_benchmarks:
        folders = islice(folders, n_benchmarks)

    benchmarks = []
    for bench_folder in folders:
        if bench_folder.is_dir():
            print(f"Running benchmark for {bench_folder}")

            log_path = bench_folder / "log.txt"
            log_file = open(log_path, "w")
            process = subprocess.Popen(
                [
                    "python",
                    "-u",  # Unbuffered output
                    "-m",
                    "gpt_engineer.main",
                    str(bench_folder),
                    "--steps",
                    "benchmark",
                ],
                stdout=log_file,
                stderr=log_file,
                bufsize=0,
            )
            benchmarks.append((bench_folder, process, log_file))

            print("You can stream the log file by running:")
            print(f"tail -f {log_path}")
            print()
    for bench_folder, process, file in benchmarks:
        process.wait()
        file.close()

        print("process", bench_folder.name, "finished with code", process.returncode)
        print("Running it. Original benchmark prompt:")
        print()
        with open(bench_folder / "prompt") as f:
            print(f.read())
        print()

        port = 8000 + benchmarks.index((bench_folder, process, file))  # Assign unique port for each instance

        with contextlib.suppress(KeyboardInterrupt):
            subprocess.run(
                [
                    "npx",
                    "http-server",
                    "-p",
                    str(port),  # Use unique port for each instance
                ],
                cwd=str(bench_folder),  # Change working directory to project's directory
            )


if __name__ == "__main__":
    run(main)