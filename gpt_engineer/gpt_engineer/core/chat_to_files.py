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


from gpt_engineer.core.code import Code

logger = logging.getLogger(__name__)


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

        # strip blanks etc
        code = code.strip()

        # Add the file to the list
        files.append((path, code))

    # Get all the text before the first ``` block
    # readme = chat.split("```")[0]
    # files.append(("README.md", readme))

    # Return the files
    return files


def overwrite_code_with_edits(chat: str, code: Code):
    """
    Overwrites the code with edits extracted from the chat.

    This function parses the chat to identify code edits and then applies those edits
    to the provided code object.

    Parameters
    ----------
    chat : str
        The chat content containing code edits.
    code : Code
        The code object to apply the edits to.
    """
    edits = parse_edits(chat)
    apply_edits(edits, code)


@dataclass
class Edit:
    filename: str
    before: str
    after: str


def parse_edits(chat: str):
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


def apply_edits(edits: List[Edit], code: Code):
    for edit in edits:
        filename = edit.filename
        if edit.before == "":
            if filename in code:
                logger.warning(
                    f"The edit to be applied wants to create a new file `{filename}`, but that already exists. The file will be overwritten. See `.gpteng/memory` for previous version."
                )
            code[filename] = edit.after  # new file
        else:
            occurrences_cnt = code[filename].count(edit.before)
            if occurrences_cnt == 0:
                logger.warning(
                    f"While applying an edit to `{filename}`, the code block to be replaced was not found. No instances will be replaced."
                )
            if occurrences_cnt > 1:
                logger.warning(
                    f"While applying an edit to `{filename}`, the code block to be replaced was found multiple times. All instances will be replaced."
                )
            code[filename] = code[filename].replace(
                edit.before, edit.after
            )  # existing file
