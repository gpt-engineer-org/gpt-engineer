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
):
    benchmarks = Path('benchmark')

    for benchmark in benchmarks.iterdir():
        if benchmark.is_dir():
            print(f'Cleaning {benchmark}')
            for path in benchmark.iterdir():
                if path.name == 'main_prompt':
                    continue

                # Get filename of Path object
                if path.is_dir():
                    # delete the entire directory
                    shutil.rmtree(path)
                else:
                    # delete the file
                    os.remove(path)

if __name__ == '__main__':
    run(main)
            

