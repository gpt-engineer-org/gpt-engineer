from gpt_engineer.applications.feature_cli.task import Task
from gpt_engineer.applications.feature_cli.repository import Repository
from gpt_engineer.applications.feature_cli.files import Files
from gpt_engineer.applications.feature_cli.file_selection import FileSelector
from gpt_engineer.applications.feature_cli.agents.agent_steps import (
    adjust_prompt_files,
    check_for_unstaged_changes,
    update_user_file_selection,
)

from gpt_engineer.core.ai import AI
from gpt_engineer.core.prompt import Prompt
from gpt_engineer.core.default.steps import improve_fn, handle_improve_mode
from gpt_engineer.core.default.disk_memory import DiskMemory
from gpt_engineer.core.default.paths import PREPROMPTS_PATH, memory_path
from gpt_engineer.core.preprompts_holder import PrepromptsHolder

from prompt_toolkit import prompt as cli_input


class TaskAgent:
    """
    A cli agent which implements a one off task
    """

    def __init__(
        self,
        ai: AI,
        project_path: str,
        task: Task,
        repository: Repository,
        file_selector: FileSelector,
    ):
        self.ai = ai
        self.project_path = project_path
        self.task = task
        self.repository = repository
        self.file_selector = file_selector

    def _confirm__task_with_user(self):
        file_selector = self.file_selector
        file_selector.update_yaml_from_tracked_files()
        file_string = file_selector.get_pretty_selected_from_yaml()

        task = self.task.get_task()

        print(f"Files: \n\nrepo\n{file_string}\n\n")
        print(f"Task: {task}\n\n")

        #  do you want to attempt this task?
        if cli_input("Do you want to implement this task? y/n: ").lower() in [
            "y",
            "yes",
        ]:
            return True

        return False

    def _run_improve_mode(self):
        memory = DiskMemory(memory_path(self.project_path))
        preprompts_holder = PrepromptsHolder(PREPROMPTS_PATH)

        prompt = Prompt(self.task.get_task())

        selected_files = self.file_selector.get_from_yaml().included_files

        files = Files(self.project_path, selected_files)

        improve_lambda = lambda: improve_fn(
            self.ai, prompt, files, memory, preprompts_holder
        )

        print("\n---- begining code generation ----\n")
        updated_files_dictionary = handle_improve_mode(improve_lambda, memory)
        print("\n---- ending code generation ----\n")

        files.write_to_disk(updated_files_dictionary)

    def run(self):

        self.task.open_task_in_editor()
        input("Please edit the task file and then press Enter to continue...")

        update_user_file_selection(self.file_selector)

        implement = self._confirm__task_with_user()

        while not implement:
            adjust_prompt_files()
            implement = self._confirm__task_with_user()

            check_for_unstaged_changes(self.repository)

        self._run_improve_mode()
