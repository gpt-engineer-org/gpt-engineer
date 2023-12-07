"""
This module provides utilities to handle and process chat content, especially for extracting code blocks
and managing them within a specified GPT Engineer project ("workspace"). It offers functionalities like parsing chat messages to
retrieve code blocks, storing these blocks into a workspace, and overwriting workspace content based on
new chat messages. Moreover, it aids in formatting and reading file content for an AI agent's input.

Key Features:
- Parse and extract code blocks from chat messages.
- Store and overwrite files within a workspace based on chat content.
- Format files to be used as inputs for AI agents.
- Retrieve files and their content based on a provided list.

Dependencies:
- `os` and `pathlib`: For handling OS-level operations and path manipulations.
- `re`: For regex-based parsing of chat content.
- `gpt_engineer.core.db`: Database handling functionalities for the workspace.
- `gpt_engineer.cli.file_selector`: Constants related to file selection.

Functions:
- parse_chat: Extracts code blocks from chat messages.
- to_files_and_memory: Saves chat content to memory and adds extracted files to a workspace.
- to_files: Adds extracted files to a workspace.
- get_code_strings: Retrieves file names and their content.
- format_file_to_input: Formats file content for AI input.
- overwrite_files_with_edits: Overwrites workspace files based on parsed edits from chat.
- apply_edits: Applies file edits to a workspace.
"""

import re
import logging

from dataclasses import dataclass
from typing import List, Tuple

from gpt_engineer.core.files_dict import FilesDict

logger = logging.getLogger(__name__)


def chat_to_files_dict(chat) -> FilesDict:
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

    files_dict = FilesDict()
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
        content = match.group(2)

        # Add the file to the list
        files_dict[path.strip()] = content.strip()

    return FilesDict(files_dict)


def overwrite_code_with_edits(chat: str, files_dict: FilesDict):
    """
    Overwrite code with edits extracted from chat.

    This function takes a chat string, parses it for edits, and applies those edits
    to the provided code object.

    Parameters
    ----------
    chat : str
        The chat content containing code edits.
    files_dict : FilesDict
        The code object to apply edits to.
    """
    edits = parse_edits(chat)
    apply_edits(edits, files_dict)


@dataclass
class Edit:
    filename: str
    before: str
    after: str


def parse_edits(chat: str):
    """
    Parse edits from a chat string.

    This function extracts code edits from a chat string and returns them as a list
    of Edit objects.

    Parameters
    ----------
    chat : str
        The chat content containing code edits.

    Returns
    -------
    List[Edit]
        A list of Edit objects representing the parsed code edits.
    """

    def parse_one_edit(lines):
        HEAD = "<<<<<<< HEAD"
        DIVIDER = "\n=======\n"
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

    edits = []
    current_edit = []
    in_fence = False

    for line in chat.split("\n"):
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


def apply_edits(edits: List[Edit], files_dict: FilesDict):
    """
    Apply a list of edits to the given code.

    This function takes a list of Edit objects and applies each edit to the code object.
    It handles the creation of new files and the modification of existing files based on the edits.

    Parameters
    ----------
    edits : List[Edit]
        A list of Edit objects representing the code edits to apply.
    files_dict : FilesDict
        The code object to apply edits to.
    """
    for edit in edits:
        filename = edit.filename
        if edit.before == "":
            if filename in files_dict:
                logger.warning(
                    f"The edit to be applied wants to create a new file `{filename}`, but that already exists. The file will be overwritten. See `.gpteng/memory` for previous version."
                )
            files_dict[filename] = edit.after  # new file
        else:
            occurrences_cnt = files_dict[filename].count(edit.before)
            if occurrences_cnt == 0:
                logger.warning(
                    f"While applying an edit to `{filename}`, the code block to be replaced was not found. No instances will be replaced."
                )
            if occurrences_cnt > 1:
                logger.warning(
                    f"While applying an edit to `{filename}`, the code block to be replaced was found multiple times. All instances will be replaced."
                )
            files_dict[filename] = files_dict[filename].replace(
                edit.before, edit.after
            )  # existing file
