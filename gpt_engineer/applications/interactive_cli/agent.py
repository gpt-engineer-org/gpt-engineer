from prompt_toolkit import prompt as cli_input
from prompt_toolkit.validation import Validator, ValidationError

from gpt_engineer.core.ai import AI
from gpt_engineer.core.base_agent import BaseAgent
from gpt_engineer.core.preprompts_holder import PrepromptsHolder
from gpt_engineer.core.prompt import Prompt
from gpt_engineer.core.default.disk_memory import DiskMemory
from gpt_engineer.core.default.paths import PREPROMPTS_PATH, memory_path
from gpt_engineer.core.default.steps import improve_fn


from feature import Feature
from repository import Repository, GitContext
from file_selection import FileSelection
from files import Files
from generation_tools import generate_branch_name

class FeatureValidator(Validator):
    def validate(self, document):
        text = document.text
        if not text:
            raise ValidationError(message="Feature description cannot be empty", cursor_position=len(text))

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
        self.feature = feature
        self.repository = repository
        self.ai = ai or AI()

        self.file_selection = FileSelection(project_path, repository)
        self.memory=DiskMemory(memory_path(project_path)),
        self.preprompts_holder = PrepromptsHolder(PREPROMPTS_PATH)


    def init(self):
        feature_description = cli_input(
                "Write feature description: ",
                multiline=True,
                validator=FeatureValidator(),
                bottom_toolbar="Press Ctrl+O to finish"
            )
            
        self.feature.set_description(feature_description)
            
        # print("\n Ticket files created at .ticket \n ")

        branch_name = generate_branch_name(self.ai, feature_description)

        branch_name = cli_input('\nConfirm branch name: ', default=branch_name)

        # todo: use gitpython to create new branch. 
        
        print(f'\nFeature branch created.\n')

        self.file_selection.update_yaml_from_tracked_files()
        self.file_selection.open_yaml_in_editor()
        input("Please edit the YAML file and then press Enter to continue...")

        self.resume()

    
    def resume(self):

        git_context = self.repository.get_git_context()

        if git_context.unstaged_changes: 
            if input("Unstaged changes present are you sure you want to proceed? y/n").lower() not in ["", "y", "yes"]:
                print("Ok, not proceeding.")
                return
            
        self.file_selection.update_yaml_from_tracked_files()

        context_string = "get context string "
        
        files = Files(self.project_path, self.file_selection.get_from_yaml())

        task = "get_task"

        prompt = Prompt(task)

        improve_fn(files, prompt, files, self.memory, None, context_string)



