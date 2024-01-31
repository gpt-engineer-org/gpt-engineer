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
    parse_diffs,
    apply_diffs,
)
from gpt_engineer.core.diff import is_similar
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
    return inspect.stack()[1].function


def setup_sys_prompt(preprompts: MutableMapping[Union[str, Path], str]) -> str:
    return (
        preprompts["roadmap"]
        + preprompts["generate"].replace("FILE_FORMAT", preprompts["file_format"])
        + "\nUseful to know:\n"
        + preprompts["philosophy"]
    )


def gen_code(
    ai: AI, prompt: str, memory: BaseMemory, preprompts_holder: PrepromptsHolder
) -> FilesDict:
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
    return (
        preprompts["improve"].replace("FILE_FORMAT", preprompts["file_format"])
        + "\nUseful to know:\n"
        + preprompts["philosophy"]
    )


def improve(
    ai: AI,
    prompt: str,
    files_dict: FilesDict,
    memory: BaseMemory,
    preprompts_holder: PrepromptsHolder,
) -> FilesDict:
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
        try:
            diffs = parse_diffs(chat)
            for file_name, diff in diffs.items():
                # if diff is a new file, validation and correction is unnecessary
                # ToDo: ALSO correct diff numbers for new files
                if not diff.is_new_file():
                    diff.validate_and_correct(
                        file_to_lines_dict(files_dict[diff.filename_pre])
                    )
            files_dict = apply_diffs(diffs, files_dict)
            memory[IMPROVE_LOG_FILE] = chat
            return files_dict
        except ValueError as error:
            # here we pray that we have given sufficient information in the exception.
            problems.append(str(error))
            if len(problems) > 0:
                messages.append(
                    HumanMessage(
                        content="Some previously produced edits were not on the requested format, or the HEAD part was not found in the code. Details: "
                        + "\n".join(problems)
                        + "\n Please provide ALL the edits again, making sure that the failing ones are now on the correct format and can be found in the code. Make sure to not repeat past mistakes. \n"
                    )
                )
            edit_refinements += 1

    memory[IMPROVE_LOG_FILE] = chat
    print("WARNING: Failed to parse and apply the edits")
    return files_dict
