import re

from gpt_engineer.db import DB


def parse_chat(chat):  # -> List[Tuple[str, str]]:
    # Get all ``` blocks and preceding filenames
    regex = r"(\S+?)\n```\S+\n(.+?)```"
    matches = re.finditer(regex, chat, re.DOTALL)

    files = []
    for match in matches:
        # Strip the filename of any non-allowed characters and convert / to \
        path = re.sub(r'[<>"|?*]', "", match.group(1))

        # Get the code
        code = match.group(2)

        # Add the file to the list
        files.append((path, code))

    # Get all the text before the first ``` block
    readme = chat.split("```")[0]
    files.append(("README.md", readme))

    # Return the files
    return files


def to_files(chat, workspace: DB):
    workspace["all_output.txt"] = chat

    files = parse_chat(chat)
    for file_name, file_content in files:
        workspace[file_name] = file_content
