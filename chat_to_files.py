from ast import List, Tuple
import os
import re


def parse_chat(chat):# -> List[Tuple[str, str]]:
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


def to_files(chat, path):
    os.makedirs(path, exist_ok=True)

    with open(os.path.join(path, 'all_output.txt'), "w") as f:
        f.write(chat)

    files = parse_chat(chat)
    for file_name, file_content in files:
        with open(os.path.join(path, file_name), "w") as f:
            f.write(file_content)