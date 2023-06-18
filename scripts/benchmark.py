# list all folders in benchmark folder
# for each folder, run the benchmark

import os
import subprocess

from itertools import islice
from pathlib import Path

from typer import run


def main(
    n_benchmarks: int | None = None,
):
    path = Path("benchmark")

    folders = path.iterdir()

    if n_benchmarks:
        folders = islice(folders, n_benchmarks)

    benchmarks = []
    for bench_folder in folders:
        if os.path.isdir(bench_folder):
            print("Running benchmark for {}".format(bench_folder))

            log_path = bench_folder / "log.txt"
            log_file = open(log_path, "w")
            process = subprocess.Popen(
                [
                    "python",
                    "-u",  # Unbuffered output
                    "-m",
                    "gpt_engineer.main",
                    bench_folder,
                    "--steps-config",
                    "benchmark",
                ],
                stdout=log_file,
                stderr=log_file,
                bufsize=0,
            )
            benchmarks.append((bench_folder, process, log_file))

            print("You can stream the log file by running:")
            print("tail -f {}".format(log_path))
            print()

    for bench_folder, process, file in benchmarks:
        process.wait()
        file.close()

        print("process", bench_folder.name, "finished with code", process.returncode)
        print("Running it. Original benchmark prompt:")
        print()
        with open(bench_folder / "main_prompt") as f:
            print(f.read())
        print()

        try:
            subprocess.run(
                [
                    "python",
                    "-m",
                    "gpt_engineer.main",
                    bench_folder,
                    "--steps-config",
                    "execute_only",
                ],
            )
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    run(main)
