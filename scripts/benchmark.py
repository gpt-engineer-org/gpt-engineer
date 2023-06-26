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
    port = 8000
    benchmarks = []
    for bench_folder in folders:
        if os.path.isdir(bench_folder):
            print(f"Running benchmark for {bench_folder}")

            log_path = bench_folder / "log.txt"
            log_file = open(log_path, "w")
            process = subprocess.Popen(
                [
                    "npx",
                    "http-server",
                    "-p",
                    str(port),
                    bench_folder
                ],
                stdout=log_file,
                stderr=log_file,
                bufsize=0,
            )
            port += 1
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

        with contextlib.suppress(KeyboardInterrupt):
            subprocess.run(
                [
                    "python",
                    "-m",
                    "gpt_engineer.main",
                    bench_folder,
                    "--steps",
                    "evaluate",
                ],
            )


if __name__ == "__main__":
    run(main)