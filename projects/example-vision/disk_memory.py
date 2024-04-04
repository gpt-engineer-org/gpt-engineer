import os
import pickle
from typing import Any

class DiskMemory:
    """
    Disk-based memory system for storing and retrieving data.
    """
    def __init__(self, directory: str):
        self.directory = directory
        if not os.path.exists(directory):
            os.makedirs(directory)

    def _get_file_path(self, key: str) -> str:
        """
        Generates a file path for a given key.
        """
        return os.path.join(self.directory, f"{key}.pkl")

    def write(self, key: str, data: Any):
        """
        Writes data to disk under the specified key.
        """
        file_path = self._get_file_path(key)
        with open(file_path, 'wb') as file:
            pickle.dump(data, file)

    def read(self, key: str) -> Any:
        """
        Reads and returns data stored under the specified key.
        """
        file_path = self._get_file_path(key)
        if not os.path.exists(file_path):
            return None
        with open(file_path, 'rb') as file:
            return pickle.load(file)

    def delete(self, key: str):
        """
        Deletes data stored under the specified key.
        """
        file_path = self._get_file_path(key)
        if os.path.exists(file_path):
            os.remove(file_path)