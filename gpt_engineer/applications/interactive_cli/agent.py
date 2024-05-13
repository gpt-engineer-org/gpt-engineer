from feature import Feature
from file_selection import FileSelection
from files import Files
from generation_tools import build_context_string, generate_branch_name
from prompt_toolkit import prompt as cli_input
from prompt_toolkit.validation import ValidationError, Validator
from repository import Repository

from gpt_engineer.core.ai import AI
from gpt_engineer.core.base_agent import BaseAgent
from gpt_engineer.core.default.disk_memory import DiskMemory
from gpt_engineer.core.default.paths import PREPROMPTS_PATH, memory_path
from gpt_engineer.core.default.steps import improve_fn
from gpt_engineer.core.preprompts_holder import PrepromptsHolder
from gpt_engineer.core.prompt import Prompt


class FeatureValidator(Validator):
    def validate(self, document):
        text = document.text
        if not text:
            raise ValidationError(
                message="Feature description cannot be empty", cursor_position=len(text)
            )


class FeatureAgent(BaseAgent):
    """
    A cli agent which implements a feature as a set of incremental tasks
    """

    def __init__(
        self,
        project_path: str,
        feature: Feature,
        repository: Repository,
        ai: AI = None,
    ):
        self.project_path = project_path
        self.feature = feature
        self.repository = repository
        self.ai = ai or AI()

        self.file_selection = FileSelection(project_path, repository)
        self.memory = DiskMemory(memory_path(project_path))
        self.preprompts_holder = PrepromptsHolder(PREPROMPTS_PATH)

    def init(self):
        self.feature.clear_feature()

        feature_description = cli_input(
            "Write feature description: ",
            multiline=True,
            validator=FeatureValidator(),
            bottom_toolbar="Press Ctrl+O to finish",
        )

        self.feature.set_description(feature_description)

        # print("\n Ticket files created at .ticket \n ")

        branch_name = generate_branch_name(self.ai, feature_description)

        branch_name = cli_input("\nConfirm branch name: ", default=branch_name)

        # todo: use gitpython to create new branch.

        print("\nFeature branch created.\n")

        self.file_selection.update_yaml_from_tracked_files()
        self.file_selection.open_yaml_in_editor()
        input("Please edit the YAML file and then press Enter to continue...")

        self.resume()

    def improve(self):
        self.resume()

    def resume(self):
        git_context = self.repository.get_git_context()

        if git_context.unstaged_changes:
            if input(
                "Unstaged changes present are you sure you want to proceed? y/n"
            ).lower() not in ["", "y", "yes"]:
                print("Ok, not proceeding.")
                return

        self.file_selection.update_yaml_from_tracked_files()

        context_string = build_context_string(self.feature, git_context)

        files = Files(self.project_path, self.file_selection.get_from_yaml())

        feature = self.feature.get_description()
        file_string = self.file_selection.get_pretty_from_yaml()
        task = self.feature.get_task()

        # list feature, files and task
        print(f"Feature: {feature}\n\n")
        print(f"Files: {file_string}\n\n")
        print(f"Task: {task}\n\n")

        #  do you want to attempt this task?
        if cli_input(
            "Do you want to attempt this task? y/n: ", default="y"
        ).lower() not in ["y", "yes"]:
            print("Ok, not proceeding. Perhaps you should update the feature and retry")
            return
            # if no: do you want to edit feature? edit task? complete? or cancel?

        prompt = Prompt(task, prefix="Task: ")

        improve_fn(
            self.ai, prompt, files, self.memory, self.preprompts_holder, context_string
        )
