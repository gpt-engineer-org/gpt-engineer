"""
GPT Engineer workflow definition and execution

This module provides the necessary utilities and functions to orchestrate the execution of GPT-engineer's tasks
related to code generation, execution, and review. It leverages a flexible approach to system prompt creation,
workflow execution, and interaction with AI, allowing for various configurations and stages of operation.

Imports:
- Standard libraries: inspect, re, subprocess
- Additional libraries/packages: termcolor, typing, enum
- Internal modules/packages: langchain.schema, gpt_engineer.core, gpt_engineer.cli

Key Features:
- Dynamic system prompt creation for both new code generation and improving existing code.
- A series of utility functions for handling various tasks like AI code generation, user clarification,
  code execution, and human review.
- Configurable workflow steps to control the process of code generation and execution in different scenarios.
- Flexibility to adapt to different configurations and use cases.

Classes:
- Config: An enumeration representing different configurations or operation modes for the workflow.

Functions:
- setup_sys_prompt(dbs: FileRepositories) -> str: Creates a system prompt for the AI.
- setup_sys_prompt_existing_code(dbs: FileRepositories) -> str: System prompt creation using existing code base.
- curr_fn() -> str: Returns the name of the current function.
- lite_gen(ai: AI, dbs: FileRepositories) -> List[Message]: Runs the AI on the main prompt and saves results.
- simple_gen(ai: AI, dbs: FileRepositories) -> List[Message]: Runs the AI on default prompts and saves results.
- clarify(ai: AI, dbs: FileRepositories) -> List[Message]: Interacts with the user for clarification.
- gen_clarified_code(ai: AI, dbs: FileRepositories) -> List[dict]: Generates code after clarification.
- execute_entrypoint(ai: AI, dbs: FileRepositories) -> List[dict]: Executes code entry point and asks user for confirmation.
- gen_entrypoint(ai: AI, dbs: FileRepositories) -> List[dict]: Generates entry point based on information about a codebase.
- use_feedback(ai: AI, dbs: FileRepositories): Uses feedback from users to improve code.
- set_improve_filelist(ai: AI, dbs: FileRepositories): Sets the file list for existing code improvements.
- assert_files_ready(ai: AI, dbs: FileRepositories): Checks for the required files for code improvement.
- get_improve_prompt(ai: AI, dbs: FileRepositories): Interacts with the user to know what they want to fix in existing code.
- improve_existing_code(ai: AI, dbs: FileRepositories): Generates improved code after getting the file list and user prompt.
- human_review(ai: AI, dbs: FileRepositories): Collects and stores human review of the generated code.

Constants:
- STEPS: A dictionary that maps the Config enum to lists of functions to execute for each configuration.

Note:
- This module is central to the GPT-engineer system and its functions are intended to be used in orchestrated
  workflows. As such, it should be used carefully, with attention to the correct order and sequence of operations.
"""

import inspect

from enum import Enum
from platform import platform
from sys import version_info
from typing import List, Union

from langchain.schema import AIMessage, HumanMessage, SystemMessage

from gpt_engineer.core.ai import AI
from gpt_engineer.core.default.on_disk_repository import FileRepositories
from gpt_engineer.tools.custom_steps import self_heal, vector_improve, gen_clarified_code, clarify, lite_gen

MAX_SELF_HEAL_ATTEMPTS = 2  # constants for self healing code
ASSUME_WORKING_TIMEOUT = 30

# Type hint for chat messages
Message = Union[AIMessage, HumanMessage, SystemMessage]


def get_platform_info():
    """Returns the Platform: OS, and the Python version.
    This is used for self healing.  There are some possible areas of conflict here if
    you use a different version of Python in your virtualenv.  A better solution would
    be to have this info printed from the virtualenv.
    """
    v = version_info
    a = f"Python Version: {v.major}.{v.minor}.{v.micro}"
    b = f"\nOS: {platform()}\n"
    return a + b


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


def simple_gen(ai: AI, dbs: FileRepositories) -> List[Message]:
    """
    Executes the AI model using the default system prompts and saves the output.

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
    messages = ai.start(setup_sys_prompt(dbs), dbs.input["prompt"], step_name=curr_fn())
    to_files_and_memory(messages[-1].content.strip(), dbs)
    return messages


def use_feedback(ai: AI, dbs: FileRepositories):
    """
    Uses the provided feedback to improve the generated code.

    This function takes in user feedback and applies it to modify previously
    generated code. If feedback is available, the AI model is primed with the
    system prompt and user instructions and then proceeds to process the feedback.
    The modified code is then saved back to the workspace. If feedback is not found,
    the user is informed to provide a 'feedback' file in the appropriate directory.

    Parameters:
    - ai (AI): An instance of the AI model.
    - dbs (DBs): An instance containing the database configurations and workspace
      information, particularly the 'all_output.txt' which contains the previously
      generated code, and 'input' which may contain the feedback from the user.

    Notes:
    - The function assumes the feedback will be found in 'dbs.input["feedback"]'.
    - If feedback is provided, the AI processes it and the resulting code is saved
      back to the workspace.
    - If feedback is absent, an instruction is printed to the console, and the program
      terminates.
    """
    messages = [
        SystemMessage(content=setup_sys_prompt(dbs)),
        HumanMessage(content=f"Instructions: {dbs.input['prompt']}"),
        AIMessage(
            content=dbs.memory["all_output.txt"]
        ),  # reload previously generated code
    ]
    if dbs.input["feedback"]:
        messages = ai.next(messages, dbs.input["feedback"], step_name=curr_fn())
        to_files_and_memory(messages[-1].content.strip(), dbs)
        return messages
    else:
        print(
            "No feedback was found in the input folder. Please create a file "
            + "called 'feedback' in the same folder as the prompt file."
        )
        exit(1)


def assert_files_ready(ai: AI, dbs: FileRepositories):
    """
    Verify the presence of required files for headless 'improve code' execution.

    This function checks the existence of 'file_list.txt' in the project metadata
    and the presence of a 'prompt' in the input. If either of these checks fails,
    an assertion error is raised to alert the user of the missing requirements.

    Parameters:
    - ai (AI): An instance of the AI model. Although passed to this function, it is
      not used within the function scope and might be for consistency with other
      function signatures.
    - dbs (DBs): An instance containing the database configurations and project metadata,
      which is used to validate the required files' presence.

    Returns:
    - list: Returns an empty list, which can be utilized for consistency in return
      types across related functions.

    Raises:
    - AssertionError: If 'file_list.txt' is not present in the project metadata
      or if 'prompt' is not present in the input.

    Notes:
    - This function is typically used in 'auto_mode' scenarios to ensure that the
      necessary files are set up correctly before proceeding with the 'improve code'
      operation.
    """
    """Checks that the required files are present for headless
    improve code execution."""
    assert (
        "file_list.txt" in dbs.project_metadata
    ), "For auto_mode file_list.txt need to be in your .gpteng folder."
    assert "prompt" in dbs.input, "For auto_mode a prompt file must exist."
    return []


class Config(str, Enum):
    """
    Enumeration representing different configuration modes for the code processing system.

    Members:
    - DEFAULT: Standard procedure for generating, executing, and reviewing code.
    - BENCHMARK: Used for benchmarking the system's performance without execution.
    - SIMPLE: A basic procedure involving generation, execution, and review.
    - LITE: A lightweight procedure for generating code without further processing.
    - CLARIFY: Process that starts with clarifying ambiguities before code generation.
    - EXECUTE_ONLY: Only executes the code without generation.
    - EVALUATE: Execute the code and then undergo a human review.
    - USE_FEEDBACK: Uses prior feedback for code generation and subsequent steps.
    - IMPROVE_CODE: Focuses on improving existing code based on a provided prompt.
    - EVAL_IMPROVE_CODE: Validates files and improves existing code.
    - EVAL_NEW_CODE: Evaluates newly generated code without further steps.

    Each configuration mode dictates the sequence and type of operations performed on the code.
    """

    DEFAULT = "default"
    BENCHMARK = "benchmark"
    SIMPLE = "simple"
    LITE = "lite"
    CLARIFY = "clarify"
    EXECUTE_ONLY = "execute_only"
    EVALUATE = "evaluate"
    USE_FEEDBACK = "use_feedback"
    IMPROVE_CODE = "improve_code"
    EVAL_IMPROVE_CODE = "eval_improve_code"
    EVAL_NEW_CODE = "eval_new_code"
    VECTOR_IMPROVE = "vector_improve"
    SELF_HEAL = "self_heal"


STEPS = {
    Config.DEFAULT: [
        simple_gen,
        gen_entrypoint,
        execute_entrypoint,
        human_review,
    ],
    Config.LITE: [
        lite_gen,
    ],
    Config.CLARIFY: [
        clarify,
        gen_clarified_code,
        gen_entrypoint,
        execute_entrypoint,
        human_review,
    ],
    Config.BENCHMARK: [
        simple_gen,
        gen_entrypoint,
    ],
    Config.SIMPLE: [
        simple_gen,
        gen_entrypoint,
        execute_entrypoint,
    ],
    Config.USE_FEEDBACK: [use_feedback, gen_entrypoint, execute_entrypoint, human_review],
    Config.EXECUTE_ONLY: [execute_entrypoint],
    Config.EVALUATE: [execute_entrypoint, human_review],
    Config.IMPROVE_CODE: [
        set_improve_filelist,
        get_improve_prompt,
        improve_existing_code,
    ],
    Config.VECTOR_IMPROVE: [vector_improve],
    Config.EVAL_IMPROVE_CODE: [assert_files_ready, improve_existing_code],
    Config.EVAL_NEW_CODE: [simple_gen],
    Config.SELF_HEAL: [self_heal],
}
"""
A dictionary mapping Config modes to a list of associated processing steps.

The STEPS dictionary dictates the sequence of functions or operations to be
performed based on the selected configuration mode from the Config enumeration.
This enables a flexible system where the user can select the desired mode and
the system can execute the corresponding steps in sequence.

Examples:
- For Config.DEFAULT, the system will first generate the code using `simple_gen`,
  then generate the entry point with `gen_entrypoint`, execute the generated
  code using `execute_entrypoint`, and finally collect human review using `human_review`.
- For Config.LITE, the system will only use the `lite_gen` function to generate the code.

This setup allows for modularity and flexibility in handling different user requirements and scenarios.
"""

# Future steps that can be added:
# run_tests_and_fix_files
# execute_entrypoint_and_fix_files_if_it_results_in_error
