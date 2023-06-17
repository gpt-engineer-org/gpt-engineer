# list all folders in benchmark folder
# for each folder, run the benchmark

import os
import sys
import subprocess
import time
import datetime
import shutil
import argparse
import json
from pathlib import Path
from typer import run
from itertools import islice

def main(
    n_benchmarks: int | None = None,
):
    processes = []
    files = []
    path = Path('benchmark')

    if n_benchmarks:
        benchmarks = islice(path.iterdir(), n_benchmarks)

    for folder in benchmarks:
        if os.path.isdir(folder):
            print('Running benchmark for {}'.format(folder))

            log_path = folder / 'log.txt'
            log_file = open(log_path, 'w')
            processes.append(subprocess.Popen(['python', '-m', 'gpt_engineer.main', folder], stdout=log_file, stderr=log_file, bufsize=0))
            files.append(log_file)

            print('You can stream the log file by running: tail -f {}'.format(log_path))

    for process, file in zip(processes, files):
        process.wait()
        print('process finished with code', process.returncode)
        file.close()


if __name__ == '__main__':
    run(main)
            

