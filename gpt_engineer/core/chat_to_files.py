"""
This module provides advanced utilities for processing and managing chat content,
specifically in GPT Engineer projects ("workspaces"). Its main focus is on the extraction
and manipulation of code blocks from chat messages. Key functionalities include parsing chat
content to identify and extract code blocks, then integrating them into workspaces.

Key Features:
- Efficient extraction of code blocks from chat messages for workspace integration.
- Dynamic updating of workspace files with new chat content.
- Automated formatting of files for AI agent processing.
- Retrieval of specific files and content for detailed analysis.

Dependencies:
- `os` and `pathlib`: Handle file system operations and path manipulations.
- `re`: Employed for regex-based parsing to extract code blocks and edits.
- `gpt_engineer.core.db`: Database functionalities for workspace management.
- `gpt_engineer.cli.file_selector`: Constants and utilities for file selection.

Core Functions:
- chat_to_files_dict: Extracts code blocks and organizes them for access.
- overwrite_code_with_edits: Updates workspace files with chat-derived edits.
- parse_edits: Parses and structures code edits from chats.
- apply_edits: Applies edits to workspace files, maintaining their relevance.
"""


import logging
import re

from collections import Counter
from dataclasses import dataclass
from typing import List

from gpt_engineer.core.files_dict import FilesDict

# Configure logging for the module
logger = logging.getLogger(__name__)


def chat_to_files_dict(chat) -> FilesDict:
    """
    Extracts code blocks from a chat string and returns a FilesDict object containing
    (filename, codeblock) pairs.

    Parameters
    ----------
    chat : str
        The chat string to extract code blocks from.

    Returns
    -------
    FilesDict
        A FilesDict object with filenames as keys and their respective code blocks as values.
    """
    # Regular expression pattern to identify code blocks and preceding filenames
    regex = r"(\S+)\n\s*```[^\n]*\n(.+?)```"
    matches = re.finditer(regex, chat, re.DOTALL)

    files_dict = FilesDict()
    for match in matches:
        # Clean and standardize the file path
        path = re.sub(r'[\:<>"|?*]', "", match.group(1))
        path = re.sub(r"^\[(.*)\]$", r"\1", path)
        path = re.sub(r"^`(.*)`$", r"\1", path)
        path = re.sub(r"[\]\:]$", "", path)

        # Extract and clean the code content
        content = match.group(2)

        # Add the cleaned path and content to the FilesDict
        files_dict[path.strip()] = content.strip()

    return files_dict


def overwrite_code_with_edits(chat: str, files_dict: FilesDict):
    """
    Parses edits from a chat and applies them to the provided FilesDict object.

    Parameters
    ----------
    chat : str
        The chat content containing code edits.
    files_dict : FilesDict
        The FilesDict object to apply edits to.
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
    Parses edits from a chat string while preserving indentation, returning a list of Edit objects.

    Parameters
    ----------
    chat : str
        The chat string containing edits.

    Returns
    -------
    List[Edit]
        A list of Edit objects representing the parsed edits.
    """
    edits = []
    lines = chat.split("\n")
    filename = ""
    for line in lines:
        if line.startswith("File:"):
            filename = line.split(":")[1].strip()
        else:
            # Extract line number, edit type, and content with leading spaces
            match = re.match(r"(\d+) ([-+])\s?(.*\S.*)", line)
            if match:
                line_number, symbol, content = match.groups()
                line_number = int(line_number)
                is_before = symbol == "-"
                edits.append(Edit(filename, line_number, content, is_before))

    # Sort edits for sequential application
    edits.sort(key=lambda edit: (edit.filename, edit.line_number, not edit.is_before))
    return edits


def is_similar(str1, str2):
    """
    Compares two strings for similarity, ignoring spaces and case.

    Parameters
    ----------
    str1, str2 : str
        The strings to compare.

    Returns
    -------
    bool
        True if the strings are similar, False otherwise.
    """
    str1, str2 = str1.replace(" ", "").lower(), str2.replace(" ", "").lower()

    counter1, counter2 = Counter(str1), Counter(str2)
    intersection = sum((counter1 & counter2).values())
    longer_length = max(len(str1), len(str2))

    return intersection >= 0.9 * longer_length


def apply_edits(edits: List[Edit], files_dict: FilesDict):
    """
    Applies a list of Edit objects to the provided FilesDict object.

    Parameters
    ----------
    edits : List[Edit]
        The list of edits to apply.
    files_dict : FilesDict
        The FilesDict object to be modified.
    """
    for edit in edits:
        filename = edit.filename
        if filename not in files_dict:
            files_dict[filename] = ""
            logger.warning(f"Created new file: {filename}")

        lines = files_dict[filename].split("\n")
        line_number = min(edit.line_number - 1, len(lines))

        if line_number < len(lines):
            if edit.is_before:  # Deletion
                if is_similar(lines[line_number], edit.content):
                    lines[line_number] = "# Line deleted line by GPT"
                    logger.warning(
                        f"Deleted from {filename}, line {edit.line_number}: '{edit.content}'"
                    )
                else:
                    logger.warning(
                        f"line {edit.line_number}: '{edit.content}' not found in {filename} where should be '{lines[line_number]}'"
                    )
            else:  # Addition
                if (
                    lines[line_number] == "# Line deleted line by GPT"
                    or len(files_dict[filename]) == 0
                ):
                    lines[line_number] = edit.content
                    logger.warning(
                        f"Added to {filename}, line {edit.line_number}: '{edit.content.strip()}'"
                    )
                else:
                    logger.warning(
                        f"The addition of {edit.content} is discarded for wrong line number"
                    )
        else:
            if not edit.is_before:
                lines.append(edit.content)
                logger.warning(
                    f"Added to {filename}, line {edit.line_number}: '{edit.content.strip()}'"
                )

        files_dict[filename] = "\n".join(lines)
