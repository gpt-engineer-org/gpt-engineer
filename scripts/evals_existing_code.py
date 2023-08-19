import os

from pathlib import Path

from gpt_engineer.chat_to_files import parse_chat
from gpt_engineer.db import DB

# these could be paramaters from one test
SNAKE_EVAL_FOLDER = "projects/snake_game_eval"
SNAKE_GAME_CODE_BLOB = "scripts/snake_game_files.txt"


def single_evaluate():
    """Evaluates a single prompt."""

    # load the known files into the project
    # the filex can be anywhere in the projects folder

    workspace = DB(SNAKE_EVAL_FOLDER)
    file_list_string = ""
    code_base_abs = Path(os.getcwd()) / SNAKE_EVAL_FOLDER
    print(code_base_abs)

    files = parse_chat(open(SNAKE_GAME_CODE_BLOB).read())
    for file_name, file_content in files:
        absolute_path = code_base_abs / file_name
        print("absolute_path: ", absolute_path)
        workspace[absolute_path] = file_content
        file_list_string += str(absolute_path) + "\n"

    # create file_list.txt (should be full paths)
    workspace["file_list.txt"] = file_list_string

    # run the project in improve code mode
    return


if __name__ == "__main__":
    single_evaluate()
