"""
Module for defining the steps involved in generating and improving code using AI.

This module provides functions that represent different steps in the process of generating
and improving code using an AI model. These steps include generating code from a prompt,
creating an entrypoint for the codebase, executing the entrypoint, and refining code edits.

Functions
---------
curr_fn : function
    Returns the name of the current function.

setup_sys_prompt : function
    Sets up the system prompt for generating code.

gen_code : function
    Generates code from a prompt using AI and returns the generated files.

gen_entrypoint : function
    Generates an entrypoint for the codebase and returns the entrypoint files.

execute_entrypoint : function
    Executes the entrypoint of the codebase.

setup_sys_prompt_existing_code : function
    Sets up the system prompt for improving existing code.


improve : function
    Improves the code based on user input and returns the updated files.
"""

import inspect
import re

from pathlib import Path
from typing import List, MutableMapping, Union

from langchain.schema import HumanMessage, SystemMessage
from termcolor import colored

from gpt_engineer.core.ai import AI
from gpt_engineer.core.base_execution_env import BaseExecutionEnv
from gpt_engineer.core.base_memory import BaseMemory
from gpt_engineer.core.chat_to_files import apply_diffs, chat_to_files_dict, parse_diffs
from gpt_engineer.core.default.constants import MAX_EDIT_REFINEMENT_STEPS
from gpt_engineer.core.default.paths import (
    CODE_GEN_LOG_FILE,
    ENTRYPOINT_FILE,
    ENTRYPOINT_LOG_FILE,
    IMPROVE_LOG_FILE,
)
from gpt_engineer.core.files_dict import FilesDict, file_to_lines_dict
from gpt_engineer.core.preprompts_holder import PrepromptsHolder


def curr_fn() -> str:
    """
    Returns the name of the current function.

    Returns
    -------
    str
        The name of the function that called this function.
    """
    return inspect.stack()[1].function


def setup_sys_prompt(preprompts: MutableMapping[Union[str, Path], str]) -> str:
    """
    Sets up the system prompt for generating code.

    Parameters
    ----------
    preprompts : MutableMapping[Union[str, Path], str]
        A mapping of preprompt messages to guide the AI model.

    Returns
    -------
    str
        The system prompt message for the AI model.
    """
    return (
        preprompts["roadmap"]
        + preprompts["generate"].replace("FILE_FORMAT", preprompts["file_format"])
        + "\nUseful to know:\n"
        + preprompts["philosophy"]
    )


def setup_sys_prompt_existing_code(
    preprompts: MutableMapping[Union[str, Path], str]
) -> str:
    """
    Sets up the system prompt for improving existing code.

    Parameters
    ----------
    preprompts : MutableMapping[Union[str, Path], str]
        A mapping of preprompt messages to guide the AI model.

    Returns
    -------
    str
        The system prompt message for the AI model to improve existing code.
    """
    return (
        preprompts["roadmap"]
        + preprompts["improve"].replace("FILE_FORMAT", preprompts["file_format_diff"])
        + "\nUseful to know:\n"
        + preprompts["philosophy"]
    )


def gen_code(
    ai: AI, prompt: str, memory: BaseMemory, preprompts_holder: PrepromptsHolder
) -> FilesDict:
    """
    Generates code from a prompt using AI and returns the generated files.

    Parameters
    ----------
    ai : AI
        The AI model used for generating code.
    prompt : str
        The user prompt to generate code from.
    memory : BaseMemory
        The memory interface where the code and related data are stored.
    preprompts_holder : PrepromptsHolder
        The holder for preprompt messages that guide the AI model.

    Returns
    -------
    FilesDict
        A dictionary of file names to their respective source code content.
    """
    preprompts = preprompts_holder.get_preprompts()
    messages = ai.start(setup_sys_prompt(preprompts), prompt, step_name=curr_fn())
    chat = messages[-1].content.strip()
    memory[CODE_GEN_LOG_FILE] = chat
    files_dict = chat_to_files_dict(chat)
    return files_dict


def gen_entrypoint(
    ai: AI,
    files_dict: FilesDict,
    memory: BaseMemory,
    preprompts_holder: PrepromptsHolder,
) -> FilesDict:
    """
    Generates an entrypoint for the codebase and returns the entrypoint files.

    Parameters
    ----------
    ai : AI
        The AI model used for generating the entrypoint.
    files_dict : FilesDict
        The dictionary of file names to their respective source code content.
    memory : BaseMemory
        The memory interface where the code and related data are stored.
    preprompts_holder : PrepromptsHolder
        The holder for preprompt messages that guide the AI model.

    Returns
    -------
    FilesDict
        A dictionary containing the entrypoint file.
    """
    preprompts = preprompts_holder.get_preprompts()
    messages = ai.start(
        system=(preprompts["entrypoint"]),
        user="Information about the codebase:\n\n" + files_dict.to_chat(),
        step_name=curr_fn(),
    )
    print()
    chat = messages[-1].content.strip()
    regex = r"```\S*\n(.+?)```"
    matches = re.finditer(regex, chat, re.DOTALL)
    entrypoint_code = FilesDict(
        {ENTRYPOINT_FILE: "\n".join(match.group(1) for match in matches)}
    )
    memory[ENTRYPOINT_LOG_FILE] = chat
    return entrypoint_code


def execute_entrypoint(
    ai: AI,
    execution_env: BaseExecutionEnv,
    files_dict: FilesDict,
    preprompts_holder: PrepromptsHolder = None,
) -> FilesDict:
    """
    Executes the entrypoint of the codebase.

    Parameters
    ----------
    ai : AI
        The AI model used for generating the entrypoint.
    execution_env : BaseExecutionEnv
        The execution environment in which the code is executed.
    files_dict : FilesDict
        The dictionary of file names to their respective source code content.
    preprompts_holder : PrepromptsHolder, optional
        The holder for preprompt messages that guide the AI model.

    Returns
    -------
    FilesDict
        The dictionary of file names to their respective source code content after execution.
    """
    if ENTRYPOINT_FILE not in files_dict:
        raise FileNotFoundError(
            "The required entrypoint "
            + ENTRYPOINT_FILE
            + " does not exist in the code."
        )

    command = files_dict[ENTRYPOINT_FILE]

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
    if input("").lower() not in ["", "y", "yes"]:
        print("Ok, not executing the code.")
        return files_dict
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

    execution_env.upload(files_dict).run(f"bash {ENTRYPOINT_FILE}")
    return files_dict


def improve(
    ai: AI,
    prompt: str,
    files_dict: FilesDict,
    memory: BaseMemory,
    preprompts_holder: PrepromptsHolder,
) -> FilesDict:
    """
    Improves the code based on user input and returns the updated files.

    Parameters
    ----------
    ai : AI
        The AI model used for improving code.
    prompt :str
        The user prompt to improve the code.
    files_dict : FilesDict
        The dictionary of file names to their respective source code content.
    memory : BaseMemory
        The memory interface where the code and related data are stored.
    preprompts_holder : PrepromptsHolder
        The holder for preprompt messages that guide the AI model.

    Returns
    -------
    FilesDict
        The dictionary of file names to their respective updated source code content.
    """
    preprompts = preprompts_holder.get_preprompts()
    messages = [
        SystemMessage(content=setup_sys_prompt_existing_code(preprompts)),
    ]

    # Add files as input
    messages.append(HumanMessage(content=f"{files_dict.to_chat()}"))
    messages.append(HumanMessage(content=f"Request: {prompt}"))
    return _improve_loop(ai, files_dict, memory, messages)


def _improve_loop(
    ai: AI, files_dict: FilesDict, memory: BaseMemory, messages: List
) -> FilesDict:
    problems = []
    # check edit correctness
    edit_refinements = 0
    while edit_refinements <= MAX_EDIT_REFINEMENT_STEPS:
        messages = ai.next(messages, step_name=curr_fn())
        files_dict = salvage_correct_hunks(messages, files_dict, memory, problems)

        if len(problems) > 0:
            messages.append(
                HumanMessage(
                    content="Some previously produced diffs were not on the requested format, or the code part was not found in the code. Details: "
                    + "\n".join(problems)
                    + "\n Please FOCUS ON the problematic diffs, making sure that the failing ones are now on the correct format and can be found in the code. Make sure to not repeat past mistakes. \n"
                )
            )
            messages = ai.next(messages, step_name=curr_fn())
            edit_refinements += 1
            files_dict = salvage_correct_hunks(messages, files_dict, memory, problems)
        return files_dict


def salvage_correct_hunks(
    messages: List,
    files_dict: FilesDict,
    memory: MutableMapping[str | Path, str],
    error_message: List,
) -> FilesDict:
    chat = messages[-1].content.strip()

    diffs = parse_diffs(chat)

    # validate and correct diffs

    for file_name, diff in diffs.items():
        # if diff is a new file, validation and correction is unnecessary
        if not diff.is_new_file():
            problems = diff.validate_and_correct(
                file_to_lines_dict(files_dict[diff.filename_pre])
            )
            error_message.extend(problems)
    files_dict = apply_diffs(diffs, files_dict)
    memory[IMPROVE_LOG_FILE] = chat
    return files_dict
