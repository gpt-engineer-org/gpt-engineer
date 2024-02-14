"""
Chat to Files Module

This module provides utilities to handle and process chat content, especially for extracting code blocks
and managing them within a specified GPT Engineer project ("workspace"). It offers functionalities like parsing chat messages to
retrieve code blocks, storing these blocks into a workspace, and overwriting workspace content based on
new chat messages. Moreover, it aids in formatting and reading file content for an AI agent's input.

Key Features:
- Efficient extraction of code blocks from chat messages for workspace integration.
- Dynamic updating of workspace files with new chat content.
- Automated formatting of files for AI agent processing.
- Retrieval of specific files and content for detailed analysis.

Dependencies:
- `os` and `pathlib`: For handling OS-level operations and path manipulations.
- `re`: For regex-based parsing of chat content.
- `gpt_engineer.core.db`: Database handling functionalities for the workspace.
- `gpt_engineer.cli.file_selector`: Constants related to file selection.

Functions:
- chat_to_files_dict(chat: str) -> FilesDict
    Extracts code blocks from a chat and returns them as a FilesDict object.
- overwrite_code_with_edits(chat: str, files_dict: FilesDict)
    Overwrites code with edits extracted from chat.
- parse_edits(chat: str) -> List[Edit]
    Parses edits from a chat string and returns them as a list of Edit objects.
- apply_edits(edits: List[Edit], files_dict: FilesDict)
    Applies a list of edits to the given code object.
"""

import logging
import re

from typing import Dict

from gpt_engineer.core.diff import ADD, REMOVE, RETAIN, Diff, Hunk
from gpt_engineer.core.files_dict import FilesDict, file_to_lines_dict

# Configure logging for the module
logger = logging.getLogger(__name__)


def chat_to_files_dict(chat: str) -> FilesDict:
    """

    Extracts code blocks from a chat string and returns a FilesDict object containing
    (filename, codeblock) pairs.
    Extracts all code blocks from a chat and returns them as a FilesDict object.
    Parses the chat string to identify and extract code blocks, which are then stored in a FilesDict
    object with filenames as keys and code content as values.

    Parameters
    ----------
    chat : str
        The chat string to extract code blocks from.

    Returns
    -------
    FilesDict
        A FilesDict object containing the extracted code blocks, with filenames as keys.
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

def apply_diffs(diffs: Dict[str, Diff], files: FilesDict) -> FilesDict:
    """
    Applies a set of diffs to a FilesDict object and returns the modified FilesDict.


    Parameters
    ----------
    diffs : Dict[str, Diff]
        A dictionary of file paths and their respective diffs to apply.
    files : FilesDict
        The FilesDict object to apply the diffs to.

    Returns
    -------
    FilesDict
        A FilesDict object with the diffs applied to the original files.
    """
    REMOVE_FLAG = "<REMOVE_LINE>"  # Placeholder to mark lines for removal
    for diff in diffs.values():
        if diff.is_new_file():
            files[diff.filename_post] = "\n".join(
                line[1] for hunk in diff.hunks for line in hunk.lines
            )
        else:
            line_dict = file_to_lines_dict(files[diff.filename_pre])
            for hunk in diff.hunks:
                current_line = hunk.start_line_pre_edit
                for line in hunk.lines:
                    if line[0] == RETAIN:
                        current_line += 1
                    elif line[0] == ADD:
                        # Append at the end of the previous line facilitates parsing non-complete additions
                        current_line -= 1
                        # Append a new line and the content if the line exists, else just add the content
                        if (
                            current_line in line_dict.keys()
                            and line_dict[current_line] != REMOVE_FLAG
                        ):
                            line_dict[current_line] += "\n" + line[1]
                        else:
                            line_dict[current_line] = line[1]
                        print(
                            f"\nAdded line {line[1]} to {diff.filename_post} at line {current_line} end"
                        )
                        current_line += 1
                    elif line[0] == REMOVE:
                        # Make the line content empty
                        line_dict[
                            current_line
                        ] = REMOVE_FLAG  # Mark the line for removal
                        print(
                            f"\nRemoved line {line[1]} from {diff.filename_post} at line {current_line}"
                        )
                        current_line += 1
            # Remove lines marked for removal
            line_dict = {
                key: line_content
                for key, line_content in line_dict.items()
                if REMOVE_FLAG not in line_content
            }
            files[diff.filename_post] = "\n".join(line_dict.values())
    return files


def parse_diffs(diff_string: str) -> dict:
    # Regex to match a complete diff block
    diff_block_pattern = re.compile(
        r"```.*?\n\s*?--- .*?\n\s*?\+\+\+ .*?\n(?:@@ .*? @@\n(?:[-+ ].*?\n)*?)*?```",
        re.DOTALL,
    )

    diffs = {}
    for block in diff_block_pattern.finditer(diff_string):
        diff_block = block.group()

        # Process each diff block
        diffs.update(parse_diff_block(diff_block))

    if not diffs:
        raise ValueError(
            f"The diff {diff_string} is not a valid diff in the unified git diff format"
        )

    return diffs


def parse_diff_block(diff_block: str) -> dict:
    lines = diff_block.strip().split("\n")[1:-1]  # Exclude the starting and ending ```
    diffs = {}
    current_diff = None
    hunk_lines = []
    filename_pre = None
    filename_post = None
    hunk_header = None

    for line in lines:
        if line.startswith("--- "):
            filename_pre = line[4:]
        elif line.startswith("+++ "):
            if (
                filename_post is not None
                and current_diff is not None
                and hunk_header is not None
            ):
                current_diff.hunks.append(Hunk(*hunk_header, hunk_lines))
                hunk_lines = []
            filename_post = line[4:]
            current_diff = Diff(filename_pre, filename_post)
            diffs[filename_post] = current_diff
        elif line.startswith("@@ "):
            if hunk_lines and current_diff is not None and hunk_header is not None:
                current_diff.hunks.append(Hunk(*hunk_header, hunk_lines))
                hunk_lines = []
            hunk_header = parse_hunk_header(line)
        elif line.startswith("+"):
            hunk_lines.append((ADD, line[1:]))
        elif line.startswith("-"):
            hunk_lines.append((REMOVE, line[1:]))
        elif line.startswith(""):
            hunk_lines.append((RETAIN, line[1:]))

    # Check current_diff is not None before appending last hunk
    if current_diff is not None and hunk_lines and hunk_header is not None:
        current_diff.hunks.append(Hunk(*hunk_header, hunk_lines))

    return diffs


def parse_hunk_header(header_line):
    # Regular expression to validate the hunk header format
    # This regex checks for the pattern @@ -[0-9]+,[0-9]+ +[0-9]+,[0-9]+ @@
    pattern = re.compile(r"^@@ -\d{1,},\d{1,} \+\d{1,},\d{1,} @@$")

    # Check if the header line matches the expected format
    if not pattern.match(header_line):
        # If not, let the validation and correction functions work out right numbers
        return (0, 0, 0, 0)

    # Proceed with parsing if the format is correct
    pre, post = header_line.split(" ")[1:3]
    start_line_pre_edit, hunk_len_pre_edit = map(int, pre[1:].split(","))
    start_line_post_edit, hunk_len_post_edit = map(int, post[1:].split(","))
    return (
        start_line_pre_edit,
        hunk_len_pre_edit,
        start_line_post_edit,
        hunk_len_post_edit,
    )
