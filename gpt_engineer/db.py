import datetime
import shutil

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


# This class represents a simple database that stores its data as files in a directory.
class DB:
    """A simple key-value store, where keys are filenames and values are file contents."""

    def __init__(self, path, in_memory_dict: Optional[Dict[Any, Any]] = None):
        self.path = Path(path).absolute()

        self.path.mkdir(parents=True, exist_ok=True)
        self.in_memory_dict = in_memory_dict

    def __contains__(self, key):
        return (self.path / key).is_file()

    def __getitem__(self, key):
        if self.in_memory_dict is not None:
            return self.in_memory_dict.__getitem__(str((self.path / key).absolute()))
        full_path = self.path / key
        if not full_path.is_file():
            raise KeyError(f"File '{key}' could not be found in '{self.path}'")
        with full_path.open("r", encoding="utf-8") as f:
            return f.read()

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __setitem__(self, key, val):
        if self.in_memory_dict is not None:
            return self.in_memory_dict.__setitem__(str((self.path / key).absolute()), val)
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
    memory: DB
    logs: DB
    preprompts: DB
    input: DB
    workspace: DB
    archive: DB


def archive(dbs: DBs):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.move(
        str(dbs.memory.path), str(dbs.archive.path / timestamp / dbs.memory.path.name)
    )
    shutil.move(
        str(dbs.workspace.path),
        str(dbs.archive.path / timestamp / dbs.workspace.path.name),
    )
    return []
