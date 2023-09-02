import os
import re
import sys
import tkinter as tk
import tkinter.filedialog as fd

from pathlib import Path
from typing import List, Union

IGNORE_FOLDERS = {"site-packages", "node_modules"}


class DisplayablePath(object):
    """
    A class representing a displayable path in a file explorer.
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
    def make_tree(cls, root: Union[str, Path], parent=None, is_last=False, criteria=None):
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


class TerminalFileSelector:
    def __init__(self, root_folder_path: Path) -> None:
        self.number_of_selectable_items = 0
        self.selectable_file_paths: dict[int, str] = {}
        self.file_path_list: list = []
        self.db_paths = DisplayablePath.make_tree(
            root_folder_path, parent=None, criteria=is_in_ignoring_extensions
        )

    def display(self):
        """
        Select files from a directory and display the selected files.
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

    def ask_for_selection(self) -> List[str]:
        """
        Ask user to select files from the terminal after displaying it

        Returns:
            List[str]: list of selected paths
        """
        user_input = input(
            "\nSelect files by entering the numbers separated by commas/spaces or "
            + "specify range with a dash. "
            + "Example: 1,2,3-5,7,9,13-15,18,20 (enter 'all' to select everything)"
            + "\n\nSelect files:"
        )
        selected_paths = []
        regex = r"\d+(-\d+)?([, ]\d+(-\d+)?)*"

        if user_input.lower() == "all":
            selected_paths = self.file_path_list
        elif re.match(regex, user_input):
            try:
                user_input = (
                    user_input.replace(" ", ",") if " " in user_input else user_input
                )
                selected_files = user_input.split(",")
                for file_number_str in selected_files:
                    if "-" in file_number_str:
                        start_str, end_str = file_number_str.split("-")
                        start = int(start_str)
                        end = int(end_str)
                        for num in range(start, end + 1):
                            selected_paths.append(str(self.selectable_file_paths[num]))
                    else:
                        num = int(file_number_str)
                        selected_paths.append(str(self.selectable_file_paths[num]))

            except ValueError:
                pass
        else:
            print("Please use a valid number/series of numbers.\n")
            sys.exit(1)

        return selected_paths


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


def ask_for_files(db_input) -> None:
    """
    Ask user to select files to improve.
    It can be done by terminal, gui, or using the old selection.

    Returns:
        dict[str, str]: Dictionary where key = file name and value = file path
    """
    use_last_string = ""
    is_valid_selection = False
    can_use_last = False
    if "file_list.txt" in db_input:
        can_use_last = True
        use_last_string = (
            "3. Use previous file list (available at "
            + f"{os.path.join(db_input.path, 'file_list.txt')})\n"
        )
        selection_number = 3
    else:
        selection_number = 1
    selection_str = f"""How do you want to select the files?

1. Use Command-Line.
2. Use File explorer.
{use_last_string if len(use_last_string) > 1 else ""}
Select option and press Enter (default={selection_number}): """
    file_path_list = []
    selected_number_str = input(selection_str)
    if selected_number_str:
        try:
            selection_number = int(selected_number_str)
        except ValueError:
            print("Invalid number. Select a number from the list above.\n")
            sys.exit(1)
    if selection_number == 1:
        # Open terminal selection
        file_path_list = terminal_file_selector()
        is_valid_selection = True
    elif selection_number == 2:
        # Open GUI selection
        file_path_list = gui_file_selector()
        is_valid_selection = True
    else:
        if can_use_last and selection_number == 3:
            # Use previous file list
            is_valid_selection = True
    if not is_valid_selection:
        print("Invalid number. Select a number from the list above.\n")
        sys.exit(1)

    file_list_string = ""
    if not selection_number == 3:
        # New files
        for file_path in file_path_list:
            file_list_string += str(file_path) + "\n"

        # Write in file_list so the user can edit and remember what was done
        db_input["file_list.txt"] = file_list_string


def gui_file_selector() -> List[str]:
    """
    Display a tkinter file selection window to select context files.
    """
    root = tk.Tk()
    root.withdraw()
    root.call("wm", "attributes", ".", "-topmost", True)
    file_list = list(
        fd.askopenfilenames(
            parent=root,
            initialdir=os.getcwd(),
            title="Select files to improve (or give context):",
        )
    )
    return file_list


def terminal_file_selector() -> List[str]:
    """
    Display a terminal file selection to select context files.
    """
    file_selector = TerminalFileSelector(Path(os.getcwd()))
    file_selector.display()
    selected_list = file_selector.ask_for_selection()
    return selected_list
