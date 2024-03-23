import tempfile

from pathlib import Path
from typing import Union

import autopep8

from gpt_engineer.core.files_dict import FilesDict


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

    def upload(self, files: FilesDict):
        for name, content in files.items():
            path = self.working_dir / name
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w") as f:
                f.write(content)
        return self

    def download(self) -> FilesDict:
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

    def lint_files_dict(self, files_dict: FilesDict) -> FilesDict:
        """
        Lints the given files dictionary. The dictionary keys are file names and the values are the file contents.
        The function supports linting for Python and JavaScript files.

        Parameters
        ----------
        files_dict : dict
            The dictionary containing file names as keys and file contents as values.

        Returns
        -------
        dict
            The dictionary containing linted file contents.
        """
        lint_types = {
            ".py": lint_python_code,
            # ".js": lint_javascript_code,
        }
        for file_name, file_content in files_dict.items():
            for file_type, lint_func in lint_types.items():
                if file_name.endswith(file_type):
                    files_dict[file_name] = lint_func(file_content)
                    print(f"Formatted {file_name} with {lint_func.__name__}")
        return files_dict


# Static method to lint Python code
def lint_python_code(code: str) -> str:
    """
    Lints the given Python code using autopep8.

    Parameters
    ----------
    code : str
        The Python code to be linted.

    Returns
    -------
    str
        The linted Python code.
    """
    return autopep8.fix_code(code)
