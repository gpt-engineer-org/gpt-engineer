import os
import platform
import subprocess
import shutil
from pathlib import Path
from typing import Union

from gpt_engineer.core.default.disk_memory import DiskMemory
from gpt_engineer.core.default.paths import memory_path


class Task(DiskMemory):
    """
    Represents a task that will be done one off without the wider context of a feature
    """

    def __init__(self, project_path: Union[str, Path]):

        self._task_path = Path(memory_path(project_path)) / "task"
        self.path = self._task_path
        self._task_filename = "task.md"
        self._files_filename = "files.yml"

        if not os.path.exists(self._task_path):
            os.makedirs(self._task_path)

        self.set_task("Please replace with task description")

        super().__init__(self._task_path)

    def delete(self):
        shutil.rmtree(self._task_path)

    def set_task(self, task: str):
        """
        Updates the task file with new text.
        Parameters
        ----------
        task : str
            The new task to write to the feature file.
        """
        super().__setitem__(self._task_filename, task)

    def get_task(self) -> str:
        """
        Retrieve the content of the task file in the database.
        Returns
        -------
        str
            The content of the feature file.
        """
        return super().__getitem__(self._task_filename)

    def _file_path(self, filename):
        return self._task_path / filename

    def _open_file_in_editor(self, path):
        """
        Opens the generated YAML file in the default system editor.
        If the YAML file is empty or doesn't exist, generate it first.
        """

        # Platform-specific methods to open the file
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.run(["open", path])
        else:  # Linux and other Unix-like systems
            subprocess.run(["xdg-open", path])

    def open_task_in_editor(self):
        """
        Opens the task file in the default system editor.
        """
        self._open_file_in_editor(self._file_path(self._task_filename))
