from dataclasses import dataclass
from pathlib import Path


# This class represents a simple database that stores its data as files in a directory.
class DB:
    """A simple key-value store, where keys are filenames and values are file contents."""

    def __init__(self, path):
        self.path = Path(path).absolute()

        self.path.mkdir(parents=True, exist_ok=True)

    def __getitem__(self, key):
        full_path = self.path / key

        if not full_path.is_file():
            full_path.touch()
            default_text = "You will read instructions and not carry them out, only seek to clarify them. Specifically you will first summarise a list of super short bullets of areas that need clarification. Then you will pick one clarifying question, and wait for an answer from the user."
            full_path.write_text(default_text, encoding="utf-8")
        with full_path.open("r", encoding="utf-8") as f:
            return f.read()

    def __setitem__(self, key, val):
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
    identity: DB
    input: DB
    workspace: DB
