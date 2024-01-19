"""
file_selector.py

This module offers interactive file selection for projects. Leveraging a terminal-based,
tree-structured display, users can navigate and select files for editing or processing.
It integrates with system editors for direct file modification and supports saving
selections for later use. Designed for efficient workflow enhancement in file-intensive
environments, it offers customizable file filtering and seamless editor integration.

Key Components:
- FileSelector: Manages file selection and interaction.
- DisplayablePath: Provides a structured view of file paths.

Usage:
Typically used in project setup or management phases for selecting specific files.
It operates within the GPT-Engineer environment, relying on core functionalities for
file handling and persistence.

"""

import os
import subprocess

from pathlib import Path
from typing import Any, Dict, List, Union

import toml

from gpt_engineer.core.default.disk_memory import DiskMemory
from gpt_engineer.core.default.paths import metadata_path
from gpt_engineer.core.files_dict import FilesDict


class FileSelector:
    IGNORE_FOLDERS = {"site-packages", "node_modules", "venv", "__pycache__"}
    FILE_LIST_NAME = "file_selection.toml"
    COMMENT = (
        "# Remove '#' to select a file.\n\n"
        "# gpt-engineer can only read selected files. "
        "Including irrelevant files will degrade performance, "
        "cost additional tokens and potentially overflow token limit.\n\n"
    )

    def __init__(self, project_path: Union[str, Path]):
        self.project_path = project_path
        self.metadata_db = DiskMemory(metadata_path(self.project_path))
        self.toml_path = self.metadata_db.path / self.FILE_LIST_NAME

    def ask_for_files(self) -> FilesDict:
        """
        Asks the user to select files for the purpose of context improvement.
        It supports selection from the terminal or using a previously saved list.
        """
        if os.getenv("GPTE_TEST_MODE"):
            # In test mode, retrieve files from a predefined TOML configuration
            assert self.FILE_LIST_NAME in self.metadata_db
            selected_files = self.get_files_from_toml(self.project_path, self.toml_path)
        else:
            # Otherwise, use the editor file selector for interactive selection
            if self.FILE_LIST_NAME in self.metadata_db:
                print(
                    f"File list detected at {self.toml_path}. Edit or delete it if you want to select new files."
                )
                selected_files = self.editor_file_selector(self.project_path, False)
            else:
                selected_files = self.editor_file_selector(self.project_path, True)

        content_dict = {}
        for file_path in selected_files:
            # selected files contains paths that are relative to the project path
            try:
                # to open the file we need the path from the cwd
                with open(Path(self.project_path) / file_path, "r") as content:
                    content_dict[str(file_path)] = content.read()
            except FileNotFoundError:
                print(f"Warning: File not found {file_path}")
        return FilesDict(content_dict)

    def editor_file_selector(
        self, input_path: str | Path, init: bool = True
    ) -> List[str]:
        """
        Provides an interactive file selection interface by generating a tree representation in a .toml file.
        Allows users to select or deselect files for the context improvement process.
        """
        root_path = Path(input_path)
        tree_dict = {}
        toml_file = DiskMemory(metadata_path(input_path)).path / "file_selection.toml"
        # Define the toml file path

        # Initialize .toml file with file tree if in initial state
        if init:
            tree_dict = {x: "selected" for x in self.get_current_files(root_path)}

            s = toml.dumps({"files": tree_dict})

            # add comments on all lines that match = "selected"
            s = "\n".join(
                [
                    "# " + line if line.endswith(' = "selected"') else line
                    for line in s.split("\n")
                ]
            )
            # Write to the toml file
            with open(toml_file, "w") as f:
                f.write(self.COMMENT)
                f.write(s)

        else:
            # Load existing files from the .toml configuration
            all_files = self.get_current_files(root_path)
            s = toml.dumps({"files": {x: "selected" for x in all_files}})

            with open(toml_file, "r") as file:
                selected_files = toml.load(file)

            lines = s.split("\n")
            s = "\n".join(
                lines[:1]
                + [
                    line
                    if line.split(" = ")[0].strip('"') in selected_files["files"]
                    else "# " + line
                    for line in lines[1:]
                ]
            )

            # Write the merged list back to the .toml for user review and modification
            with open(toml_file, "w") as file:
                file.write(self.COMMENT)  # Ensure to write the comment
                file.write(s)

        print(
            "Please select and deselect (add # in front) files, save it, and close it to continue..."
        )
        self.open_with_default_editor(
            toml_file
        )  # Open the .toml file in the default editor for user modification
        return self.get_files_from_toml(
            input_path, toml_file
        )  # Return the list of selected files after user edits

    def open_with_default_editor(self, file_path):
        """
        Attempts to open the specified file using the system's default text editor or a common fallback editor.
        """
        editors = [
            "gedit",
            "notepad",
            "nvim",
            "write",
            "nano",
            "vim",
            "emacs",
        ]  # Putting the beginner-friendly text editor forward
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

    def is_utf8(self, file_path):
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

    def get_files_from_toml(self, input_path, toml_file):
        """
        Retrieves the list of files selected by the user from a .toml configuration file.
        This function parses the .toml file and returns the list of selected files.
        """
        selected_files = []
        edited_tree = toml.load(toml_file)  # Load the edited .toml file

        # Iterate through the files in the .toml and append selected files to the list
        for file, _ in edited_tree["files"].items():
            selected_files.append(file)

        # Ensure that at least one file is selected, or raise an exception
        if not selected_files:
            raise Exception(
                "No files were selected. Please select at least one file to proceed."
            )

        print(f"\nYou have selected the following files:\n{input_path}")

        project_path = Path(input_path).resolve()
        all_paths = set(
            project_path.joinpath(file).resolve(strict=False) for file in selected_files
        )

        try:
            for displayable_path in DisplayablePath.make_tree(project_path):
                if displayable_path.path in all_paths:
                    print(displayable_path.displayable())
        except FileNotFoundError:
            print("Specified path does not exist: ", project_path)
        except Exception as e:
            print("An error occurred while trying to display the file tree:", e)

        print("\n")
        return selected_files

    def merge_file_lists(
        self, existing_files: list[str], new_files: list[str]
    ) -> Dict[str, Any]:
        """
        Merges the new files list with the existing one, preserving the selection status.
        """
        # Update the existing files with any new files or changes
        for file, properties in new_files.items():
            if file not in existing_files:
                existing_files[file] = properties  # Add new files as unselected
            # If you want to update other properties of existing files, you can do so here

        return existing_files

    def get_current_files(self, project_path: Union[str, Path]) -> list[str]:
        """
        Generates a dictionary of all files in the project directory
        with their selection status set to False by default.
        """
        all_files = []
        project_path = Path(
            project_path
        ).resolve()  # Ensure path is absolute and resolved

        for path in project_path.glob("**/*"):  # Recursively list all files
            if path.is_file():
                relpath = path.relative_to(project_path)

                parts = relpath.parts
                if any(part.startswith(".") for part in parts):
                    continue  # Skip hidden fileso
                if any(part in self.IGNORE_FOLDERS for part in parts):
                    continue

                all_files.append(str(relpath))

        return all_files

    def is_in_ignoring_extensions(self, path: Path) -> bool:
        """
        Check if a path is not hidden or in the '__pycache__' directory.
        Helps in filtering out unnecessary files during file selection.
        """
        is_hidden = not path.name.startswith(".")
        is_pycache = "__pycache__" not in path.name
        return is_hidden and is_pycache


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
        Generate a tree of DisplayablePath objects, ensure it's only called on directories.
        """
        root = Path(str(root))  # Ensure root is a Path object
        criteria = criteria or cls._default_criteria
        displayable_root = cls(root, parent, is_last)
        yield displayable_root

        if root.is_dir():  # Check if root is a directory before iterating
            children = sorted(
                list(path for path in root.iterdir() if criteria(path)),
                key=lambda s: str(s).lower(),
            )
            count = 1
            for path in children:
                is_last = count == len(children)
                yield from cls.make_tree(
                    path, parent=displayable_root, is_last=is_last, criteria=criteria
                )
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
