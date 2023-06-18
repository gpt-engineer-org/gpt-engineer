from dataclasses import dataclass
from pathlib import Path


# This class represents a simple database that stores its data as files in a directory.
# It supports both text and binary files, and can handle directory structures.
class DB:
    def __init__(self, path):
        # Convert the path string to a Path object and get its absolute path.
        self.path = Path(path).absolute()

        # Create the directory if it doesn't exist.
        self.path.mkdir(parents=True, exist_ok=True)

    def __getitem__(self, key):
        # Combine the database directory with the provided file path.
        full_path = self.path / key

        # Check if the file exists before trying to open it.
        if full_path.is_file():
            # Open the file in text mode and return its content.
            with full_path.open("r") as f:
                return f.read()
        else:
            # If the file doesn't exist, raise an error.
            raise FileNotFoundError(f"No such file: '{full_path}'")

    def __setitem__(self, key, val):
        # Combine the database directory with the provided file path.
        full_path = self.path / key

        # Create the directory tree if it doesn't exist.
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Write the data to the file. If val is a string, it's written as text.
        # If val is bytes, it's written as binary data.
        if isinstance(val, str):
            full_path.write_text(val)
        elif isinstance(val, bytes):
            full_path.write_bytes(val)
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
