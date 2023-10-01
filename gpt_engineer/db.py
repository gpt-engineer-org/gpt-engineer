import datetime
import shutil

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Union


# This class represents a simple database that stores its data as files in a directory.
class DB:
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

        assert isinstance(val, str), "val must be str"

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


# dataclass for all dbs:
@dataclass
class DBs:
    memory: DB
    logs: DB
    preprompts: DB
    input: DB
    workspace: DB
    archive: DB
    project_metadata: DB


def archive(dbs: DBs) -> None:
    """
    Archive the memory and workspace databases.

    Parameters
    ----------
    dbs : DBs
        The databases to archive.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.move(
        str(dbs.memory.path), str(dbs.archive.path / timestamp / dbs.memory.path.name)
    )

    exclude_dir = ".gpteng"
    items_to_copy = [f for f in dbs.workspace.path.iterdir() if not f.name == exclude_dir]

    for item_path in items_to_copy:
            destination_path = dbs.archive.path / timestamp / item_path.name
            if item_path.is_file():
                shutil.copy2(item_path, destination_path)
            elif item_path.is_dir():
                shutil.copytree(item_path, destination_path)

    return []
