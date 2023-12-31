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
    - file_selector: Enables terminal-based file selection.

Functions:
    - is_in_ignoring_extensions: Checks if a path should be ignored based on predefined rules.
    - ask_for_files: Asks user to select files or uses a previous file list.
    - editor_file_selector: Displays a GUI for file selection.

Dependencies:
    - os
    - re
    - sys
    - pathlib
    - typing

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
    A class that represents a path in a file system and provides functionality
    to display it in a tree-like structure similar to that of a file explorer.

    Class Attributes:
        - display_filename_prefix_middle (str): Prefix for filenames in the middle of a list.
        - display_filename_prefix_last (str): Prefix for filenames at the end of a list.
        - display_parent_prefix_middle (str): Prefix for parent directories in the middle of a list.
        - display_parent_prefix_last (str): Prefix for parent directories at the end of a list.

    Attributes:
        - depth (int): Depth of the path in relation to the root.
        - path (Path): The actual path object.
        - parent (DisplayablePath): Parent path. None if it's the root.
        - is_last (bool): Flag to check if the current path is the last child of its parent.

    Methods:
        - display_name: Return the display name for the path, with directories having a trailing '/'.
        - make_tree: Class method to generate a tree of DisplayablePath objects for the given root.
        - _default_criteria: Default criteria for filtering paths.
        - displayable: Generate the displayable string representation of the file or directory.

    Note:
        It is assumed that the global constant IGNORE_FOLDERS is defined elsewhere,
        which lists the folder names to ignore during the tree generation.
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

        Args:
            path (Union[str, Path]): The path of the file or directory.
            parent_path (DisplayablePath): The parent path of the file or directory.
            is_last (bool): Whether the file or directory is the last child of its parent.
        """
        self.depth: int = 0
        self.path = Path(str(path))
        self.parent = parent_path
        self.is_last = is_last
        if self.parent:
            self.depth = self.parent.depth + 1

    @property
    def display_name(self) -> str:
        """
        Get the display name of the file or directory.

        Returns:
            str: The display name.
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

        Args:
            root: The root path of the tree.
            parent: The parent path of the root path. Defaults to None.
            is_last: Whether the root path is the last child of its parent.
            criteria: The criteria function to filter the paths. Defaults to None.

        Yields:
            DisplayablePath: The DisplayablePath objects in the tree.
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

        Args:
            path: The path to check.

        Returns:
            bool: True if the path should be included, False otherwise.
        """
        return True

    def displayable(self) -> str:
        """
        Get the displayable string representation of the file or directory.

        Returns:
            str: The displayable string representation.
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

        return "".join(reversed(parts))


class FileSelector:
    """
    A terminal-based file selector for navigating and selecting files from a specified root folder.

    Attributes:
        number_of_selectable_items (int): The number of items (files) that can be selected.
        selectable_file_paths (dict[int, str]): A mapping from index number to the corresponding file path.
        file_path_list (list): A list containing paths of the displayed files.
        db_paths: A structured representation of all paths (both files and directories) within the root folder.

    Args:
        root_folder_path (Path): The root folder path from where files are to be listed and selected.

    Methods:
        display(): Prints the list of files and directories to the terminal, allowing files to be selectable by number.
        ask_for_selection() -> List[str]: Prompts the user to select files by providing index numbers and returns the list of selected file paths.
    """

    def __init__(self, root_folder_path: Path) -> None:
        self.number_of_selectable_items = 0
        self.selectable_file_paths: dict[int, str] = {}
        self.file_path_list: list = []
        self.db_paths = DisplayablePath.make_tree(
            root_folder_path, parent=None, criteria=is_in_ignoring_extensions
        )
        self.root_folder_path = root_folder_path

    def display(self):
        """
        Displays a list of files from the root folder in the terminal. Files are enumerated for selection,
        while directories are simply listed (currently non-selectable).
        """
        count = 0
        file_path_enumeration = {}
        file_path_list = []
        for path in self.db_paths:
            n_digits = len(str(count))
            n_spaces = 3 - n_digits
            if n_spaces < 0:
                # We can only print 1000 aligned files. I think it is decent enough
                n_spaces = 0
            spaces_str = " " * n_spaces
            if not path.path.is_dir():
                print(f"{count}. {spaces_str}{path.displayable()}")
                file_path_enumeration[count] = path.path
                file_path_list.append(path.path)
                count += 1
            else:
                # By now we do not accept selecting entire dirs.
                # But could add that in the future. Just need to add more functions
                # and remove this else block...
                number_space = " " * n_digits
                print(f"{number_space}  {spaces_str}{path.displayable()}")

        self.number_of_selectable_items = count
        self.file_path_list = file_path_list
        self.selectable_file_paths = file_path_enumeration


def is_in_ignoring_extensions(path: Path) -> bool:
    """
    Check if a path is not hidden or in the __pycache__ directory.

    Args:
        path: The path to check.

    Returns:
        bool: True if the path is not in ignored rules. False otherwise.
    """
    is_hidden = not path.name.startswith(".")
    is_pycache = "__pycache__" not in path.name
    return is_hidden and is_pycache


def ask_for_files(project_path: Union[str, Path]) -> FilesDict:
    """
    Ask user to select files to improve.
    It can be done by terminal, gui, or using the old selection.

    Returns:
        dict[str, str]: Dictionary where key = file name and value = file path
    """

    metadata_db = DiskMemory(metadata_path(project_path))
    if os.getenv("TEST_MODE"):
        print("Test mode: Simulating file selection")
        resolved_path = Path(project_path).resolve()
        all_files = list(resolved_path.glob("**/*"))
        selected_files = [file for file in all_files if file.is_file()]
    else:
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
        file_path = Path(file_path)
        try:
            with open(file_path, "r") as content:
                content_dict[str(file_path)] = content.read()
        except FileNotFoundError:
            print(f"Warning: File not found {file_path}")
    return FilesDict(content_dict)


def open_with_default_editor(file_path):
    """
    Opens the specified file using the system's default text editor or a common fallback.

    Parameters:
    - file_path (str): The path to the file to be opened.

    """

    editors = ["vim", "nano", "notepad", "gedit"]  # A list of common editors
    chosen_editor = os.environ.get("EDITOR")  # Get the preferred editor if set

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
    Determines if a file is UTF-8 encoded by attempting to decode it.

    Parameters:
    - file_path (str): Path to the file.

    Returns:
    - bool: True if file is UTF-8 encoded, False otherwise.
    """
    try:
        with open(file_path, "rb") as file:
            data = file.read()
            data.decode("utf-8")
            return True
    except UnicodeDecodeError:
        return False


def editor_file_selector(input_path: str, init: bool = True) -> List[str]:
    """
    Display an editor file selection to select context files.
    Generates a tree representation in a .toml file and allows users to edit it.
    Users can comment out files to ignore them.
    """
    root_path = Path(input_path)
    tree_dict = {"files": {}}
    toml_file = DiskMemory(metadata_path(input_path)).path / "file_selection.toml"
    if init:
        for path in DisplayablePath.make_tree(root_path):
            if path.path.is_dir() or not is_utf8(path.path):
                continue
            relative_path = os.path.relpath(path.path, input_path)
            tree_dict["files"][relative_path] = {"selected": False}

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
    open_with_default_editor(toml_file)

    selected_files = []
    edited_tree = toml.load(toml_file)
    for file, properties in edited_tree["files"].items():
        if properties.get("selected", False):
            selected_files.append(str(Path(input_path).joinpath(file).resolve()))

    if not selected_files:
        raise Exception(
            "No files were selected. Please select at least one file to proceed."
        )

    print(f"\nYou have selected the following files:\n{input_path}")
    all_paths = set()
    for selected in selected_files:
        all_paths.add(selected)
        all_paths.update(str(Path(selected).parent.resolve()))

    for path in DisplayablePath.make_tree(Path(input_path)):
        full_path = str(path.path.resolve())
        if full_path in all_paths:
            print(path.displayable())

    print("\n")
    return selected_files
