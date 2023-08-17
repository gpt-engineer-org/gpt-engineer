import datetime
import shutil

from dataclasses import dataclass
from pathlib import Path


# This class represents a simple database that stores its data as files in a directory.
class DB:
    """
    A simple key-value store, where keys are filenames and values are file contents.

    Parameters
    ----------
    path : str
        The path to the directory to use for the key-value store
    """

    def __init__(self, path):
        """
        Initialize the DB class.

        Parameters
        ----------
        path : str
            The path to the directory to use for the key-value store
        """
        self.path = Path(path).absolute()

        self.path.mkdir(parents=True, exist_ok=True)

    def __contains__(self, key):
        """
        Check if a key is in the DB.
    
        Parameters
        ----------
        key : str
            The key to check
    
        Returns
        -------
        bool
            True if the key is in the DB, False otherwise
        """
        return (self.path / key).is_file()

    def __getitem__(self, key):
        """
        Get the value for a key in the DB.
    
        Parameters
        ----------
        key : str
            The key to get the value for
    
        Returns
        -------
        str
            The value for the key
    
        Raises
        ------
        KeyError
            If the key is not in the DB
        """
        full_path = self.path / key

        if not full_path.is_file():
            raise KeyError(f"File '{key}' could not be found in '{self.path}'")
        with full_path.open("r", encoding="utf-8") as f:
            return f.read()

    def get(self, key, default=None):
        """
        Get the value for a key in the DB, or a default value if the key is not in the DB.
    
        Parameters
        ----------
        key : str
            The key to get the value for
        default : optional
            The default value to return if the key is not in the DB
    
        Returns
        -------
        The value for the key, or the default value if the key is not in the DB
        """
        try:
            return self[key]
        except KeyError:
            return default

    def __setitem__(self, key, val):
        """
        Set the value for a key in the DB.
    
        Parameters
        ----------
        key : str
            The key to set the value for
        val : str
            The value to set
    
        Raises
        ------
        TypeError
            If val is neither a string nor bytes
        """
        full_path = self.path / key
        full_path.parent.mkdir(parents=True, exist_ok=True)

        if isinstance(val, str):
            full_path.write_text(val, encoding="utf-8")
        else:
            # If val is neither a string nor bytes, raise an error.
            raise TypeError("val must be either a str or bytes")


# dataclass for all dbs:
@dataclass
class DBs:
    """
    A dataclass for all DBs.

    Attributes
    ----------
    memory : DB
        The memory DB
    logs : DB
        The logs DB
    preprompts : DB
        The preprompts DB
    input : DB
        The input DB
    workspace : DB
        The workspace DB
    archive : DB
        The archive DB
    """
    memory: DB
    logs: DB
    preprompts: DB
    input: DB
    workspace: DB
    archive: DB


def archive(dbs: DBs):
    """
    Archive the memory and workspace DBs.

    Parameters
    ----------
    dbs : DBs
        The DBs to archive

    Returns
    -------
    list
        An empty list
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.move(
        str(dbs.memory.path), str(dbs.archive.path / timestamp / dbs.memory.path.name)
    )
    shutil.move(
        str(dbs.workspace.path),
        str(dbs.archive.path / timestamp / dbs.workspace.path.name),
    )
    return []
