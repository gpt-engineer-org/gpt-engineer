"""
This module provides functionality to clean up benchmark directories by removing
all files and folders except for 'prompt' and 'main_prompt'.
"""

# list all folders in benchmark folder
# for each folder, run the benchmark

import os
import shutil

from pathlib import Path

from typer import run


def main():
    """
    Main function that iterates through all directories in the 'benchmark' folder
    and cleans them by removing all files and directories except for 'prompt' and
    'main_prompt'.
    """

    benchmarks = Path("benchmark")

    for benchmark in benchmarks.iterdir():
        if benchmark.is_dir():
            print(f"Cleaning {benchmark}")
            for path in benchmark.iterdir():
                if path.name in ["prompt", "main_prompt"]:
                    continue

                # Get filename of Path object
                if path.is_dir():
                    # delete the entire directory
                    shutil.rmtree(path)
                else:
                    # delete the file
                    os.remove(path)


if __name__ == "__main__":
    run(main)
