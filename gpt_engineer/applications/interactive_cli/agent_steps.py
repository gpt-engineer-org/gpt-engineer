from feature import Feature
from file_selection import FileSelection
from repository import Repository
from files import Files
from generation_tools import generate_branch_name


from gpt_engineer.core.ai import AI
from gpt_engineer.core.prompt import Prompt
from gpt_engineer.core.default.steps import improve_fn

from prompt_toolkit import prompt as cli_input
from prompt_toolkit.validation import ValidationError, Validator


class FeatureValidator(Validator):
    def validate(self, document):
        text = document.text
        if not text:
            raise ValidationError(
                message="Feature description cannot be empty", cursor_position=len(text)
            )


def initialize_new_feature(ai: AI, feature: Feature):
    feature.clear_feature()

    feature_description = cli_input(
        "Write feature description: ",
        multiline=True,
        validator=FeatureValidator(),
        bottom_toolbar="Press Ctrl+O to finish",
    )

    feature.set_description(feature_description)

    # print("\n Ticket files created at .ticket \n ")

    branch_name = generate_branch_name(ai, feature_description)

    branch_name = cli_input("\nConfirm branch name: ", default=branch_name)

    # todo: use gitpython to create new branch.

    print("\nFeature branch created.\n")


def update_user_file_selection(file_selection: FileSelection):
    file_selection.update_yaml_from_tracked_files()
    file_selection.open_yaml_in_editor()
    input("Please edit the YAML file and then press Enter to continue...")


def check_for_unstaged_changes(
    repository: Repository,
):
    git_context = repository.get_git_context()

    if git_context.unstaged_changes:
        if input(
            "Unstaged changes present are you sure you want to proceed? y/n"
        ).lower() not in ["", "y", "yes"]:
            print("Ok, not proceeding.")
            return


def confirm_task_and_context_with_user(feature: Feature, file_selection: FileSelection):
    file_selection.update_yaml_from_tracked_files()

    feature_description = feature.get_description()
    file_string = file_selection.get_pretty_from_yaml()
    task = feature.get_task()

    # list feature, files and task
    print(f"Feature: {feature_description}\n\n")
    print(f"Files: {file_string}\n\n")
    print(f"Task: {task}\n\n")

    #  do you want to attempt this task?
    if cli_input("Do you want to attempt this task? y/n: ").lower() not in [
        "y",
        "yes",
    ]:
        print("Ok, not proceeding. Perhaps you should update the feature and retry")
        return
        # TODO: if no: do you want to edit feature? edit task? complete? or cancel?


def run_improve_function(ai: AI, feature: Feature, files: Files):

    prompt = Prompt(feature.get_task(), prefix="Task: ")

    #  WIP!


# improve_fn(
#     self.ai, prompt, files, self.memory, self.preprompts_holder, context_string
# )

#     files_dict_before = FileSelector(project_path).ask_for_files()
#     files_dict = handle_improve_mode(prompt, agent, memory, files_dict_before)
#     if not files_dict or files_dict_before == files_dict:
#         print(
#             f"No changes applied. Could you please upload the debug_log_file.txt in {memory.path} folder in a github issue?"
#         )

#     else:
#         print("\nChanges to be made:")
#         compare(files_dict_before, files_dict)

#         print()
#         print(colored("Do you want to apply these changes?", "light_green"))
#         if not prompt_yesno():
#             files_dict = files_dict_before
