"""
This module provides functionalities for selecting files from an editor file explorer.

It allows the user to choose files for the purpose of context improvement. This module
provides a tree-based display in the terminal to enable file selection with support for
navigating through directories and ignoring specified directories.

Features:
    - Supports editor file selection.
    - Provides a tree-based display of directories and files.
    - Allows for custom filtering of displayed files and directories.
    - Support to reuse a previous file selection list.
    - Option to ignore specific directories (e.g. "site-packages", "node_modules", "venv").

Classes:
    - DisplayablePath: Represents a displayable path in a file explorer, allowing for a
      tree structure display in the terminal.
    - FileSelector: Enables terminal-based file selection.

Functions:
    - is_in_ignoring_extensions: Checks if a path should be ignored based on predefined rules.
    - ask_for_files: Asks user to select files or uses a previous file list.
    - editor_file_selector: Displays a GUI for file selection.
    - open_with_default_editor: Opens a file in the default system editor or a common fallback.
    - is_utf8: Checks if a file is UTF-8 encoded.
    - get_files_from_toml: Retrieves selected files from a TOML configuration.

Dependencies:
    - os
    - subprocess
    - pathlib
    - typing
    - toml

Note:
    This module is built on top of `gpt_engineer.core.db` and assumes existence and
    functionalities provided by DB and DBs classes.
"""

import os
import subprocess

from pathlib import Path
from typing import List, Union

import toml

from gpt_engineer.core.default.disk_memory import DiskMemory
from gpt_engineer.core.default.paths import metadata_path
from gpt_engineer.core.files_dict import FilesDict

IGNORE_FOLDERS = {"site-packages", "node_modules", "venv"}
FILE_LIST_NAME = "file_selection.toml"


class DisplayablePath(object):
    """
    Represents a path in a file system and displays it in a tree-like structure.
    Useful for displaying file and directory structures like in a file explorer.
    """

    display_filename_prefix_middle = "├── "
    display_filename_prefix_last = "└── "
    display_parent_prefix_middle = "    "
    display_parent_prefix_last = "│   "

    def __init__(
        self, path: Union[str, Path], parent_path: "DisplayablePath", is_last: bool
    ):
        """
        Initialize a DisplayablePath object.
        """
        self.depth = 0
        self.path = Path(str(path))
        self.parent = parent_path
        self.is_last = is_last
        if self.parent:
            self.depth = self.parent.depth + 1  # Increment depth if it has a parent

    @property
    def display_name(self) -> str:
        """
        Get the display name of the file or directory.
        """
        if self.path.is_dir():
            return self.path.name + "/"
        return self.path.name

    @classmethod
    def make_tree(
        cls, root: Union[str, Path], parent=None, is_last=False, criteria=None
    ):
        """
        Generate a tree of DisplayablePath objects.
        """
        root = Path(str(root))
        criteria = criteria or cls._default_criteria
        displayable_root = cls(root, parent, is_last)
        yield displayable_root

        children = sorted(
            list(path for path in root.iterdir() if criteria(path)),
            key=lambda s: str(s).lower(),
        )
        count = 1
        for path in children:
            is_last = count == len(children)
            if path.is_dir() and path.name not in IGNORE_FOLDERS:
                yield from cls.make_tree(
                    path, parent=displayable_root, is_last=is_last, criteria=criteria
                )
            else:
                yield cls(path, displayable_root, is_last)
            count += 1

    @classmethod
    def _default_criteria(cls, path: Path) -> bool:
        """
        The default criteria function to filter the paths.
        """
        return True

    def displayable(self) -> str:
        """
        Get the displayable string representation of the file or directory.
        """
        if self.parent is None:
            return self.display_name

        _filename_prefix = (
            self.display_filename_prefix_last
            if self.is_last
            else self.display_filename_prefix_middle
        )

        parts = ["{!s} {!s}".format(_filename_prefix, self.display_name)]

        parent = self.parent
        while parent and parent.parent is not None:
            parts.append(
                self.display_parent_prefix_middle
                if parent.is_last
                else self.display_parent_prefix_last
            )
            parent = parent.parent

        return "".join(reversed(parts))  # Assemble the parts into the final string


def is_in_ignoring_extensions(path: Path) -> bool:
    """
    Check if a path is not hidden or in the '__pycache__' directory.
    Helps in filtering out unnecessary files during file selection.
    """
    is_hidden = not path.name.startswith(".")
    is_pycache = "__pycache__" not in path.name
    return is_hidden and is_pycache


def ask_for_files(project_path: Union[str, Path]) -> FilesDict:
    """
    Asks the user to select files for the purpose of context improvement.
    It supports selection from the terminal or using a previously saved list.
    """
    metadata_db = DiskMemory(metadata_path(project_path))
    if os.getenv("GPTE_TEST_MODE"):
        # In test mode, retrieve files from a predefined TOML configuration
        assert FILE_LIST_NAME in metadata_db
        selected_files = get_files_from_toml(
            project_path, metadata_db.path / FILE_LIST_NAME
        )
    else:
        # Otherwise, use the editor file selector for interactive selection
        if FILE_LIST_NAME in metadata_db:
            print(
                f"File list detected at {metadata_db.path / FILE_LIST_NAME}. "
                "Edit or delete it if you want to select new files."
            )
            selected_files = editor_file_selector(project_path, False)
        else:
            selected_files = editor_file_selector(project_path, True)

    content_dict = {}
    for file_path in selected_files:
        # selected files contains paths that are relative to the project path
        try:
            # to open the file we need the path from the cwd
            with open(Path(project_path) / file_path, "r") as content:
                content_dict[str(file_path)] = content.read()
        except FileNotFoundError:
            print(f"Warning: File not found {file_path}")
    return FilesDict(content_dict)


def open_with_default_editor(file_path):
    """
    Attempts to open the specified file using the system's default text editor or a common fallback editor.
    """
    editors = ["vim", "nano", "notepad", "gedit"]  # List of fallback editors
    chosen_editor = os.environ.get("EDITOR")

    # Try the preferred editor first, then fallback to common editors
    if chosen_editor:
        try:
            subprocess.run([chosen_editor, file_path])
            return
        except Exception:
            pass

    for editor in editors:
        try:
            subprocess.run([editor, file_path])
            return
        except Exception:
            continue
    print("No suitable text editor found. Please edit the file manually.")


def is_utf8(file_path):
    """
    Determines if the file is UTF-8 encoded by trying to read and decode it.
    Useful for ensuring that files are in a readable and compatible format.
    """
    try:
        with open(file_path, "rb") as file:
            file.read().decode("utf-8")
            return True
    except UnicodeDecodeError:
        return False


def editor_file_selector(input_path: str, init: bool = True) -> List[str]:
    """
    Provides an interactive file selection interface by generating a tree representation in a .toml file.
    Allows users to select or deselect files for the context improvement process.
    """
    root_path = Path(input_path)
    tree_dict = {"files": {}}  # Initialize the dictionary to hold file selection state
    toml_file = (
        DiskMemory(metadata_path(input_path)).path / "file_selection.toml"
    )  # Define the toml file path

    # Initialize .toml file with file tree if in initial state
    if init:
        for path in DisplayablePath.make_tree(
            root_path
        ):  # Create a tree structure from the root path
            if path.path.is_dir() or not is_utf8(path.path):
                continue
            relative_path = os.path.relpath(
                path.path, input_path
            )  # Get the relative path of the file
            tree_dict["files"][relative_path] = {
                "selected": False
            }  # Initialize file selection as False

        # Write instructions and file selection states to .toml file
        comment = (
            "# Change 'selected' from false to true to include files in the edit. "
            "GPT-engineer can only read and edit the files that set to true. "
            "Including irrelevant files will degrade coding performance, "
            "cost additional tokens and potentially lead to violations "
            "of the token limit, resulting in runtime errors.\n\n"
        )
        with open(toml_file, "w") as f:
            f.write(comment)
            toml.dump(tree_dict, f)

    print(
        "Please select(true) and deselect(false) files, save it, and close it to continue..."
    )
    open_with_default_editor(
        toml_file
    )  # Open the .toml file in the default editor for user modification
    return get_files_from_toml(
        input_path, toml_file
    )  # Return the list of selected files after user edits


def get_files_from_toml(input_path, toml_file):
    """
    Retrieves the list of files selected by the user from a .toml configuration file.
    This function parses the .toml file and returns the list of selected files.
    """
    selected_files = []
    edited_tree = toml.load(toml_file)  # Load the edited .toml file

    # Iterate through the files in the .toml and append selected files to the list
    for file, properties in edited_tree["files"].items():
        if properties.get("selected", False):  # Check if the file is selected
            selected_files.append(file)

    # Ensure that at least one file is selected, or raise an exception
    if not selected_files:
        raise Exception(
            "No files were selected. Please select at least one file to proceed."
        )

    print(f"\nYou have selected the following files:\n{input_path}")
    all_paths = set()
    for selected in selected_files:
        all_paths.add(selected)
        all_paths.update(str(Path(selected).parent.resolve()))

    # Display the tree structure of the selected paths
    for path in DisplayablePath.make_tree(Path(input_path)):
        full_path = str(path.path.resolve())
        if full_path in all_paths:
            print(path.displayable())

    print("\n")
    return selected_files
