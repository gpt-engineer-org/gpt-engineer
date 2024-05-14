from feature import Feature
from file_selection import FileSelection
from repository import Repository
from files import Files
from generation_tools import generate_branch_name, build_context_string
from termcolor import colored

from gpt_engineer.core.ai import AI
from gpt_engineer.core.prompt import Prompt
from gpt_engineer.core.default.steps import improve_fn, handle_improve_mode
from gpt_engineer.core.default.disk_memory import DiskMemory
from gpt_engineer.core.default.paths import PREPROMPTS_PATH, memory_path
from gpt_engineer.core.preprompts_holder import PrepromptsHolder
from gpt_engineer.core.prompt import Prompt

from prompt_toolkit import prompt as cli_input
from prompt_toolkit.validation import ValidationError, Validator
import difflib


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


def update_feature_description(feature: Feature):
    feature.open_feature_in_editor()
    input("Please edit the feature file and then press Enter to continue...")


def update_task_description(feature: Feature):
    feature.open_feature_in_editor()
    input("Please edit the feature file and then press Enter to continue...")


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


def confirm_feature_context_and_task_with_user(
    feature: Feature, file_selection: FileSelection
):
    file_selection.update_yaml_from_tracked_files()

    feature_description = feature.get_description()
    file_string = file_selection.get_pretty_from_yaml()
    task = feature.get_task()

    # list feature, files and task
    print(f"Feature: {feature_description}\n\n")
    print(f"Files: {file_string}\n\n")
    print(f"Task: {task}\n\n")

    #  do you want to attempt this task?
    if cli_input("Do you want to implement this task? y/n: ").lower() in [
        "y",
        "yes",
    ]:
        return True

    return False


def check_if_task_is_complete():

    # feature.complete task
    # then 


def adjust_feature_task_or_files():
    # todo : create a function which uses the test4.py example code approach to offer a selection of options to the user 

    # c - complete the task and start a new one 

    # f - "edit feature" using update_feature_description step 
    # s - "edit file selection" using update_user_file_selection step
    # t - "edit task" using update_task_description step

    # 

def compare_files(f1: Files, f2: Files):
    def colored_diff(s1, s2):
        lines1 = s1.splitlines()
        lines2 = s2.splitlines()

        diff = difflib.unified_diff(lines1, lines2, lineterm="")

        RED = "\033[38;5;202m"
        GREEN = "\033[92m"
        RESET = "\033[0m"

        colored_lines = []
        for line in diff:
            if line.startswith("+"):
                colored_lines.append(GREEN + line + RESET)
            elif line.startswith("-"):
                colored_lines.append(RED + line + RESET)
            else:
                colored_lines.append(line)

        return "\n".join(colored_lines)

    for file in sorted(set(f1) | set(f2)):
        diff = colored_diff(f1.get(file, ""), f2.get(file, ""))
        if diff:
            print(f"Changes to {file}:")
            print(diff)


def prompt_yesno() -> bool:
    TERM_CHOICES = colored("y", "green") + "/" + colored("n", "red") + " "
    while True:
        response = input(TERM_CHOICES).strip().lower()
        if response in ["y", "yes"]:
            return True
        if response in ["n", "no"]:
            break
        print("Please respond with 'y' or 'n'")


def run_improve_function(
    project_path,
    feature: Feature,
    repository: Repository,
    ai: AI,
    file_selection: FileSelection,
):

    memory = DiskMemory(memory_path(project_path))
    preprompts_holder = PrepromptsHolder(PREPROMPTS_PATH)

    context_string = build_context_string(feature, repository.get_git_context())

    prompt = Prompt(feature.get_task(), prefix="Task: ")

    files = Files(project_path, file_selection.get_from_yaml())

    improve_lambda = lambda: improve_fn(
        ai, prompt, files, memory, preprompts_holder, context_string
    )

    updated_files_dictionary = handle_improve_mode(improve_lambda, memory)
    if not updated_files_dictionary or files == updated_files_dictionary:
        print(
            f"No changes applied. Could you please upload the debug_log_file.txt in {memory.path} folder in a github issue?"
        )

    else:
        print("\nChanges to be made:")
        compare_files(files, updated_files_dictionary)

        print()
        print(colored("Do you want to apply these changes?", "light_green"))
        if not prompt_yesno():
            return

    files.write_to_disk(updated_files_dictionary)
