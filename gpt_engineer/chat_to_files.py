import os
from pathlib import Path
import re

from dataclasses import dataclass
from typing import List, Tuple

from gpt_engineer.db import DB, DBs
from gpt_engineer.file_selector import FILE_LIST_NAME


def parse_chat(chat) -> List[Tuple[str, str]]:
    """
    Extracts all code blocks from a chat and returns them
    as a list of (filename, codeblock) tuples.

    Parameters
    ----------
    chat : str
        The chat to extract code blocks from.

    Returns
    -------
    List[Tuple[str, str]]
        A list of tuples, where each tuple contains a filename and a code block.
    """
    # Get all ``` blocks and preceding filenames
    regex = r"(\S+)\n\s*```[^\n]*\n(.+?)```"
    matches = re.finditer(regex, chat, re.DOTALL)

    files = []
    for match in matches:
        # Strip the filename of any non-allowed characters and convert / to \
        path = re.sub(r'[\:<>"|?*]', "", match.group(1))

        # Remove leading and trailing brackets
        path = re.sub(r"^\[(.*)\]$", r"\1", path)

        # Remove leading and trailing backticks
        path = re.sub(r"^`(.*)`$", r"\1", path)

        # Remove trailing ]
        path = re.sub(r"[\]\:]$", "", path)

        # Get the code
        code = match.group(2)

        # Add the file to the list
        files.append((path, code))

    # Get all the text before the first ``` block
    readme = chat.split("```")[0]
    files.append(("README.md", readme))

    # Return the files
    return files


def to_files(chat: str, dbs: DBs):
    """
    Parse the chat and add all extracted files to the workspace.

    Parameters
    ----------
    chat : str
        The chat to parse.
    workspace : DB
        The database containing the workspace.
    """
    dbs.memory["all_output.txt"] = chat

    files = parse_chat(chat)
    for file_name, file_content in files:
        dbs.workspace[file_name] = file_content


def overwrite_files(chat: str, dbs: DBs) -> None:
    """
    Parse the chat and overwrite all files in the workspace.

    Parameters
    ----------
    chat : str
        The chat containing the AI files.
    dbs : DBs
        The database containing the workspace.
    """
    dbs.memory["all_output_overwrite.txt"] = chat

    files = parse_chat(chat)
    for file_name, file_content in files:
        if file_name == "README.md":
            dbs.memory["LAST_MODIFICATION_README.md"] = file_content
        else:
            dbs.workspace[file_name] = file_content


def get_code_strings(workspace: DB, metadata_db: DB) -> dict[str, str]:
    """
    Read file_list.txt and return file names and their content.

    Parameters
    ----------
    input : dict
        A dictionary containing the file_list.txt.

    Returns
    -------
    dict[str, str]
        A dictionary mapping file names to their content.
    """

    def get_all_files_in_dir(directory):
        for root, dirs, files in os.walk(directory):
            for file in files:
                yield os.path.join(root, file)
        for dir in dirs:
            yield from get_all_files_in_dir(os.path.join(root, dir))

    files_paths = metadata_db[FILE_LIST_NAME].strip().split("\n")
    files = []

    for full_file_path in files_paths:
        if os.path.isdir(full_file_path):
            for file_path in get_all_files_in_dir(full_file_path):
                files.append(file_path)
        else:
            files.append(full_file_path)

    files_dict = {}
    for path in files:
        assert os.path.commonpath([full_file_path, workspace.path]) == str(
            workspace.path
        ), "Trying to edit files outside of the workspace"
        file_name = os.path.relpath(path, workspace.path)
        if file_name in workspace:
            files_dict[file_name] = workspace[file_name]
    return files_dict


def format_file_to_input(file_name: str, file_content: str) -> str:
    """
    Format a file string to use as input to the AI agent.

    Parameters
    ----------
    file_name : str
        The name of the file.
    file_content : str
        The content of the file.

    Returns
    -------
    str
        The formatted file string.
    """
    file_str = f"""
    {file_name}
    ```
    {file_content}
    ```
    """
    return file_str


def overwrite_files_with_edits(chat: str, dbs: DBs):
    edits = parse_edits(chat)
    apply_edits(edits, dbs.workspace)


@dataclass
class Edit:
    filename: str
    before: str
    after: str


def parse_edits(llm_response):
    def parse_one_edit(lines):
        HEAD = "<<<<<<< HEAD"
        DIVIDER = "======="
        UPDATE = ">>>>>>> updated"

        filename = lines.pop(0)
        text = "\n".join(lines)
        splits = text.split(DIVIDER)
        if len(splits) != 2:
            raise ValueError(f"Could not parse following text as code edit: \n{text}")
        before, after = splits

        before = before.replace(HEAD, "").strip()
        after = after.replace(UPDATE, "").strip()

        return Edit(filename, before, after)

    def parse_all_edits(txt):
        edits = []
        current_edit = []
        in_fence = False

        for line in txt.split("\n"):
            if line.startswith("```") and in_fence:
                edits.append(parse_one_edit(current_edit))
                current_edit = []
                in_fence = False
                continue
            elif line.startswith("```") and not in_fence:
                in_fence = True
                continue

            if in_fence:
                current_edit.append(line)

        return edits

    return parse_all_edits(llm_response)


def apply_edits(edits: List[Edit], workspace: DB):
    for edit in edits:
        filename = edit.filename.replace("workspace/", "")
        if edit.before == "":
            workspace[filename] = edit.after  # new file
        else:
            workspace[filename] = workspace[filename].replace(
                edit.before, edit.after
            )  # existing file
