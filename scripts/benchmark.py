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


def main():
    processes = []
    files = []
    benchmarks = Path('benchmark')
    for folder in benchmarks.iterdir():
        if os.path.isdir(folder):
            print('Running benchmark for {}'.format(folder))

            log_path = folder / 'log.txt'
            log_file = open(log_path, 'w')
            processes.append(subprocess.Popen(['python', '-m', 'gpt_engineer.main', folder], stdout=log_file, stderr=log_file))
            files.append(log_file)

            print('You can stream the log file by running: tail -f {}'.format(log_path))

    for process, file in zip(processes, files):
        process.wait()
        print('process finished with code', process.returncode)
        file.close()


if __name__ == '__main__':
    main()
            

