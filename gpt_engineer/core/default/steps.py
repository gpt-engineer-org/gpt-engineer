from gpt_engineer.core.code import Code
from gpt_engineer.core.ai import AI
from gpt_engineer.core.chat_to_files import parse_chat
from gpt_engineer.core.default.paths import ENTRYPOINT_FILE, CODE_GEN_LOG_FILE, ENTRYPOINT_LOG_FILE
from gpt_engineer.data.file_repository import OnDiskRepository
from gpt_engineer.core.base_repository import BaseRepository
from gpt_engineer.core.base_execution_env import BaseExecutionEnv
from langchain.schema import HumanMessage, SystemMessage

import inspect
import os
import re
from termcolor import colored
import subprocess

# TODO: THIS NEEDS A BETTER SOLUTION
PREPROMPTS_PATH = os.path.join("gpt_engineer", "preprompts")


def curr_fn() -> str:
    """
    Retrieves the name of the calling function.

    This function uses Python's inspection capabilities to dynamically fetch the
    name of the function that called `curr_fn()`. This approach ensures that the
    function's name isn't hardcoded, making it more resilient to refactoring and
    changes to function names.

    Returns:
    - str: The name of the function that called `curr_fn()`.
    """
    return inspect.stack()[1].function


def setup_sys_prompt(db: OnDiskRepository) -> str:
    """
    Constructs a system prompt for the AI based on predefined instructions and philosophies.

    This function is responsible for setting up the system prompts for the AI, instructing
    it on how to generate code and the coding philosophy to adhere to. The constructed prompt
    consists of the "roadmap", "generate" (with dynamic format replacements), and the coding
    "philosophy" taken from the given DBs object.

    Parameters:
    - dbs (DBs): The database object containing pre-defined prompts and instructions.

    Returns:
    - str: The constructed system prompt for the AI.
    """
    return (
        db["roadmap"]
        + db["generate"].replace("FILE_FORMAT", db["file_format"])
        + "\nUseful to know:\n"
        + db["philosophy"]
    )


def gen_code(ai: AI, prompt: str, memory: BaseRepository) -> Code:
    """
    Executes the AI model using the default system prompts and saves the full output to memory and program to disk.

    This function prepares the system prompt using the provided database configurations
    and then invokes the AI model with this system prompt and the main input prompt.
    Once the AI generates the output, this function saves it to the specified workspace.
    The AI's execution is tracked using the name of the current function for contextual reference.

    Parameters:
    - ai (AI): An instance of the AI model.
    - dbs (DBs): An instance containing the database configurations, including system and
      input prompts, and file formatting preferences.

    Returns:
    - List[Message]: A list of message objects encapsulating the AI's generated output.

    Note:
    The function assumes the `ai.start` method and the `to_files` utility are correctly
    set up and functional. Ensure these prerequisites are in place before invoking `simple_gen`.
    """
    db = OnDiskRepository(PREPROMPTS_PATH)
    messages = ai.start(setup_sys_prompt(db), prompt, step_name=curr_fn())
    chat = messages[-1].content.strip()
    memory[CODE_GEN_LOG_FILE] = chat
    files = parse_chat(chat)
    code = Code({key: val for key, val in files})
    return code


def gen_entrypoint(ai: AI, code: Code, memory: BaseRepository) -> Code:
    """
    Generates an entry point script based on a given codebase's information.

    This function prompts the AI model to generate a series of Unix terminal commands
    required to a) install dependencies and b) run all necessary components of a codebase
    provided in the workspace. The generated commands are then saved to 'run.sh' in the
    workspace.

    Parameters:
    - ai (AI): An instance of the AI model.
    - dbs (DBs): An instance containing the database configurations and workspace
      information, particularly the 'all_output.txt' which contains details about the
      codebase on disk.

    Returns:
    - List[dict]: A list of messages containing the AI's response.

    Notes:
    - The AI is instructed not to install packages globally, use 'sudo', provide
      explanatory comments, or use placeholders. Instead, it should use example values
      where necessary.
    - The function uses regular expressions to extract command blocks from the AI's
      response to create the 'run.sh' script.
    - It assumes the presence of an 'all_output.txt' file in the specified workspace
      that contains information about the codebase.
    """
    #ToDo: This should enter the preprompts...
    messages = ai.start(
        system=(
            "You will get information about a codebase that is currently on disk in "
            "the current folder.\n"
            "From this you will answer with code blocks that includes all the necessary "
            "unix terminal commands to "
            "a) install dependencies "
            "b) run all necessary parts of the codebase (in parallel if necessary).\n"
            "Do not install globally. Do not use sudo.\n"
            "Do not explain the code, just give the commands.\n"
            "Do not use placeholders, use example values (like . for a folder argument) "
            "if necessary.\n"
        ),
        user="Information about the codebase:\n\n" + code.to_string(),
        step_name=curr_fn(),
    )
    print()
    chat = messages[-1].content.strip()
    regex = r"```\S*\n(.+?)```"
    matches = re.finditer(regex, chat, re.DOTALL)
    entrypoint_code = Code(
        {ENTRYPOINT_FILE: "\n".join(match.group(1) for match in matches)}
    )
    memory[ENTRYPOINT_LOG_FILE] = chat
    return entrypoint_code


def execute_entrypoint(execution_env: BaseExecutionEnv, code: Code) -> None:
    """
    Executes the specified entry point script (`run.sh`) from a workspace.

    This function prompts the user to confirm whether they wish to execute a script named
    'run.sh' located in the specified workspace. If the user confirms, the script is
    executed using a subprocess. The user is informed that they can interrupt the
    execution at any time using ctrl+c.

    Parameters:
    - ai (AI): An instance of the AI model, not directly used in this function but
      included for consistency with other functions.
    - dbs (DBs): An instance containing the database configurations and workspace
      information.

    Returns:
    - List[dict]: An empty list. This function does not produce a list of messages
      but returns an empty list for consistency with the return type of other related
      functions.

    Note:
    The function assumes the presence of a 'run.sh' script in the specified workspace.
    Ensure the script is available and that it has the appropriate permissions
    (e.g., executable) before invoking this function.
    """

    if not ENTRYPOINT_FILE in code:
        raise FileNotFoundError("The required entrypoint " + ENTRYPOINT_FILE + " does not exist in the code.")

    command = code[ENTRYPOINT_FILE]

    print()
    print(
        colored(
            "Do you want to execute this code? (Y/n)",
            "red",
        )
    )
    print()
    print(command)
    print()
    if input().lower() not in ["", "y", "yes"]:
        print("Ok, not executing the code.")
        return []
    print("Executing the code...")
    print()
    print(
        colored(
            "Note: If it does not work as expected, consider running the code"
            + " in another way than above.",
            "green",
        )
    )
    print()
    print("You can press ctrl+c *once* to stop the execution.")
    print()

    execution_env.execute_program(code)


def improve(ai: AI, prompt: str) -> Code:
    """
    Process and improve the code from a specified set of existing files based on a user prompt.

    This function first retrieves the code from the designated files and then formats this
    code to be processed by the Language Learning Model (LLM). After setting up the system prompt
    for existing code improvements, the files' contents are sent to the LLM. Finally, the user's
    prompt detailing desired improvements is passed to the LLM, and the subsequent response
    from the LLM is used to overwrite the original files.

    Parameters:
    - ai (AI): An instance of the AI model that is responsible for processing and generating
      responses based on the provided system and user inputs.
    - dbs (DBs): An instance containing the database configurations, user prompts, and project metadata.
      It is used to fetch the selected files for improvement and the user's improvement prompt.

    Returns:
    - list[Message]: Returns a list of Message objects that record the interaction between the
      system, user, and the AI model. This includes both the input to and the response from the LLM.

    Notes:
    - Ensure that the user has correctly set up the desired files for improvement and provided an
      appropriate prompt before calling this function.
    - The function expects the files to be formatted in a specific way to be properly processed by the LLM.
    """

    """
    After the file list and prompt have been aquired, this function is called
    to sent the formatted prompt to the LLM.
    """

    files_info = get_code_strings(
        dbs.workspace, dbs.project_metadata
    )  # this has file names relative to the workspace path

    messages = [
        SystemMessage(content=setup_sys_prompt_existing_code(dbs)),
    ]
    # Add files as input
    for file_name, file_str in files_info.items():
        code_input = format_file_to_input(file_name, file_str)
        messages.append(HumanMessage(content=f"{code_input}"))

    messages.append(HumanMessage(content=f"Request: {dbs.input['prompt']}"))

    messages = ai.next(messages, step_name=curr_fn())

    overwrite_files_with_edits(messages[-1].content.strip(), dbs)
    return messages
