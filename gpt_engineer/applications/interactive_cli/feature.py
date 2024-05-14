import json
import os
import platform
import subprocess
from pathlib import Path
from typing import Union

from gpt_engineer.core.default.disk_memory import DiskMemory


class Feature(DiskMemory):
    """
    Represents a ticket which will be developed incrementally,

    Includes with a feature (overal description of the change),
    a task (current incremental work item),
    and progress (history of incremental work completed)
    """

    def __init__(self, project_path: Union[str, Path]):

        self.feature_path = Path(project_path) / ".feature"
        self.feature_filename = "feature.md"
        self.progress_filename = "progress.json"
        self.task_filename = "task.md"

        super().__init__(self.feature_path)

    def clear_feature(self) -> None:
        self.set_description("")
        self.set_task("")
        super().__setitem__(self.progress_filename, json.dumps({"done": []}))

    def get_description(self) -> str:
        """
        Retrieve the content of the feature file in the database.

        Returns
        -------
        str
            The content of the feature file.
        """
        return super().__getitem__(self.feature_filename)

    def set_description(self, feature_description: str):
        """
        Updates the feature file with new text.

        Parameters
        ----------
        feature_description : str
            The new feature_description to write to the feature file.
        """
        super().__setitem__(self.feature_filename, feature_description)

    def get_progress(self) -> dict:
        """
        Retrieve the progress object.

        Returns
        -------
        str
            The content of the feature file.
        """
        return json.loads(super().__getitem__(self.progress_filename))

    def update_progress(self, task: str):
        """
        Updates the progress with a new completed task.

        Parameters
        ----------
        feature_description : str
            The new feature_description to write to the feature file.
        """
        progress = self.get_progress()
        new_progress = progress["done"].append(task)
        super().__setitem__(self.progress_filename, json.dumps(new_progress, indent=4))

    def set_task(self, task: str):
        """
        Updates the task file with new text.

        Parameters
        ----------
        task : str
            The new task to write to the feature file.
        """
        super().__setitem__(self.task_filename, task)

    def get_task(self) -> str:
        """
        Retrieve the content of the feature file in the database.

        Returns
        -------
        str
            The content of the feature file.
        """
        return super().__getitem__(self.task_filename)

    def complete_task(self):
        """
        Moves the current task to the 'done' list in the progress.json file and clears the task file.
        """
        task = self.get_task()

        if task:
            self.update_progress(task)
            self.set_task("")

    def _file_path(self, filename):
        return self.feature_path / filename

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

    def open_feature_in_editor(self):
        """
        Opens the feature file in the default system editor.
        """
        self._open_file_in_editor(self._file_path(self.feature_filename))

    def open_task_in_editor(self):
        """
        Opens the task file in the default system editor.
        """
        self._open_file_in_editor(self._file_path(self.task_filename))
