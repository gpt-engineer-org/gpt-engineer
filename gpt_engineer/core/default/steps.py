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

_apply_morph_edit : function
    Send code editing instructions to Morph API and return the merged code.
"""

import inspect
import io
import re
import sys
import traceback
import json
import os
from openai import OpenAI


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
    DEBUG_LOG_FILE,
    DIFF_LOG_FILE,
    ENTRYPOINT_FILE,
    ENTRYPOINT_LOG_FILE,
    IMPROVE_LOG_FILE,
)
from gpt_engineer.core.files_dict import FilesDict, file_to_lines_dict
from gpt_engineer.core.preprompts_holder import PrepromptsHolder
from gpt_engineer.core.prompt import Prompt


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
    preprompts: MutableMapping[Union[str, Path], str],
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
    ai: AI, prompt: Prompt, memory: BaseMemory, preprompts_holder: PrepromptsHolder
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
    messages = ai.start(
        setup_sys_prompt(preprompts), prompt.to_langchain_content(), step_name=curr_fn()
    )
    chat = messages[-1].content.strip()
    memory.log(CODE_GEN_LOG_FILE, "\n\n".join(x.pretty_repr() for x in messages))
    files_dict = chat_to_files_dict(chat)
    return files_dict


def gen_entrypoint(
    ai: AI,
    prompt: Prompt,
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
    user_prompt = prompt.entrypoint_prompt
    if not user_prompt:
        user_prompt = """
        Make a unix script that
        a) installs dependencies
        b) runs all necessary parts of the codebase (in parallel if necessary)
        """
    preprompts = preprompts_holder.get_preprompts()
    messages = ai.start(
        system=(preprompts["entrypoint"]),
        user=user_prompt
        + "\nInformation about the codebase:\n\n"
        + files_dict.to_chat(),
        step_name=curr_fn(),
    )
    print()
    chat = messages[-1].content.strip()
    regex = r"```\S*\n(.+?)```"
    matches = re.finditer(regex, chat, re.DOTALL)
    entrypoint_code = FilesDict(
        {ENTRYPOINT_FILE: "\n".join(match.group(1) for match in matches)}
    )
    memory.log(ENTRYPOINT_LOG_FILE, "\n\n".join(x.pretty_repr() for x in messages))
    return entrypoint_code


def execute_entrypoint(
    ai: AI,
    execution_env: BaseExecutionEnv,
    files_dict: FilesDict,
    prompt: Prompt = None,
    preprompts_holder: PrepromptsHolder = None,
    memory: BaseMemory = None,
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


def apply_morph_edit(instructions: str, initial_code: str, code_edit: str) -> str:
    """
    Send code editing instructions to Morph API and return the merged code.

    Args:
        instructions (str): The instructions for the edit.
        initial_code (str): The original code to modify.
        code_edit (str): The proposed code changes.

    Returns:
        str: The merged/edited code returned by Morph, or the original code if an error occurs.
    """
    api_key = os.getenv("MORPH_API_KEY")
    if not api_key:
        print("Error: MORPH_API_KEY not set.")
        return initial_code

    client = OpenAI(api_key=api_key, base_url="https://api.morphllm.com/v1")

    try:
        response = client.chat.completions.create(
            model="morph-v3-large",
            messages=[
                {
                    "role": "user",
                    "content": f"<instruction>{instructions}</instruction>\n<code>{initial_code}</code>\n<update>{code_edit}</update>",
                }
            ],
        )
        merged_code = response.choices[0].message.content
        if not merged_code:
            print("Warning: Morph returned empty content. Using original code.")
            return initial_code
        return merged_code

    except Exception as e:
        print(f"Unexpected error applying Morph edit: {e}")
        return initial_code


def improve_fn(
    ai: AI,
    prompt: Prompt,
    files_dict: FilesDict,
    memory: BaseMemory,
    preprompts_holder: PrepromptsHolder,
    diff_timeout=3,
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
    messages.append(HumanMessage(content=prompt.to_langchain_content()))
    memory.log(
        DEBUG_LOG_FILE,
        "UPLOADED FILES:\n" + files_dict.to_log() + "\nPROMPT:\n" + prompt.text,
    )
    return _improve_loop(ai, files_dict, memory, messages, diff_timeout=diff_timeout)


def _improve_loop(
    ai: AI, files_dict: FilesDict, memory: BaseMemory, messages: List, diff_timeout=3
) -> FilesDict:
    messages = ai.next(messages, step_name=curr_fn())
    # Log AI raw response
    ai_response = messages[-1].content.strip()

    try:
        data = json.loads(ai_response)
    except json.JSONDecodeError as e:
        # Log the error and the response for debugging
        print(f"Failed to parse AI response as JSON: {e}")
        print("AI response:", ai_response)
        return files_dict  # Return the original files_dict unchanged

    for file in data:
        if file["target_file"] not in files_dict:
            files_dict[file["target_file"]] = file["code_edit"]
        else:
            # Use Morph to apply the edit
            merged_code = apply_morph_edit(
                instructions=file["instructions"],
                initial_code=files_dict[file["target_file"]],
                code_edit=file["code_edit"],
            )
            files_dict[file["target_file"]] = merged_code

    return files_dict


class Tee(object):
    def __init__(self, *files):
        self.files = files

    def write(self, obj):
        for file in self.files:
            file.write(obj)

    def flush(self):
        for file in self.files:
            file.flush()


def handle_improve_mode(prompt, agent, memory, files_dict, diff_timeout=3):
    captured_output = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = Tee(sys.stdout, captured_output)

    try:
        files_dict = agent.improve(files_dict, prompt, diff_timeout=diff_timeout)
    except Exception as e:
        print(
            f"Error while improving the project: {e}\nCould you please upload the debug_log_file.txt in {memory.path}/logs folder to github?\nFULL STACK TRACE:\n"
        )
        traceback.print_exc(file=sys.stdout)  # Print the full stack trace
    finally:
        # Reset stdout
        sys.stdout = old_stdout

        # Get the captured output
        captured_string = captured_output.getvalue()
        print(captured_string)
        memory.log(DEBUG_LOG_FILE, "\nCONSOLE OUTPUT:\n" + captured_string)

    return files_dict
