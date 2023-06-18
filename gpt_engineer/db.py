from dataclasses import dataclass
import os
from pathlib import Path


class DB:
    """A simple key-value store, where keys are filenames and values are file contents."""

    def __init__(self, path):
        self.path = Path(path).absolute()
        os.makedirs(self.path, exist_ok=True)

    def __getitem__(self, key):
        with open(self.path / key, encoding='utf-8') as f:
            return f.read()

    def __setitem__(self, key, val):
        Path(self.path / key).absolute().parent.mkdir(parents=True, exist_ok=True)

        with open(self.path / key, 'w', encoding='utf-8') as f:
            f.write(val)

    def __contains__(self, key):
        return (self.path / key).exists()


@dataclass
class DBs:
    """A dataclass for all dbs"""

    memory: DB
    logs: DB
    identity: DB
    input: DB
    workspace: DB
