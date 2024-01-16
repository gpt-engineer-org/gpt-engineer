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

import logging
import re

from dataclasses import dataclass
from typing import List

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
    line_number: int
    content: str
    is_before: bool


def parse_edits(chat: str):
    """
    Parse edits from a chat string, preserving indentation.
    """
    edits = []
    lines = chat.split("\n")
    filename = ""
    for line in lines:
        if line.startswith("File:"):
            filename = line.split(":")[1].strip()
        else:
            # Modified regex to capture leading spaces (indentation)
            match = re.match(r"(\d+) ([-+]) (.*\S.*)", line)
            if match:
                line_number, symbol, content = match.groups()
                line_number = int(line_number)
                is_before = symbol == "-"
                edits.append(Edit(filename, line_number, content, is_before))

    # Sort edits such that 'before' edits come before 'after' edits
    edits.sort(key=lambda edit: (edit.filename, edit.line_number, not edit.is_before))
    return edits


def apply_edits(edits: List[Edit], files_dict: FilesDict):
    # Step 1: Sort edits by original line number
    edits.sort(key=lambda edit: edit.line_number)

    # Step 2: Apply edits while tracking line number shifts with a standard dictionary
    line_shifts = {}  # Standard dictionary to track line number shifts
    for edit in edits:
        filename = edit.filename
        original_line_index = edit.line_number - 1
        adjusted_line_index = original_line_index + line_shifts.get(filename, 0)

        lines = files_dict[filename].split("\n")
        if adjusted_line_index < len(lines):
            # Modify existing line
            lines[adjusted_line_index] = edit.content
            print(
                f"Modified line {adjusted_line_index + 1} in {filename}: '{edit.content}'"
            )
        else:
            # Append new line
            lines.append(edit.content)
            print(
                f"Added line {adjusted_line_index + 1} in {filename}: '{edit.content}'"
            )
            line_shifts[filename] = (
                line_shifts.get(filename, 0) + 1
            )  # Update line shift for this file

        files_dict[filename] = "\n".join(lines)
