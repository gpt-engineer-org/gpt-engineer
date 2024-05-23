import json
import os
import platform
import subprocess
from pathlib import Path
from typing import Union

from gpt_engineer.core.default.disk_memory import DiskMemory
from gpt_engineer.applications.interactive_cli.file_selection import FileSelector
from gpt_engineer.applications.interactive_cli.repository import Repository


class Feature(DiskMemory):
    """
    Represents a ticket which will be developed incrementally,

    Includes with a feature (overal description of the change),
    a task (current incremental work item),
    and progress (history of incremental work completed)
    """

    def __init__(self, project_path: Union[str, Path], repository: Repository):

        self._feature_path = Path(project_path) / ".feature"
        self._feature_filename = "feature.md"
        self._progress_filename = "progress.json"
        self._task_filename = "task.md"
        self._files_filename = "files.yml"

        self.file_selector = FileSelector(
            Path(project_path) / ".feature" / self._files_filename, repository
        )

        super().__init__(self._feature_path)

    def clear_feature(self) -> None:
        self.set_description(
            """Please replace with your own feature description. Markdown is supported.

Hint: 
Improve your prompts by including technical references to any APIs, libraries, components etc that the pre trained model may not know about in detail already."""
        )
        self.set_task(
            "Please replace with a task description - directing the AI on the first task to implement on this feature"
        )
        super().__setitem__(self._progress_filename, json.dumps({"done": []}))

    def get_description(self) -> str:
        """
        Retrieve the content of the feature file in the database.

        Returns
        -------
        str
            The content of the feature file.
        """
        return super().__getitem__(self._feature_filename)

    def set_description(self, feature_description: str):
        """
        Updates the feature file with new text.

        Parameters
        ----------
        feature_description : str
            The new feature_description to write to the feature file.
        """
        super().__setitem__(self._feature_filename, feature_description)

    def get_progress(self) -> dict:
        """
        Retrieve the progress object.

        Returns
        -------
        str
            The content of the feature file.
        """

        json_string = super().__getitem__(self._progress_filename)
        if json_string:
            return json.loads(json_string)

        return None

    def update_progress(self, task: str):
        """
        Updates the progress with a new completed task.

        Parameters
        ----------
        feature_description : str
            The new feature_description to write to the feature file.
        """
        progress = self.get_progress()

        print(progress["done"])

        progress["done"].append(task)

        json_string = json.dumps(progress, indent=4)

        super().__setitem__(self._progress_filename, json_string)

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
        Retrieve the content of the feature file in the database.

        Returns
        -------
        str
            The content of the feature file.
        """
        return super().__getitem__(self._task_filename)

    def complete_task(self):
        """
        Moves the current task to the 'done' list in the progress.json file and clears the task file.
        """
        task = self.get_task()

        if task:
            self.update_progress(task)
            self.set_task("")

    def _file_path(self, filename):
        return self._feature_path / filename

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
        self._open_file_in_editor(self._file_path(self._feature_filename))

    def open_task_in_editor(self):
        """
        Opens the task file in the default system editor.
        """
        self._open_file_in_editor(self._file_path(self._task_filename))
