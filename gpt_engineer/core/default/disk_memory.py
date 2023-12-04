"""
Module for simple file-based key-value database management.

This module provides a simple file-based key-value database system, where keys are
represented as filenames and values are the contents of these files. The primary class,
DB, is responsible for the CRUD operations on the database. Additionally, the module
provides a dataclass `DBs` that encapsulates multiple `DB` instances to represent different
databases like memory, logs, preprompts, etc.

Functions:
    archive(dbs: DBs) -> None:
        Archives the memory and workspace databases, moving their contents to
        the archive database with a timestamp.

Classes:
    DB:
        A simple key-value store implemented as a file-based system.

    DBs:
        A dataclass containing multiple DB instances representing different databases.

Imports:
    - datetime: For timestamp generation when archiving.
    - shutil: For moving directories during archiving.
    - dataclasses: For the DBs dataclass definition.
    - pathlib: For path manipulations.
    - typing: For type annotations.
"""

import json
import shutil

from gpt_engineer.core.base_memory import BaseMemory
from pathlib import Path
from typing import Any, Optional, Union, Iterator, Dict
from gpt_engineer.tools.experimental.supported_languages import SUPPORTED_LANGUAGES


# This class represents a simple database that stores its tools as files in a directory.
class DiskMemory(BaseMemory):
    """
    A file-based key-value store where keys correspond to filenames and values to file contents.

    This class provides an interface to a file-based database, leveraging file operations to
    facilitate CRUD-like interactions. It allows for quick checks on the existence of keys,
    retrieval of values based on keys, and setting new key-value pairs.

    Attributes:
        path (Path): The directory path where the database files are stored.
    """

    """
    A file-based key-value store where keys correspond to filenames and values to file contents.

    This class provides an interface to a file-based database, leveraging file operations to
    facilitate CRUD-like interactions. It allows for quick checks on the existence of keys,
    retrieval of values based on keys, and setting new key-value pairs.

    Attributes
    ----------
    path : Path
        The directory path where the database files are stored.

    Methods
    -------
    __contains__(key: str) -> bool:
        Check if a file (key) exists in the database.

    __getitem__(key: str) -> str:
        Retrieve the content of a file (value) based on its name (key).

    get(key: str, default: Optional[Any] = None) -> Any:
        Fetch content of a file or return a default value if it doesn't exist.

    __setitem__(key: Union[str, Path], val: str):
        Set or update the content of a file in the database.

    Note:
    -----
    Care should be taken when choosing keys (filenames) to avoid potential
    security issues, such as directory traversal. The class implements some checks
    for this but it's essential to validate inputs from untrusted sources.
    """

    """A simple key-value store, where keys are filenames and values are file contents."""

    def __init__(self, path: Union[str, Path]):
        """
        Initialize the DB class.

        Parameters
        ----------
        path : Union[str, Path]
            The path to the directory where the database files are stored.
        """
        self.path: Path = Path(path).absolute()

        self.path.mkdir(parents=True, exist_ok=True)

    def __contains__(self, key: str) -> bool:
        """
        Check if a file with the specified name exists in the database.

        Parameters
        ----------
        key : str
            The name of the file to check.

        Returns
        -------
        bool
            True if the file exists, False otherwise.
        """
        return (self.path / key).is_file()

    def __getitem__(self, key: str) -> str:
        """
        Get the content of a file in the database.

        Parameters
        ----------
        key : str
            The name of the file to get the content of.

        Returns
        -------
        str
            The content of the file.

        Raises
        ------
        KeyError
            If the file does not exist in the database.
        """
        full_path = self.path / key

        if not full_path.is_file():
            raise KeyError(f"File '{key}' could not be found in '{self.path}'")
        with full_path.open("r", encoding="utf-8") as f:
            return f.read()

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Get the content of a file in the database, or a default value if the file does not exist.

        Parameters
        ----------
        key : str
            The name of the file to get the content of.
        default : any, optional
            The default value to return if the file does not exist, by default None.

        Returns
        -------
        any
            The content of the file, or the default value if the file does not exist.
        """
        try:
            return self[key]
        except KeyError:
            return default

    def __setitem__(self, key: Union[str, Path], val: str) -> None:
        """
        Set the content of a file in the database.

        Parameters
        ----------
        key : Union[str, Path]
            The name of the file to set the content of.
        val : str
            The content to set.

        Raises
        ------
        TypeError
            If val is not string.
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
        Delete a file or directory in the database.

        Parameters
        ----------
        key : Union[str, Path]
            The name of the file or directory to delete.

        Raises
        ------
        KeyError
            If the file or directory does not exist in the database.
        """
        item_path = self.path / key
        if not item_path.exists():
            raise KeyError(f"Item '{key}' could not be found in '{self.path}'")

        if item_path.is_file():
            item_path.unlink()
        elif item_path.is_dir():
            shutil.rmtree(item_path)

    def __iter__(self) -> Iterator[str]:
        return iter(
            sorted(
                str(item.relative_to(self.path))
                for item in sorted(self.path.rglob("*"))
                if item.is_file()
            )
        )

    def __len__(self):
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
        Returns directory as a list of file paths. Useful for passing to the LLM where it needs to understand the wider context of files available for reference.
        """
        if supported_code_files_only:
            return self._supported_files()
        else:
            return self._all_files()

    def to_dict(self) -> Dict[str | Path, str]:
        return {file_path: self[file_path] for file_path in self}

    def to_json(self) -> str:
        return json.dumps(self.to_dict())
