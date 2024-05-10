import tempfile

from pathlib import Path
from typing import Union

from gpt_engineer.core.files_dict import FilesDict
from gpt_engineer.core.linting import Linting


class FileStore:
    """
    Module for managing file storage in a temporary directory.

    This module provides a class that manages the storage of files in a temporary directory.
    It includes methods for uploading files to the directory and downloading them as a
    collection of files.

    Classes
    -------
    FileStore
        Manages file storage in a temporary directory, allowing for upload and download of files.

    Imports
    -------
    - tempfile: For creating temporary directories.
    - Path: For handling file system paths.
    - Union: For type annotations.
    - FilesDict: For handling collections of files.
    """

    def __init__(self, path: Union[str, Path, None] = None):
        if path is None:
            path = Path(tempfile.mkdtemp(prefix="gpt-engineer-"))

        self.working_dir = Path(path)
        self.working_dir.mkdir(parents=True, exist_ok=True)
        self.id = self.working_dir.name.split("-")[-1]

    def push(self, files: FilesDict):
        for name, content in files.items():
            path = self.working_dir / name
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w") as f:
                f.write(content)
        return self

    def linting(self, files: FilesDict) -> FilesDict:
        # lint the code
        linting = Linting()
        return linting.lint_files(files)

    def pull(self) -> FilesDict:
        files = {}
        for path in self.working_dir.glob("**/*"):
            if path.is_file():
                with open(path, "r") as f:
                    try:
                        content = f.read()
                    except UnicodeDecodeError:
                        content = "binary file"
                    files[str(path.relative_to(self.working_dir))] = content
        return FilesDict(files)
