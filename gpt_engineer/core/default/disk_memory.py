"""
Disk Memory Module
==================

This module provides a simple file-based key-value database system, where keys are
represented as filenames and values are the contents of these files. The `DiskMemory` class
is responsible for the CRUD operations on the database.

Attributes
----------
None

Functions
---------
None

Classes
-------
DiskMemory
    A file-based key-value store where keys correspond to filenames and values to file contents.
"""

import base64
import json
import shutil

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterator, Optional, Union

from gpt_engineer.core.base_memory import BaseMemory
from gpt_engineer.tools.supported_languages import SUPPORTED_LANGUAGES


# This class represents a simple database that stores its tools as files in a directory.
class DiskMemory(BaseMemory):
    """
    A file-based key-value store where keys correspond to filenames and values to file contents.

    This class provides an interface to a file-based database, leveraging file operations to
    facilitate CRUD-like interactions. It allows for quick checks on the existence of keys,
    retrieval of values based on keys, and setting new key-value pairs.

    Attributes
    ----------
    path : Path
        The directory path where the database files are stored.
    """

    def __init__(self, path: Union[str, Path]):
        """
        Initialize the DiskMemory class with a specified path.

        Parameters
        ----------
        path : str or Path
            The path to the directory where the database files will be stored.

        """
        self.path: Path = Path(path).absolute()

        self.path.mkdir(parents=True, exist_ok=True)

    def __contains__(self, key: str) -> bool:
        """
        Determine whether the database contains a file with the specified key.

        Parameters
        ----------
        key : str
            The key (filename) to check for existence in the database.

        Returns
        -------
        bool
            Returns True if the file exists, False otherwise.

        """
        return (self.path / key).is_file()

    def __getitem__(self, key: str) -> str:
        """
        Retrieve the content of a file in the database corresponding to the given key.
        If the file is an image with a .png or .jpeg extension, it returns the content
        in Base64-encoded string format.

        Parameters
        ----------
        key : str
            The key (filename) whose content is to be retrieved.

        Returns
        -------
        str
            The content of the file associated with the key, or Base64-encoded string if it's a .png or .jpeg file.

        Raises
        ------
        KeyError
            If the file corresponding to the key does not exist in the database.
        """
        full_path = self.path / key

        if not full_path.is_file():
            raise KeyError(f"File '{key}' could not be found in '{self.path}'")

        if full_path.suffix in [".png", ".jpeg", ".jpg"]:
            with full_path.open("rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
                mime_type = "image/png" if full_path.suffix == ".png" else "image/jpeg"
                return f"data:{mime_type};base64,{encoded_string}"
        else:
            with full_path.open("r", encoding="utf-8") as f:
                return f.read()

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Retrieve the content of a file in the database, or return a default value if not found.

        Parameters
        ----------
        key : str
            The key (filename) whose content is to be retrieved.
        default : Any, optional
            The default value to return if the file does not exist. Default is None.

        Returns
        -------
        Any
            The content of the file if it exists, a new DiskMemory instance if the key corresponds to a directory.
        """

        item_path = self.path / key
        try:
            if item_path.is_file():
                return self[key]
            elif item_path.is_dir():
                return DiskMemory(item_path)
            else:
                return default
        except:
            return default

    def __setitem__(self, key: Union[str, Path], val: str) -> None:
        """
        Set or update the content of a file in the database corresponding to the given key.

        Parameters
        ----------
        key : str or Path
            The key (filename) where the content is to be set.
        val : str
            The content to be written to the file.

        Raises
        ------
        ValueError
            If the key attempts to access a parent path.
        TypeError
            If the value is not a string.

        """
        if str(key).startswith("../"):
            raise ValueError(f"File name {key} attempted to access parent path.")

        if not isinstance(val, str):
            raise TypeError("val must be str")

        full_path = self.path / key
        full_path.parent.mkdir(parents=True, exist_ok=True)

        full_path.write_text(val, encoding="utf-8")

    def __delitem__(self, key: Union[str, Path]) -> None:
        """
        Delete a file or directory from the database corresponding to the given key.

        Parameters
        ----------
        key : str or Path
            The key (filename or directory name) to be deleted.

        Raises
        ------
        KeyError
            If the file or directory corresponding to the key does not exist in the database.

        """
        item_path = self.path / key
        if not item_path.exists():
            raise KeyError(f"Item '{key}' could not be found in '{self.path}'")

        if item_path.is_file():
            item_path.unlink()
        elif item_path.is_dir():
            shutil.rmtree(item_path)

    def __iter__(self) -> Iterator[str]:
        """
        Iterate over the keys (filenames) in the database.

        Yields
        ------
        Iterator[str]
            An iterator over the sorted list of keys (filenames) in the database.

        """
        return iter(
            sorted(
                str(item.relative_to(self.path))
                for item in sorted(self.path.rglob("*"))
                if item.is_file()
            )
        )

    def __len__(self) -> int:
        """
        Get the number of files in the database.

        Returns
        -------
        int
            The number of files in the database.

        """
        return len(list(self.__iter__()))

    def _supported_files(self) -> str:
        valid_extensions = {
            ext for lang in SUPPORTED_LANGUAGES for ext in lang["extensions"]
        }
        file_paths = [
            str(item)
            for item in self
            if Path(item).is_file() and Path(item).suffix in valid_extensions
        ]
        return "\n".join(file_paths)

    def _all_files(self) -> str:
        file_paths = [str(item) for item in self if Path(item).is_file()]
        return "\n".join(file_paths)

    def to_path_list_string(self, supported_code_files_only: bool = False) -> str:
        """
        Generate a string representation of the file paths in the database.

        Parameters
        ----------
        supported_code_files_only : bool, optional
            If True, filter the list to include only supported code file extensions.
            Default is False.

        Returns
        -------
        str
            A newline-separated string of file paths.

        """
        if supported_code_files_only:
            return self._supported_files()
        else:
            return self._all_files()

    def to_dict(self) -> Dict[Union[str, Path], str]:
        """
        Convert the database contents to a dictionary.

        Returns
        -------
        Dict[Union[str, Path], str]
            A dictionary with keys as filenames and values as file contents.

        """
        return {file_path: self[file_path] for file_path in self}

    def to_json(self) -> str:
        """
        Serialize the database contents to a JSON string.

        Returns
        -------
        str
            A JSON string representation of the database contents.

        """
        return json.dumps(self.to_dict())

    def log(self, key: Union[str, Path], val: str) -> None:
        """
        Append to a file or create and write to it if it doesn't exist.

        Parameters
        ----------
        key : str or Path
            The key (filename) where the content is to be appended.
        val : str
            The content to be appended to the file.

        """

        if str(key).startswith("../"):
            raise ValueError(f"File name {key} attempted to access parent path.")

        if not isinstance(val, str):
            raise TypeError("val must be str")

        full_path = self.path / "logs" / key
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Touch if it doesnt exist
        if not full_path.exists():
            full_path.touch()

        with open(full_path, "a", encoding="utf-8") as file:
            file.write(f"\n{datetime.now().isoformat()}\n")
            file.write(val + "\n")

    def archive_logs(self):
        """
        Moves all logs to archive directory based on current timestamp
        """
        if "logs" in self:
            archive_dir = (
                self.path / f"logs_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"
            )
            shutil.move(self.path / "logs", archive_dir)
