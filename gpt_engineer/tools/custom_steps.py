import subprocess
from pathlib import Path
from typing import List, Union
from platform import platform
from sys import version_info
from langchain.schema import SystemMessage, HumanMessage, AIMessage

from gpt_engineer.core.ai import AI
from gpt_engineer.core.prepromt_holder import PrepromptHolder
from gpt_engineer.core.default.on_disk_repository import OnDiskRepository
from gpt_engineer.core.base_repository import BaseRepository
from gpt_engineer.core.default.paths import (
    ENTRYPOINT_FILE,
    CODE_GEN_LOG_FILE,
    ENTRYPOINT_LOG_FILE,
    IMPROVE_LOG_FILE,
)
from gpt_engineer.core.default.steps import curr_fn, setup_sys_prompt
from gpt_engineer.core.chat_to_files import parse_chat
from gpt_engineer.core.code import Code
from gpt_engineer.core.base_execution_env import BaseExecutionEnv
from gpt_engineer.tools.code_vector_repository import CodeVectorRepository

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


def self_heal(ai: AI, execution_env: BaseExecutionEnv, code: Code) -> Code:
    """Attempts to execute the code from the entrypoint and if it fails,
    sends the error output back to the AI with instructions to fix.
    This code will make `MAX_SELF_HEAL_ATTEMPTS` to try and fix the code
    before giving up.
    This makes the assuption that the previous step was `gen_entrypoint`,
    this code could work with `simple_gen`, or `gen_clarified_code` as well.
    """

    # step 1. execute the entrypoint
    # log_path = dbs.workspace.path / "log.txt"

    attempts = 0
    messages = []
    preprompts = PrepromptHolder.get_preprompts()
    while attempts < MAX_SELF_HEAL_ATTEMPTS:
        # log_file = open(log_path, "w")  # wipe clean on every iteration
        # timed_out = False

        # p = subprocess.Popen(  # attempt to run the entrypoint
        #     "bash run.sh",
        #     shell=True,
        #     cwd=dbs.workspace.path,
        #     stdout=log_file,
        #     stderr=log_file,
        #     bufsize=0,
        # )
        # try:  # timeout if the process actually runs
        #     p.wait(timeout=ASSUME_WORKING_TIMEOUT)
        # except subprocess.TimeoutExpired:
        #     timed_out = True
        #     print("The process hit a timeout before exiting.")
        process = execution_env.execute_program(code)
        # get the result and output
        # step 2. if the return code not 0, package and send to the AI
        if process.returncode != 0:
            print("run.sh failed.  Let's fix it.")

            # pack results in an AI prompt

            # Using the log from the previous step has all the code and
            # the gen_entrypoint prompt inside.
            if attempts < 1:
                messages: List[Message] = [SystemMessage(content=code.to_chat())]
                # messages.append(ai.fuser(get_platform_info()))  # add in OS and Py version WHAT IS ai.fuser()???
                messages.append(SystemMessage(content=get_platform_info()))
                # append the error message
            # Wait for the process to terminate and get stdout and stderr
            stdout, stderr = process.communicate()

            # stdout and stderr are bytes, decode them to string if needed
            output = stdout.decode("utf-8")
            error = stderr.decode("utf-8")
            messages.append(SystemMessage(content=output + "\n " + error))

            messages = ai.next(
                messages, preprompts["file_format_fix"], step_name=curr_fn()
            )
        else:  # the process did not fail, we are done here.
            return code

        # log_file.close()

        # this overwrites the existing files
        # to_files_and_memory(messages[-1].content.strip(), dbs)
        files = parse_chat(messages[-1].content.strip())
        code = Code({key: val for key, val in files})
        attempts += 1

    return code


# Todo: Adapt to refactor and code object
# def vector_improve(ai: AI, dbs: OnDiskRepository):
#     code_vector_repository = CodeVectorRepository()
#     code_vector_repository.load_from_directory(dbs.workspace.path)
#     releventDocuments = code_vector_repository.relevent_code_chunks(dbs.input["prompt"])
#
#     code_file_list = f"Here is a list of all the existing code files present in the root directory your code will be added to:"
#     code_file_list += "\n {fileRepositories.workspace.to_path_list_string()}"
#
#     relevent_file_contents = f"Here are files relevent to the query which you may like to change, reference or add to \n"
#
#     for doc in releventDocuments:
#         filename_without_path = Path(doc.metadata["filename"]).name
#         file_content = dbs.workspace[filename_without_path]
#         relevent_file_contents += format_file_to_input(
#             filename_without_path, file_content
#         )
#
#     messages = [
#         SystemMessage(content=setup_sys_prompt_existing_code(dbs)),
#     ]
#
#     messages.append(HumanMessage(content=f"{code_file_list}"))
#     messages.append(HumanMessage(content=f"{relevent_file_contents}"))
#     messages.append(HumanMessage(content=f"Request: {dbs.input['prompt']}"))
#
#     messages = ai.next(messages, step_name=curr_fn())
#
#     overwrite_code_with_edits(messages[-1].content.strip(), dbs)
#     return messages


def gen_clarified_code(ai: AI, prompt: str, memory: BaseRepository) -> Code:
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
    preprompts = PrepromptHolder.get_preprompts()
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

        print()
        user_input = input('(answer in text, or "c" to move on)\n')
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

    chat = messages[-1].content.strip()
    memory[CODE_GEN_LOG_FILE] = chat
    files = parse_chat(chat)
    code = Code({key: val for key, val in files})
    return code


def lite_gen(ai: AI, prompt: str, memory: BaseRepository) -> Code:
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
    preprompts = PrepromptHolder.get_preprompts()
    messages = ai.start(prompt, preprompts["file_format"], step_name=curr_fn())
    chat = messages[-1].content.strip()
    memory[CODE_GEN_LOG_FILE] = chat
    files = parse_chat(chat)
    code = Code({key: val for key, val in files})
    return code
