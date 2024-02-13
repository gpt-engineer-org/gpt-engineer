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

incorrect_edit : function
    Identifies incorrect edits in the generated code.

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
from gpt_engineer.core.chat_to_files import (
    chat_to_files_dict,
    overwrite_code_with_edits,
    parse_edits,
)
from gpt_engineer.core.default.constants import MAX_EDIT_REFINEMENT_STEPS
from gpt_engineer.core.default.paths import (
    CODE_GEN_LOG_FILE,
    ENTRYPOINT_FILE,
    ENTRYPOINT_LOG_FILE,
    IMPROVE_LOG_FILE,
)
from gpt_engineer.core.files_dict import FilesDict
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
        preprompts["improve"].replace("FILE_FORMAT", preprompts["file_format"])
        + "\nUseful to know:\n"
        + preprompts["philosophy"]
    )


def incorrect_edit(files_dict: FilesDict, chat: str) -> List[str,]:
    """
    Identifies incorrect edits in the generated code.

    Parameters
    ----------
    files_dict : FilesDict
        The dictionary of file names to their respective source code content.
    chat : str
        The chat content containing the edits.

    Returns
    -------
    List[str]
        A list of problems identified in the edits.
    """
    problems = []
    try:
        edits = parse_edits(chat)
    except ValueError as problem:
        print("Not possible to parse chat to edits")
        problems.append(str(problem))
        return problems

    for edit in edits:
        # only trigger for existing files
        if edit.filename in files_dict:
            if edit.before not in files_dict[edit.filename]:
                problems.append(
                    "This section, assigned to be exchanged for an edit block, does not have an exact match in the code: "
                    + edit.before
                    + "\nThis is often a result of placeholders, such as ... or references to 'existing code' or 'rest of function' etc, which cannot be used the HEAD part of the edit blocks. Also, to get a match, all comments, including long doc strings may have to be reproduced in the patch HEAD"
                )
    return problems


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
    prompt : str
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
    problems = [""]

    # check edit correctness
    edit_refinements = 0
    while len(problems) > 0 and edit_refinements <= MAX_EDIT_REFINEMENT_STEPS:
        messages = ai.next(messages, step_name=curr_fn())
        chat = messages[-1].content.strip()
        problems = incorrect_edit(files_dict, chat)
        if len(problems) > 0:
            messages.append(
                HumanMessage(
                    content="Some previously produced edits were not on the requested format, or the HEAD part was not found in the code. Details: "
                    + "\n".join(problems)
                    + "\n Please provide ALL the edits again, making sure that the failing ones are now on the correct format and can be found in the code. Make sure to not repeat past mistakes. \n"
                )
            )
        edit_refinements += 1
    overwrite_code_with_edits(chat, files_dict)
    memory[IMPROVE_LOG_FILE] = chat
    return files_dict
