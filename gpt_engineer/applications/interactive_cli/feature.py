import json
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
        super().__init__(Path(project_path) / ".feature") 


    def clear_feature(self) -> None:
        self.set_description("")
        self.set_task("")
        super().__setitem__("progress.json", json.dumps({"done": []}))

    def get_description(self) -> str:
        """
        Retrieve the content of the feature file in the database.

        Returns
        -------
        str
            The content of the feature file.
        """
        return super().__getitem__("description")
    
    def set_description(self, feature_description: str):
        """
        Updates the feature file with new text.

        Parameters
        ----------
        feature_description : str
            The new feature_description to write to the feature file.
        """
        super().__setitem__("description", feature_description)

    def get_progress(self) -> dict:
        """
        Retrieve the progress object.

        Returns
        -------
        str
            The content of the feature file.
        """
        return json.loads(super().__getitem__("progress.json"))

    def update_progress(self, task: str):
        """
        Updates the progress with a new completed task.

        Parameters
        ----------
        feature_description : str
            The new feature_description to write to the feature file.
        """
        progress= self.get_progress()
        new_progress = progress['done'].append(task)
        super().__setitem__("progress.json", json.dumps(new_progress, indent=4))
    
    def set_task(self, task: str):
        """
        Updates the task file with new text.

        Parameters
        ----------
        task : str
            The new task to write to the feature file.
        """
        super().__setitem__("task",task)

    def get_task(self) -> str:
        """
        Retrieve the content of the feature file in the database.

        Returns
        -------
        str
            The content of the feature file.
        """
        return super().__getitem__("task")


    def complete_task(self):
        """
        Moves the current task to the 'done' list in the progress.json file and clears the task file.
        """
        task = self.get_task()

        if task:
            self.update_progress(task)
            self.set_task("")

