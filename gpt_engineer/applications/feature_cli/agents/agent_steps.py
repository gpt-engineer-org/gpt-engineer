from gpt_engineer.applications.feature_cli.feature import Feature
from gpt_engineer.applications.feature_cli.file_selection import FileSelector
from gpt_engineer.applications.feature_cli.repository import (
    Repository,
    GitContext,
)
from gpt_engineer.applications.feature_cli.generation_tools import (
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

from prompt_toolkit import (
    prompt as cli_input,
    PromptSession as InputSession,
    HTML,
    print_formatted_text,
)
from prompt_toolkit.validation import ValidationError, Validator
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


def print_feature_state(feature, file_selector):

    if not feature.has_description():
        output = "No active feature."
    else:
        feature_description = feature.get_description()
        file_string = file_selector.get_pretty_selected_from_yaml()
        completed_tasks_string = "None"
        active_task_string = "None"

        completed_tasks = feature.get_progress()["done"]

        if completed_tasks and len(completed_tasks) > 0:
            completed_tasks_string = "\n".join(
                [f"• {task}" for task in completed_tasks]
            )

        if feature.has_task():
            active_task_string = feature.get_task()

        output = f"""
---

<b>Active Feature</b>

<i>{feature_description}</i>

<b>File Selection</b>

<i>{file_string}</i>

<b>Completed Tasks</b>

<i>{completed_tasks_string}</i>

<b>Active Task</b>

<i>{active_task_string}</i>

---
"""

    print_formatted_text(HTML(output))


def select_create_branch():
    completer = WordCompleter(["1", "2", "x"], ignore_case=True)
    session = InputSession()

    # Using prompt to get user input
    result = session.prompt(
        """Would you like to 

1 - Initialize new feature (on new branch)
2 - Initialize new feature (on current branch)

x - Exit

""",
        completer=completer,
    ).lower()

    print()

    if result == "1":
        return True
    if result == "2":
        return False
    if result == "x":
        print("Exiting...")
        return


def initialize_new_feature(ai: AI, feature: Feature, repository: Repository):

    create__branch = select_create_branch()

    feature.clear_feature()

    update_feature_description(feature)

    if create__branch:
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
    input("\nPlease edit the feature file and then press Enter to continue...")


def update_task_description(feature: Feature):
    feature.open_task_in_editor()
    input("\nPlease edit the task file and then press Enter to continue...")


def update_feature(feature: Feature, file_selector: FileSelector):
    completer = WordCompleter(["1", "2", "3", "x"], ignore_case=True)
    session = InputSession()

    result = session.prompt(
        HTML(
            """
<b>Would you like to:</b>

<green>1 - Edit Feature Description</green>
<green>2 - Edit File Selection</green>
<green>3 - Finish/Deactivate Feature</green>

<green>x - Exit</green>

"""
        ),
        completer=completer,
    ).lower()

    print()

    if result == "1":
        update_feature_description(feature)
    if result == "2":
        update_user_file_selection(file_selector)
    if result == "3":
        print("Sorry! Not implemented yet.")
    if result == "x":
        print("Exiting...")
        return


def initiate_new_task(ai, feature, git_context, file_selector):
    """
    Runs a flow which ends in the user saving a new task in the task.md file
    """

    completer = WordCompleter(["1", "2", "3", "x"], ignore_case=True)
    session = InputSession()

    result = session.prompt(
        HTML(
            """
<blue>No active task...</blue>

<b>Would you like to:</b>

<green>1 - Suggest New Tasks (Recommended)</green>
<green>2 - New Custom Task</green>

<green>x - Exit</green>

"""
        ),
        completer=completer,
    ).lower()

    print()

    if result == "1":
        suggest_new_tasks(ai, feature, git_context, file_selector)
    elif result == "2":
        update_task_description(feature)
    elif result == "x":
        print("Exiting...")
        return


def get_git_context(repository):
    with yaspin(text="Gathering git context...") as spinner:
        git_context = repository.get_git_context()
        spinner.ok("✔")


def suggest_new_tasks(ai, feature, git_context, file_selector):

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

    task_list_message = "\n".join(
        [f"<green>{i + 1}: {tasks[i]}</green>" for i in range(max_tasks)]
    )

    def get_prompt():
        return f"""
<b>AI Reasoning</b>
<i>{response.planning_thoughts}</i>

<b>Which task would you like to you like to work on?</b>

{task_list_message}

<green>c: Custom task</green>

<green>x: Exit</green>

"""

    session = InputSession()
    result = session.prompt(HTML(get_prompt()), completer=completer).lower()

    print()

    if result in options[:-1]:
        selected_task = tasks[int(result) - 1]
        feature.set_task(selected_task)

    if result == "c":
        update_task_description(feature)

    task = feature.get_task()

    print_formatted_text(
        HTML(
            f"""---

<b>Active Task</b>
                                  
<i>{task}</i>

---
"""
        )
    )


def check_existing_task(feature, file_selector):
    completer = WordCompleter(["1", "2", "3", "x"], ignore_case=True)
    session = InputSession()

    result = session.prompt(
        HTML(
            """<blue>You have an existing task present</blue> 

<b>Would you like to:</b>

<green>1 - Implement task</green>
<green>2 - Mark task as complete</green>
<green>3 - Discard task and continue</green>

<green>x - Exit</green>

"""
        ),
        completer=completer,
    ).lower()

    print()

    if result == "1":
        return True
    if result == "2":
        complete_task(feature, file_selector)
        return False
    if result == "3":
        feature.set_task("")
        return True
    if result == "x":
        print("Exiting...")
        return False

    return False


def check_for_unstaged_changes(
    repository: Repository,
):
    unstaged_changes = repository.get_unstaged_changes()

    if not unstaged_changes:
        return True

    completer = WordCompleter(["1", "2", "3", "x"], ignore_case=True)
    session = InputSession()

    result = session.prompt(
        HTML(
            """<blue>Unstaged changes present...</blue>

<b>Would you like to:</b>

<green>1 - Stage changes and continue</green>
<green>2 - Undo changes and continue</green>
<green>3 - Continue with unstaged changes</green>

<green>x - Exit</green>

"""
        ),
        completer=completer,
    ).lower()

    print()

    if result == "1":
        repository.stage_all_changes()
    if result == "2":
        repository.undo_unstaged_changes()
    if result == "3":
        return True
    if result == "x":
        print("Exiting...")
        return False

    return True


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


def generate_code_for_task(
    project_path,
    feature: Feature,
    git_context: GitContext,
    ai: AI,
    file_selector: FileSelector,
):

    memory = DiskMemory(memory_path(project_path))
    preprompts_holder = PrepromptsHolder(PREPROMPTS_PATH)

    context_string = build_feature_context_string(feature, git_context)

    feature_agent_context = f"""I am working on a feature but breaking it up into small incremental tasks. Your job is to complete the incremental task provided to you - only that task and nothing more.

The purpose of this message is to give you wider context around the feature you are working on and what incremental tasks have already been completed so far.

{context_string}"""

    prompt = Prompt(feature.get_task(), prefix="Task: ")

    files = file_selector.get_included_as_file_repository()

    improve_lambda = lambda: improve_fn(
        ai, prompt, files, memory, preprompts_holder, feature_agent_context
    )

    print_formatted_text("\n---- Beginning code generation ----\n")
    updated_files_dictionary = handle_improve_mode(improve_lambda, memory)
    print("\n---- Ending code generation ----\n")

    files.write_to_disk(updated_files_dictionary)


def run_adjust_loop(feature, file_selector):
    implement = confirm_feature_context_and_task_with_user(feature, file_selector)

    while not implement:
        adjust_prompt_files()
        implement = confirm_feature_context_and_task_with_user(feature, file_selector)


def complete_task(feature, file_selector):
    feature.complete_task()
    file_selector.update_yaml_from_tracked_files()
    print_formatted_text(HTML("<blue>Task Completed</blue>\n"))


def review_changes(
    project_path,
    feature: Feature,
    repository: Repository,
    ai: AI,
    file_selector: FileSelector,
):

    completer = WordCompleter(["1", "2", "3", "4", "5", "x"], ignore_case=True)
    session = InputSession()

    result = session.prompt(
        HTML(
            """<blue>Code generation for task complete </blue>

<green><b>Important:</b> Please review and edit the unstaged changes with your IDE of choice...</green>

<b>Would you like to:</b>

<green>1 - Complete task and stage changes (Recommended)</green>
<green>2 - Complete task and don't stage changes</green>

<green>3 - Undo changes and Retry task</green>
<green>4 - Leave changes and Retry task</green>

<green>5 - Discard task and continue</green>

<green>x - Exit</green>

"""
        ),
        completer=completer,
    ).lower()

    print()

    if result == "1":
        repository.stage_all_changes()
        complete_task(feature, file_selector)
    if result == "2":
        complete_task(feature, file_selector)
    if result == "3":
        print("Rerunning generation...")
        repository.undo_unstaged_changes()
        generate_code_for_task(repository, project_path, feature, ai, file_selector)
    if result == "4":
        print("Rerunning generation...")
        repository.undo_unstaged_changes()
        generate_code_for_task(repository, project_path, feature, ai, file_selector)
    if result == "5":
        feature.clear_task()

    if result == "x":
        print("exiting...")
        return


def confirm_chat_feature():

    completer = WordCompleter(["1", "2", "3", "4", "5", "x"], ignore_case=True)
    session = InputSession()

    result = session.prompt(
        HTML(
            """<blue>Active Feature Detected</blue>

<b>Would you like to:</b>

<green>1 - Chat with feaure context and code</green>
<green>2 - Chat with code only</green>

<green>x - Exit</green>

"""
        ),
        completer=completer,
    ).lower()

    print()

    if result == "1":
        return True
    if result == "2":
        return False

    if result == "x":
        print("exiting...")
        return
