from gpt_engineer.applications.interactive_cli_loop.feature import Feature
from gpt_engineer.applications.interactive_cli_loop.file_selection import FileSelector
from gpt_engineer.applications.interactive_cli_loop.repository import Repository
from gpt_engineer.applications.interactive_cli_loop.files import Files
from gpt_engineer.applications.interactive_cli_loop.generation_tools import (
    generate_branch_name,
    build_feature_context_string,
    generate_suggested_tasks,
)

from gpt_engineer.core.ai import AI
from gpt_engineer.core.prompt import Prompt
from gpt_engineer.core.default.steps import improve_fn, handle_improve_mode
from gpt_engineer.core.default.disk_memory import DiskMemory
from gpt_engineer.core.default.paths import PREPROMPTS_PATH, memory_path
from gpt_engineer.core.preprompts_holder import PrepromptsHolder

from prompt_toolkit import prompt as cli_input
from prompt_toolkit.validation import ValidationError, Validator
from prompt_toolkit import PromptSession as InputSession
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.completion import WordCompleter

from yaspin import yaspin


# This is a random comment to prove the assistant works
class FeatureValidator(Validator):
    def validate(self, document):
        text = document.text
        if not text:
            raise ValidationError(
                message="Feature description cannot be empty", cursor_position=len(text)
            )


def initialize_new_feature(
    ai: AI, feature: Feature, repository: Repository, no_branch: bool
):
    feature.clear_feature()

    update_feature_description(feature)

    if not no_branch:
        print("Creating feature branch... (this can be disabled with -nb setting)")

        branch_name = generate_branch_name(ai, feature.get_description())

        branch_name = cli_input("\nConfirm branch name: ", default=branch_name)

        repository.create_branch(branch_name)
        print("\nFeature branch created.\n")


def update_user_file_selection(file_selector: FileSelector):
    file_selector.update_yaml_from_tracked_files()
    file_selector.open_yaml_in_editor()
    input(
        "Please edit the file selection for this feature and then press Enter to continue..."
    )


def update_feature_description(feature: Feature):
    feature.open_feature_in_editor()
    input("Please edit the feature file and then press Enter to continue...")


def update_task_description(feature: Feature):
    feature.open_task_in_editor()
    input("Please edit the task file and then press Enter to continue...")


def initiate_new_task(ai, feature, git_context, file_selector):

    files = file_selector.get_included_as_file_repository()

    try:
        with yaspin(text="Generating suggested tasks...") as spinner:
            response = generate_suggested_tasks(ai, feature, git_context, files)
            spinner.ok("✔")  # Success message
    except Exception as e:
        raise RuntimeError("Error generating task suggestions.") from e

    tasks = response.tasks

    max_tasks = min(len(tasks), 3)
    options = [str(i + 1) for i in range(max_tasks)] + ["c"]
    completer = WordCompleter(options, ignore_case=True)

    task_list_message = "\n".join([f"{i + 1}: {tasks[i]}" for i in range(max_tasks)])

    def get_prompt():
        return [
            ("class:text", response.planning_thoughts),
            (
                "class:text",
                "\n\nWould you like to work on one of these suggested tasks or choose your own?\n",
            ),
            ("class:text", task_list_message),
            ("class:text", "\nc: Custom task\n"),
        ]

    session = InputSession()
    result = session.prompt(FormattedText(get_prompt()), completer=completer).lower()

    if result in options[:-1]:
        selected_task = tasks[int(result) - 1]
        print(f"Selected task: {selected_task}")
        feature.set_task(selected_task)

    if result == "c":
        update_task_description(feature)


def check_for_unstaged_changes(
    repository: Repository,
):
    unstaged_changes = repository.get_unstaged_changes()

    if unstaged_changes:
        if input(
            "Unstaged changes present are you sure you want to proceed? y/n: "
        ).lower() not in ["", "y", "yes"]:
            print("Ok, not proceeding.")
            return


def confirm_feature_context_and_task_with_user(
    feature: Feature, file_selector: FileSelector
):
    file_selector.update_yaml_from_tracked_files()
    file_string = file_selector.get_pretty_selected_from_yaml()

    feature_description = feature.get_description()
    task = feature.get_task()

    # list feature, files and task
    print(f"Feature: {feature_description}\n\n")
    print(f"Files: \n\nrepo\n{file_string}\n\n")
    print(f"Task: {task}\n\n")

    #  do you want to attempt this task?
    if cli_input("Do you want to implement this task? y/n: ").lower() in [
        "y",
        "yes",
    ]:
        return True

    return False


# todo : create a function which uses the test4.py example code approach to offer a selection of options to the user
# f - "edit feature" using update_feature_description step
# s - "edit file selection" using update_user_file_selection step
# t - "edit task" using update_task_description step
# c - complete the task and start a new one
# x - exit
def adjust_prompt_files():
    input("Please edit the prompt files and then press Enter to continue...")


def run_task_loop(
    project_path,
    feature: Feature,
    repository: Repository,
    ai: AI,
    file_selector: FileSelector,
):

    memory = DiskMemory(memory_path(project_path))
    preprompts_holder = PrepromptsHolder(PREPROMPTS_PATH)

    context_string = build_feature_context_string(feature, repository.get_git_context())

    feature_agent_context = f"""I am working on a feature but breaking it up into small incremental tasks. Your job is to complete the incremental task provided to you - only that task and nothing more.

The purpose of this message is to give you wider context around the feature you are working on and what incremental tasks have already been completed so far.

{context_string}"""

    prompt = Prompt(feature.get_task(), prefix="Task: ")

    files = file_selector.get_included_as_file_repository()

    improve_lambda = lambda: improve_fn(
        ai, prompt, files, memory, preprompts_holder, feature_agent_context
    )

    print("\n---- begining code generation ----\n")
    # Creates loop
    updated_files_dictionary = handle_improve_mode(improve_lambda, memory)
    print("\n---- ending code generation ----\n")

    files.write_to_disk(updated_files_dictionary)

    review_changes(project_path, feature, repository, ai, file_selector)


def run_adjust_loop(feature, file_selector):
    implement = confirm_feature_context_and_task_with_user(feature, file_selector)

    while not implement:
        adjust_prompt_files()
        implement = confirm_feature_context_and_task_with_user(feature, file_selector)


def run_task(repository, project_path, feature, ai, file_selector):
    print("Rerunning generation...")
    check_for_unstaged_changes(repository)
    run_task_loop(project_path, feature, repository, ai, file_selector)


def complete_task(repository, project_path, feature, ai, file_selector):
    print("Completing task... ")
    repository.stage_all_changes()
    feature.complete_task()
    file_selector.update_yaml_from_tracked_files()
    git_context = repository.get_git_context()

    print("Continuing with next task...")
    initiate_new_task(ai, feature, git_context, file_selector)

    check_for_unstaged_changes(repository)

    run_task_loop(project_path, feature, repository, ai, file_selector)


def review_changes(
    project_path,
    feature: Feature,
    repository: Repository,
    ai: AI,
    file_selector: FileSelector,
):

    completer = WordCompleter(["r", "c", "u"], ignore_case=True)
    session = InputSession()

    # Using prompt to get user input
    result = session.prompt(
        """Please review the unstaged changes generated by GPT Engineer.. 

r: Retry the task (incorporating changes to prompt files)
c: Complete task and stage changes 
x: Exit
""",
        completer=completer,
    ).lower()

    if result == "r":
        run_task(repository, project_path, feature, ai, file_selector)
    if result == "c":
        complete_task(repository, project_path, feature, ai, file_selector)
    if result == "x":
        print("exiting...")
        return
