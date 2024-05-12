from prompt_toolkit import prompt as cli_input
from prompt_toolkit.validation import Validator, ValidationError

from gpt_engineer.core.ai import AI
from gpt_engineer.core.base_agent import BaseAgent
from gpt_engineer.core.files_dict import FilesDict
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
        self.project_path = project_path
        self.feature = feature
        self.repository = repository
        self.ai = ai or AI()

        self.file_selection = FileSelection(project_path, repository)
        self.memory=DiskMemory(memory_path(project_path))
        self.preprompts_holder = PrepromptsHolder(PREPROMPTS_PATH)


    def init(self):

        self.feature.clear_feature()
        
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

    def improve(self):
        self.resume()
    
    def resume(self):

        git_context = self.repository.get_git_context()

        if git_context.unstaged_changes: 
            if input("Unstaged changes present are you sure you want to proceed? y/n").lower() not in ["", "y", "yes"]:
                print("Ok, not proceeding.")
                return
            
        self.file_selection.update_yaml_from_tracked_files()

        context_string = self.get_contenxt_string(self.feature, git_context)
        
        files = Files(self.project_path, self.file_selection.get_from_yaml())

        feature = self.feature.get_description()
        file_string = self.file_selection.get_pretty_from_yaml()
        task = self.feature.get_task()


        # list feature and task
        print(f"Feature: {feature}\n\n")
        print(f"Files: {file_string}\n\n")
        print(f"Task: {task}\n\n")

        #  do you want to attempt this task? 
        if cli_input("Do you want to attempt this task? y/n: ", default='y').lower() not in ["y", "yes"]:
            print("Ok, not proceeding. Perhaps you should update the feature and retry")
            return
            # if no: do you want to edit feature? edit task? complete? or cancel?

        prompt = Prompt(task)

        improve_fn(self.ai, prompt, files, self.memory, self.preprompts_holder, context_string)


    def get_contenxt_string(self, feature, git_context:GitContext):
        return f"""I am working on a feature but breaking it up into small incremental tasks. Your job is to complete the incremental task provided to you - only that task and nothign more. 
        
The purpose of this message is to give you wider context around the feature you are working on and what incremental tasks have already been completed so far.

## Feature - this is the description fo the current feature we are working on.
{feature.get_description()}

## Completed Tasks - these are the lists of tasks you have completed so far on the feature branch.
{feature.get_progress()["done"]}

## Git Context - these are the code changes made so far while implementing this feature. This may include work completed by you on previous tasks as well as changes made independently by me.
### Branch Changes - this is the cumulative diff of all the commits so far on the feature branch. 
{git_context.branch_changes}

### Staged Changes - this is the diff of the current staged changes. 
{git_context.staged_changes}
"""


