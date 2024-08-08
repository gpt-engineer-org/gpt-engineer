"""
This Python script provides functionalities for parsing chat transcripts that contain file paths and code blocks,
applying diffs to these files, and parsing unified git diff format strings. The script is designed to work within
a larger system that involves processing and manipulating code files based on chat inputs and diff information.

Key Components:
- chat_to_files_dict: Parses a chat transcript, extracting file paths and associated code blocks, and organizes
  them into a FilesDict object, which is a custom dictionary format designed to hold file contents keyed by their paths.

- apply_diffs: Takes a dictionary of Diff objects (which represent changes to be made to files) and a FilesDict
  object containing the current state of files. It applies the changes described by the Diff objects to the
  corresponding files in the FilesDict, updating the file contents as specified by the diffs.

- parse_diffs: Parses a string containing diffs in the unified git diff format, extracting the changes described
  in the diffs and organizing them into a dictionary of Diff objects, keyed by the filename to which each diff applies.

- parse_diff_block: Parses a single block of text from a diff string, translating it into a Diff object that
  represents the changes described in that block of text.

This script is intended for use in environments where code collaboration or review is conducted through chat interfaces,
allowing for the dynamic application of changes to code bases and the efficient handling of file and diff information in chat transcripts.
"""

import logging
import re

from typing import Dict, Tuple

from regex import regex

from gpt_engineer.core.diff import ADD, REMOVE, RETAIN, Diff, Hunk
from gpt_engineer.core.files_dict import FilesDict, file_to_lines_dict

# Initialize a logger for this module
logger = logging.getLogger(__name__)


def chat_to_files_dict(chat: str) -> FilesDict:
    """
    Converts a chat string containing file paths and code blocks into a FilesDict object.

    Args:
    - chat (str): The chat string containing file paths and code blocks.

    Returns:
    - FilesDict: A dictionary with file paths as keys and code blocks as values.
    """
    # Regex to match file paths and associated code blocks
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
    Applies diffs to the provided files.

    Args:
    - diffs (Dict[str, Diff]): A dictionary of diffs to apply, keyed by filename.
    - files (FilesDict): The original files to which diffs will be applied.

    Returns:
    - FilesDict: The updated files after applying diffs.
    """
    files = FilesDict(files.copy())
    REMOVE_FLAG = "<REMOVE_LINE>"  # Placeholder to mark lines for removal
    for diff in diffs.values():
        if diff.is_new_file():
            # If it's a new file, create it with the content from the diff
            files[diff.filename_post] = "\n".join(
                line[1] for hunk in diff.hunks for line in hunk.lines
            )
        else:
            # Convert the file content to a dictionary of lines
            line_dict = file_to_lines_dict(files[diff.filename_pre])
            for hunk in diff.hunks:
                current_line = hunk.start_line_pre_edit
                for line in hunk.lines:
                    if line[0] == RETAIN:
                        current_line += 1
                    elif line[0] == ADD:
                        # Handle added lines
                        current_line -= 1
                        if (
                            current_line in line_dict.keys()
                            and line_dict[current_line] != REMOVE_FLAG
                        ):
                            line_dict[current_line] += "\n" + line[1]
                        else:
                            line_dict[current_line] = line[1]
                        current_line += 1
                    elif line[0] == REMOVE:
                        # Mark removed lines with REMOVE_FLAG
                        line_dict[current_line] = REMOVE_FLAG
                        current_line += 1

            # Remove lines marked for removal
            line_dict = {
                key: line_content
                for key, line_content in line_dict.items()
                if REMOVE_FLAG not in line_content
            }
            # Reassemble the file content
            files[diff.filename_post] = "\n".join(line_dict.values())
    return files


def parse_diffs(diff_string: str, diff_timeout=3) -> dict:
    """
    Parses a diff string in the unified git diff format.

    Args:
    - diff_string (str): The diff string to parse.

    Returns:
    - dict: A dictionary of Diff objects keyed by filename.
    """
    # Regex to match individual diff blocks
    diff_block_pattern = regex.compile(
        r"```.*?\n\s*?--- .*?\n\s*?\+\+\+ .*?\n(?:@@ .*? @@\n(?:[-+ ].*?\n)*?)*?```",
        re.DOTALL,
    )

    diffs = {}
    try:
        for block in diff_block_pattern.finditer(diff_string, timeout=diff_timeout):
            diff_block = block.group()

            # Parse individual diff blocks and update the diffs dictionary
            diff = parse_diff_block(diff_block)
            for filename, diff_obj in diff.items():
                if filename not in diffs:
                    diffs[filename] = diff_obj
                else:
                    print(
                        f"\nMultiple diffs found for {filename}. Only the first one is kept."
                    )
    except TimeoutError:
        print("gpt-engineer timed out while parsing git diff")

    if not diffs:
        print(
            "GPT did not provide any proposed changes. Please try to reselect the files for uploading and edit your prompt file."
        )

    return diffs


def parse_diff_block(diff_block: str) -> dict:
    """
    Parses a block of diff text into a Diff object.

    Args:
    - diff_block (str): A single block of diff text.

    Returns:
    - dict: A dictionary containing a single Diff object keyed by the post-edit filename.
    """
    lines = diff_block.strip().split("\n")[1:-1]  # Exclude the opening and closing ```
    diffs = {}
    current_diff = None
    hunk_lines = []
    filename_pre = None
    filename_post = None
    hunk_header = None

    for line in lines:
        if line.startswith("--- "):
            # Pre-edit filename
            filename_pre = line[4:]
        elif line.startswith("+++ "):
            # Post-edit filename and initiation of a new Diff object
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
            # Start of a new hunk in the diff
            if hunk_lines and current_diff is not None and hunk_header is not None:
                current_diff.hunks.append(Hunk(*hunk_header, hunk_lines))
                hunk_lines = []
            hunk_header = parse_hunk_header(line)
        elif line.startswith("+"):
            # Added line
            hunk_lines.append((ADD, line[1:]))
        elif line.startswith("-"):
            # Removed line
            hunk_lines.append((REMOVE, line[1:]))
        else:
            # Retained line
            hunk_lines.append((RETAIN, line[1:]))

    # Append the last hunk if any
    if current_diff is not None and hunk_lines and hunk_header is not None:
        current_diff.hunks.append(Hunk(*hunk_header, hunk_lines))

    return diffs


def parse_hunk_header(header_line) -> Tuple[int, int, int, int]:
    """
    Parses the header of a hunk from a diff.

    Args:
    - header_line (str): The header line of a hunk.

    Returns:
    - tuple: A tuple containing start and length information for pre- and post-edit.
    """
    pattern = re.compile(r"^@@ -\d{1,},\d{1,} \+\d{1,},\d{1,} @@$")

    if not pattern.match(header_line):
        # Return a default value if the header does not match the expected format
        return 0, 0, 0, 0

    pre, post = header_line.split(" ")[1:3]
    start_line_pre_edit, hunk_len_pre_edit = map(int, pre[1:].split(","))
    start_line_post_edit, hunk_len_post_edit = map(int, post[1:].split(","))
    return (
        start_line_pre_edit,
        hunk_len_pre_edit,
        start_line_post_edit,
        hunk_len_post_edit,
    )
