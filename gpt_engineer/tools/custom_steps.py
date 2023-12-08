from termcolor import colored
from typing import List, Union
from platform import platform
from sys import version_info
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from gpt_engineer.core.ai import AI
from gpt_engineer.core.preprompts_holder import PrepromptsHolder
from gpt_engineer.core.base_memory import BaseMemory
from gpt_engineer.core.default.paths import (
    ENTRYPOINT_FILE,
    CODE_GEN_LOG_FILE,
)
from gpt_engineer.core.default.steps import (
    curr_fn,
    setup_sys_prompt,
)
from gpt_engineer.core.chat_to_files import chat_to_files_dict
from gpt_engineer.core.files_dict import FilesDict
from gpt_engineer.core.base_execution_env import BaseExecutionEnv

# Type hint for chat messages
Message = Union[AIMessage, HumanMessage, SystemMessage]
MAX_SELF_HEAL_ATTEMPTS = 2


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


def self_heal(
    ai: AI,
    execution_env: BaseExecutionEnv,
    files_dict: FilesDict,
    preprompts_holder: PrepromptsHolder = None,
) -> FilesDict:
    """Attempts to execute the code from the entrypoint and if it fails,
    sends the error output back to the AI with instructions to fix.
    This code will make `MAX_SELF_HEAL_ATTEMPTS` to try and fix the code
    before giving up.
    This makes the assuption that the previous step was `gen_entrypoint`,
    this code could work with `simple_gen`, or `gen_clarified_code` as well.
    """

    # step 1. execute the entrypoint
    # log_path = dbs.workspace.path / "log.txt"
    if not ENTRYPOINT_FILE in files_dict:
        raise FileNotFoundError(
            "The required entrypoint " + ENTRYPOINT_FILE + " does not exist in the code."
        )

    attempts = 0
    messages = []
    if preprompts_holder is None:
        raise AssertionError("Prepromptsholder required for self-heal")
    preprompts = preprompts_holder.get_preprompts()
    while attempts < MAX_SELF_HEAL_ATTEMPTS:
        command = files_dict[ENTRYPOINT_FILE]
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
            return files_dict
        print("Executing the code...")
        stdout_full, stderr_full, returncode = execution_env.upload(files_dict).run(
            f"bash {ENTRYPOINT_FILE}"
        )
        # get the result and output
        # step 2. if the return code not 0, package and send to the AI
        if returncode != 0:
            print("run.sh failed.  Let's fix it.")

            # pack results in an AI prompt

            # Using the log from the previous step has all the code and
            # the gen_entrypoint prompt inside.
            if attempts < 1:
                messages: List[Message] = [SystemMessage(content=files_dict.to_chat())]
                messages.append(SystemMessage(content=get_platform_info()))

            messages.append(SystemMessage(content=stdout_full + "\n " + stderr_full))

            messages = ai.next(
                messages, preprompts["file_format_fix"], step_name=curr_fn()
            )
        else:  # the process did not fail, we are done here.
            return files_dict

        files_dict = {**files_dict, **chat_to_files_dict(messages[-1].content.strip())}
        attempts += 1

    return files_dict


def clarified_gen(
    ai: AI, prompt: str, memory: BaseMemory, preprompts_holder: PrepromptsHolder
) -> FilesDict:
    """
    Generates code based on clarifications obtained from the user.

    This function processes the messages logged during the user's clarification session
    and uses them, along with the system's prompts, to guide the AI in generating code.
    The generated code is saved to a specified workspace.

    Parameters:
    - ai (AI): An instance of the AI model, responsible for processing and generating the code.
    - dbs (DBs): An instance containing the database configurations, which includes system
      and input prompts.

    Returns:
    - List[dict]: A list of message dictionaries capturing the AI's interactions and generated
      outputs during the code generation process.
    """
    preprompts = preprompts_holder.get_preprompts()
    messages: List[Message] = [SystemMessage(content=preprompts["clarify"])]
    user_input = prompt
    while True:
        messages = ai.next(messages, user_input, step_name=curr_fn())
        msg = messages[-1].content.strip()

        if "nothing to clarify" in msg.lower():
            break

        if msg.lower().startswith("no"):
            print("Nothing to clarify.")
            break

        print('(answer in text, or "c" to move on)\n')
        user_input = input()
        print()

        if not user_input or user_input == "c":
            print("(letting gpt-engineer make its own assumptions)")
            print()
            messages = ai.next(
                messages,
                "Make your own assumptions and state them explicitly before starting",
                step_name=curr_fn(),
            )
            print()

        user_input += """
            \n\n
            Is anything else unclear? If yes, ask another question.\n
            Otherwise state: "Nothing to clarify"
            """

    print()

    messages = [
        SystemMessage(content=setup_sys_prompt(preprompts)),
    ] + messages[
        1:
    ]  # skip the first clarify message, which was the original clarify priming prompt
    messages = ai.next(
        messages,
        preprompts["generate"].replace("FILE_FORMAT", preprompts["file_format"]),
        step_name=curr_fn(),
    )
    print()
    chat = messages[-1].content.strip()
    memory[CODE_GEN_LOG_FILE] = chat
    files_dict = chat_to_files_dict(chat)
    return files_dict


def lite_gen(
    ai: AI, prompt: str, memory: BaseMemory, preprompts_holder: PrepromptsHolder
) -> FilesDict:
    """
    Executes the AI model using the main prompt and saves the generated results.

    This function invokes the AI model by feeding it the main prompt. After the
    AI processes and generates the output, the function saves this output to the
    specified workspace. The AI's output is also tracked using the current function's
    name to provide context.

    Parameters:
    - ai (AI): An instance of the AI model.
    - dbs (DBs): An instance containing the database configurations, including input prompts
      and file formatting preferences.

    Returns:
    - List[Message]: A list of message objects encapsulating the AI's output.

    Note:
    The function assumes the `ai.start` method and the `to_files` utility to be correctly
    set up and functional. Ensure these prerequisites before invoking `lite_gen`.
    """
    preprompts = preprompts_holder.get_preprompts()
    messages = ai.start(prompt, preprompts["file_format"], step_name=curr_fn())
    chat = messages[-1].content.strip()
    memory[CODE_GEN_LOG_FILE] = chat
    files_dict = chat_to_files_dict(chat)
    return files_dict
