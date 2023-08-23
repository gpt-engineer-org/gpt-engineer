import os
import subprocess

from pathlib import Path

import yaml

from gpt_engineer.chat_to_files import parse_chat
from gpt_engineer.db import DB

EVAL_LIST_NAME = "evaluations"


# these could be paramaters from one test
SNAKE_EVAL_FOLDER = "projects/snake_game_eval"
SNAKE_GAME_CODE_BLOB = "scripts/snake_game_files.txt"
IMPROVE_CODE_PROMPT = "The grid is currently 10x10, change the grid to be 42x42."


def single_evaluate(eval_ob: dict) -> None:
    """Evaluates a single prompt."""
    print(f"running evaluation: {eval_ob['name']}")

    # Step 1. Setup known project
    # load the known files into the project
    # the filex can be anywhere in the projects folder

    workspace = DB(SNAKE_EVAL_FOLDER)
    file_list_string = ""
    code_base_abs = Path(os.getcwd()) / SNAKE_EVAL_FOLDER

    files = parse_chat(open(SNAKE_GAME_CODE_BLOB).read())
    for file_name, file_content in files:
        absolute_path = code_base_abs / file_name
        print("creating: ", absolute_path)
        workspace[absolute_path] = file_content
        file_list_string += str(absolute_path) + "\n"

    # create file_list.txt (should be full paths)
    workspace["file_list.txt"] = file_list_string

    # create the prompt
    workspace["prompt"] = IMPROVE_CODE_PROMPT

    # Step 2.  run the project in improve code mode,
    # make sure the flag -sf is set to skip feedback

    print(f"Running benchmark for {SNAKE_EVAL_FOLDER}")

    log_path = code_base_abs / "log.txt"
    log_file = open(log_path, "w")
    process = subprocess.Popen(
        [
            "python",
            "-u",  # Unbuffered output
            "-m",
            "gpt_engineer.main",
            SNAKE_EVAL_FOLDER,
            "--steps",
            "eval_improve_code",
        ],
        stdout=log_file,
        stderr=log_file,
        bufsize=0,
    )
    print(f"waiting for {eval_ob['name']} to finish.")
    process.wait()
    # we want to wait until it finishes.

    # TODO: check the code was properly changed.
    # in grid.py check the code now looks like:
    # def __init__(self, width=42, height=42):  # Updated grid size


def load_evaluations_from_file(file_path):
    """Loads the evaluations from a YAML file."""
    try:
        with open(file_path, "r") as file:
            data = yaml.safe_load(file)
            if EVAL_LIST_NAME in data:
                return data[EVAL_LIST_NAME]
            else:
                print(f"'{EVAL_LIST_NAME}' not found in {file_path}")
    except FileNotFoundError:
        print(f"File not found: {file_path}")


def run_all_evaluations(eval_list: list[dict]) -> None:
    for eval_ob in eval_list:
        single_evaluate(eval_ob)

    # TODO: roll up evaluations into report


if __name__ == "__main__":
    eval_list = load_evaluations_from_file("scripts/existing_code_eval.yaml")
    run_all_evaluations(eval_list)
