from gpt_engineer.core.code import Code
from gpt_engineer.core.ai import AI
from gpt_engineer.core.chat_to_files import parse_chat, overwrite_code_with_edits, parse_edits
from gpt_engineer.core.default.paths import (
    ENTRYPOINT_FILE,
    CODE_GEN_LOG_FILE,
    ENTRYPOINT_LOG_FILE,
    IMPROVE_LOG_FILE,
    PREPROMPTS_PATH,
)
from gpt_engineer.core.default.constants import MAX_EDIT_REFINEMENT_STEPS
from gpt_engineer.core.default.on_disk_repository import OnDiskRepository
from gpt_engineer.core.base_repository import BaseRepository
from gpt_engineer.core.base_execution_env import BaseExecutionEnv

from typing import Union, MutableMapping, List
from pathlib import Path
from langchain.schema import HumanMessage, SystemMessage
import inspect
import re
from termcolor import colored
from gpt_engineer.core.preprompt_holder import PrepromptHolder


def curr_fn() -> str:
    """
    Retrieves the name of the calling function.

    This utility function uses Python's inspection capabilities to dynamically fetch the
    name of the function that called `curr_fn()`. It is used for tracking and logging purposes.

    Returns:
        str: The name of the function that called `curr_fn()`.
    """
    return inspect.stack()[1].function


def setup_sys_prompt(preprompts: MutableMapping[Union[str, Path], str]) -> str:
    """
    Constructs a system prompt for the AI based on predefined instructions and philosophies.

    This function prepares a system prompt that guides the AI in generating code according to
    specific instructions and coding philosophies. It combines various components such as the
    roadmap, generate instructions, and coding philosophy from the provided repository.

    Parameters:
        preprompts (OnDiskRepository): The repository containing predefined prompts and instructions.

    Returns:
        str: The constructed system prompt for the AI.
    """
    return (
        preprompts["roadmap"]
        + preprompts["generate"].replace("FILE_FORMAT", preprompts["file_format"])
        + "\nUseful to know:\n"
        + preprompts["philosophy"]
    )


def gen_code(ai: AI, prompt: str, memory: BaseRepository, preprompts_path: Union[str, Path]) -> Code:
    """
    Generates code based on a given prompt using an AI model.

    This function uses the AI model to generate code from a given prompt. It sets up the system
    prompt, invokes the AI model, and then saves the generated output to memory. The generated
    code is also saved to disk.

    Parameters:
        ai (AI): The AI model used for code generation.
        prompt (str): The user prompt that describes what code to generate.
        memory (BaseRepository): The repository where the generated code and full output are saved.

    Returns:
        Code: A dictionary-like object containing the generated code files.
    """
    preprompts = PrepromptHolder.get_preprompts(preprompts_path)
    messages = ai.start(setup_sys_prompt(preprompts), prompt, step_name=curr_fn())
    chat = messages[-1].content.strip()
    memory[CODE_GEN_LOG_FILE] = chat
    files = parse_chat(chat)
    code = Code({key: val for key, val in files})
    return code


def gen_entrypoint(ai: AI, code: Code, memory: BaseRepository, preprompts_path: Union[str, Path]) -> Code:
    """
    Generates an entry point script for a given codebase.

    This function prompts the AI model to generate Unix terminal commands necessary for installing
    dependencies and running all parts of the codebase. The generated commands are saved to 'run.sh'
    and the interaction is logged.

    Parameters:
        ai (AI): The AI model used for generating the entry point script.
        code (Code): The codebase information used to generate the script.
        memory (BaseRepository): The repository where the interaction is logged.

    Returns:
        Code: A dictionary-like object containing the entry point script.
    """
    preprompts = PrepromptHolder.get_preprompts(preprompts_path)
    messages = ai.start(
        system=(preprompts["entrypoint"]),
        user="Information about the codebase:\n\n" + code.to_chat(),
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


def execute_entrypoint(ai: AI, execution_env: BaseExecutionEnv, code: Code) -> None:
    """
    Executes the entry point script in a given execution environment.

    This function handles user confirmation and execution of the 'run.sh' script. It ensures that
    the script exists in the code and then proceeds to execute it, allowing the user to interrupt
    the process if necessary.

    Parameters:
        execution_env (BaseExecutionEnv): The environment in which the script is executed.
        code (Code): The codebase containing the 'run.sh' script.

    Returns:
        None

    Parameters
    ----------
    ai
    """

    if not ENTRYPOINT_FILE in code:
        raise FileNotFoundError(
            "The required entrypoint " + ENTRYPOINT_FILE + " does not exist in the code."
        )

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


def setup_sys_prompt_existing_code(preprompts: MutableMapping[Union[str, Path], str]) -> str:
    """
    Constructs a system prompt for the AI to improve existing code.

    This function prepares a system prompt that instructs the AI on how to approach improving
    an existing codebase. It combines the "improve" instruction with the coding philosophy from
    the provided repository.

    Parameters:
        preprompts (OnDiskRepository): The repository containing predefined prompts and instructions.

    Returns:
        str: The constructed system prompt for code improvement.
    """
    return (
        preprompts["improve"].replace("FILE_FORMAT", preprompts["file_format"])
        + "\nUseful to know:\n"
        + preprompts["philosophy"]
    )


def incorrect_edit(code: Code, chat: str) -> List[str,]:
    problems = list()
    try:
        edits = parse_edits(chat)
    except ValueError as problem:
        print("Not possible to parse chat to edits")
        problems.append(str(problem))
    for edit in edits:
        if not edit.before in code[edit.filename]:
            problems.append("This section, assigned to be exchanged for an edit block, does not have an exact match in the code: " + edit.before + "\nThis is often a result of placeholders, such as ... or references to 'existing code' or 'rest of function' etc, which cannot be used the HEAD part of the edit blocks. Also, to get a match, all comments, including long doc strings may have to be reproduced in the patch HEAD")
    return problems



def improve(ai: AI, prompt: str, code: Code, memory: BaseRepository, preprompts_path: Union[str, Path]) -> Code:
    """
    Improves existing code based on user input using an AI model.

    This function processes and enhances the code from a set of existing files based on a user
    prompt. It formats the code for the AI model, sends it for processing, and then applies the
    improvements to the original files.

    Parameters:
        ai (AI): The AI model used for code improvement.
        prompt (str): The user prompt detailing the desired code improvements.
        code (Code): The existing codebase to be improved.
        memory (BaseRepository): The repository where the improvement process is logged.

    Returns:
        Code: A dictionary-like object containing the improved code files.
    """
    preprompts = PrepromptHolder.get_preprompts(preprompts_path)
    messages = [
        SystemMessage(content=setup_sys_prompt_existing_code(preprompts)),
    ]
    # Add files as input
    messages.append(HumanMessage(content=f"{code.to_chat()}"))
    messages.append(HumanMessage(content=f"Request: {prompt}"))
    problems = [""]
    # check edit correctness
    edit_refinements = 0
    while len(problems) > 0 and edit_refinements <= MAX_EDIT_REFINEMENT_STEPS:
        messages = ai.next(messages, step_name=curr_fn())
        chat = messages[-1].content.strip()
        problems = incorrect_edit(code, chat)
        if len(problems) > 0:
            messages.append(HumanMessage(content=f"Some previously produced edits were not on the requested format, or the HEAD part was not found in the code. Details: " + "\n".join(problems) + "\n Please provide ALL the edits again, making sure that the failing ones are now on the correct format and can be found in the code. Make sure to not repeat past mistakes. \n"))
        edit_refinements += 1
    overwrite_code_with_edits(chat, code)
    memory[IMPROVE_LOG_FILE] = chat
    return code
