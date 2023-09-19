import os
import re

from dataclasses import dataclass
from typing import List, Tuple

from gpt_engineer.db import DBs, DB
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


def to_files(chat: str, workspace: DB):
    """
    Parse the chat and add all extracted files to the workspace.

    Parameters
    ----------
    chat : str
        The chat to parse.
    workspace : DB
        The workspace to add the files to.
    """
    workspace["all_output.txt"] = chat  # TODO store this in memory db instead

    files = parse_chat(chat)
    for file_name, file_content in files:
        workspace[file_name] = file_content


def overwrite_files(chat, dbs: DBs):
    """
    Replace the AI files with the older local files.

    Parameters
    ----------
    chat : str
        The chat containing the AI files.
    dbs : DBs
        The database containing the workspace.
    """
    dbs.workspace["all_output.txt"] = chat  # TODO store this in memory db instead

    files = parse_chat(chat)
    for file_name, file_content in files:
        if file_name == "README.md":
            dbs.workspace[
                "LAST_MODIFICATION_README.md"
            ] = file_content  # TODO store this in memory db instead
        else:
            dbs.workspace[file_name] = file_content


def get_code_strings(input: DB) -> dict[str, str]:
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
    files_paths = input[FILE_LIST_NAME].strip().split("\n")
    files_dict = {}
    for full_file_path in files_paths:
        with open(full_file_path, "r") as file:
            file_data = file.read()
        if file_data:
            file_name = os.path.relpath(full_file_path, input.path)
            files_dict[file_name] = file_data
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


def overwrite_files_with_edits(chat, dbs: DBs):
    edits = parse_edits(chat)

    # # # # DEBUG
    print('\nEDITS:\n\n')
    for e in edits:
        print('filename:', e.filename)
        print('before:',e.before)
        print('after:',e.after)
        print('----\n')
    # # # # 

    apply_edits(edits, dbs.workspace)


@dataclass
class Edit:
    filename: str
    before: str
    after: str

def parse_edits(llm_response):
    def parse_one_edit(lines):
        HEAD   = '<<<<<<< HEAD'
        DIVIDER  = '======='
        UPDATE = '>>>>>>> updated'
        
        filename = lines.pop(0)
        text = '\n'.join(lines)
        splits = text.split(DIVIDER)
        if len(splits)!=2: raise ValueError(f"Could not parse following text as code edit: \n{text}")
        before, after = splits

        before = before.replace(HEAD, '').strip()
        after = after.replace(UPDATE, '').strip()
        
        return Edit(filename, before, after)

    def parse_all_edits(txt):
        edits = []
        current_edit = []
        in_fence = False

        for line in txt.split('\n'):
            if line.startswith('```') and in_fence:
                edits.append(parse_one_edit(current_edit))
                current_edit = []
                in_fence = False
                continue
            elif line.startswith('```') and not in_fence:
                in_fence = True        
                continue

            if in_fence: current_edit.append(line)

        return edits

    return parse_all_edits(llm_response)

def apply_edits(edits: List[Edit], workspace: DB):
    for edit in edits:
        filename = edit.filename.replace('workspace/', '')
        if edit.before == '':
            workspace[filename] = edit.after  # new file
        else:
            workspace[filename] = workspace[filename].replace(edit.before, edit.after)  # existing file
