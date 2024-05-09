import json
from pathlib import Path

class Ticket:
    """
    Represents a ticket with a feature, task, and progress.
    """
    def __init__(self, feature: str, task: str, progress: dict):
        self.feature = feature
        self.task = task
        self.progress = progress

    @classmethod
    def load_or_create_at_directory(cls, project_path: str) -> "Ticket":
        """
        Load the ticket data from a directory.
        """
        feature_path = Path(project_path) / ".ticket" / "feature"
        task_path = Path(project_path) / ".ticket" / "task"
        progress_path = Path(project_path) / ".ticket" / "progress.json"

        if not feature_path.exists():
            feature = ""
            cls._save_feature()
        else:
            with open(feature_path, 'r', encoding='utf-8') as file:
                feature = file.read().strip()

        if not task_path.exists():
            task = ""
            cls._save_task()
        else:
            with open(task_path, 'r', encoding='utf-8') as file:
                task = file.read().strip()

        if not progress_path.exists():
            progress = {"todo": [], "done": []}
            cls._save_progress()
        else:
            with open(progress_path, 'r', encoding='utf-8') as file:
                progress = json.load(file)

        return cls(feature, task, progress)
    

    def clear_ticket(self):
        """
        Clears the feature and task files and resets the progress.json file.
        """
        self.feature = ""
        self.task = ""
        self.progress = {"todo": [], "done": []}
        self._save()

    def update_feature(self, text: str):
        """
        Updates the feature file with new text.

        Parameters
        ----------
        text : str
            The new text to write to the feature file.
        """
        self.feature = text
        self._save_feature()

    def update_task(self, text: str):
        """
        Updates the task file with new text.

        Parameters
        ----------
        text : str
            The new text to write to the task file.
        """
        self.task = text
        self._save_task()

    def complete_task(self):
        """
        Moves the current task to the 'done' list in the progress.json file and clears the task file.
        """
        if self.task:
            self.progress['done'].append(self.task)
            self.task = ""
            self._save()

    def _save(self):
        """
        Helper method to save the feature, task, and progress to their respective files.
        """
        self._save_feature()
        self._save_task()
        self._save_progress()

    def _save_feature(self):
        with open(Path(self.project_path) / ".ticket" / "feature", 'w', encoding='utf-8') as file:
            file.write(self.feature)

    def _save_task(self):
        with open(Path(self.project_path) / ".ticket" / "task", 'w', encoding='utf-8') as file:
            file.write(self.task)

    def _save_progress(self):
        with open(Path(self.project_path) / ".ticket" / "progress.json", 'w', encoding='utf-8') as file:
            json.dump(self.progress, file, indent=4)