
import os
from pathlib import Path
import subprocess

from gpt_engineer.chat_to_files import parse_chat
from gpt_engineer.db import DB


# these could be paramaters from one test
SNAKE_EVAL_FOLDER = "projects/snake_game_eval"
SNAKE_GAME_CODE_BLOB = "scripts/snake_game_files.txt"
IMPROVE_CODE_PROMPT = "The grid is currently 10x10, change the grid to be 42x42."

def single_evaluate():
    """Evaluates a single prompt."""
    
    # Step 1. Setup known project
    # load the known files into the project
    # the filex can be anywhere in the projects folder

    workspace=DB(SNAKE_EVAL_FOLDER)
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
   
    # TODO: check the code was properly changed.  


if __name__ == "__main__":
    single_evaluate()