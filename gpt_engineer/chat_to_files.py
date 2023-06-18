import re
from typing import List, Tuple
from gpt_engineer.db import DB


def parse_chat(chat) -> List[Tuple[str, str]]:
    # Get all ``` blocks
    regex = r"```(.*?)```"

    matches = re.finditer(regex, chat, re.DOTALL)

    files = []
    for match in matches:
        path = match.group(1).split("\n")[0]
        # Get the code
        code = match.group(1).split("\n")[1:]
        code = "\n".join(code)
        # Add the file to the list
        files.append((path, code))

    return files


def to_files(chat: str, workspace: DB):
    workspace["all_output.txt"] = chat

    files = parse_chat(chat)
    for file_name, file_content in files:
        workspace[file_name] = file_content
