import re
import subprocess

from enum import Enum
from typing import Callable, Dict, List

from gpt_engineer.ai import AI
from gpt_engineer.chat_to_files import to_files
from gpt_engineer.db import DBs
from gpt_engineer.models import Message, Messages, Role


def setup_sys_prompt(dbs: DBs) -> str:
    """Constructs the system setup prompt."""
    return dbs.identity["generate"] + "\nUseful to know:\n" + dbs.identity["philosophy"]


### Steps


def clarify(ai: AI, dbs: DBs) -> Messages:
    """
    Ask the user if they want to clarify anything and save the results to the workspace.
    """
    user_msg = dbs.input["main_prompt"]
    messages = Messages([Message(role=Role.SYSTEM, content=dbs.identity["qa"])])
    while True:
        messages = ai.next(messages=messages, user_prompt=user_msg)

        response_content: str = messages.last_message_content()
        if response_content.strip().lower().startswith("no"):
            break

        print()
        user_msg = input('(answer in text, or "c" to move on)\n')
        print()

        if not user_msg or user_msg == "c":
            break

        user_msg += (
            "\n\n"
            "Is anything else unclear? If yes, only answer in the form:\n"
            "{remaining unclear areas} remaining questions.\n"
            "{Next question}\n"
            'If everything is sufficiently clear, only answer "no".'
        )
    print()
    return messages


def simple_gen(ai: AI, dbs: DBs) -> Messages:
    """Run the AI on the main prompt and save the results"""
    messages = ai.start(
        Messages(
            [
                Message(role=Role.SYSTEM, content=setup_sys_prompt(dbs)),
                Message(role=Role.USER, content=dbs.input["main_prompt"]),
            ]
        )
    )
    to_files(messages.last_message_content(), dbs.workspace)
    return messages


def run_clarified(ai: AI, dbs: DBs) -> Messages:
    """
    Run the AI using the messages clarified in the previous step.
    """
    # get the messages from previous step
    messages = ai.next(
        Messages(
            [Message(role=Role.SYSTEM, content=setup_sys_prompt(dbs))]
            + Messages.from_json(dbs.logs[clarify.__name__]).messages[1:]
        ),
        user_prompt=dbs.identity["use_qa"],
    )
    to_files(messages.last_message_content(), dbs.workspace)
    return messages


def gen_spec(ai: AI, dbs: DBs) -> Messages:
    """
    Generate a spec from the main prompt + clarifications and save the results to
    the workspace
    """
    messages = Messages(
        [
            Message(role=Role.SYSTEM, content=setup_sys_prompt(dbs)),
            Message(
                role=Role.SYSTEM, content=f"Instructions: {dbs.input['main_prompt']}"
            ),
        ]
    )
    messages = ai.next(messages, user_prompt=dbs.identity["spec"])

    dbs.memory["specification"] = messages.last_message_content()

    return messages


def respec(ai: AI, dbs: DBs) -> Messages:
    messages = Messages(
        Messages.from_json(dbs.logs[gen_spec.__name__]).messages
        + [Message(role=Role.SYSTEM, content=dbs.identity["respec"])]
    )

    messages = ai.next(messages)
    messages = ai.next(
        messages,
        user_prompt=(
            "Based on the conversation so far, please reiterate the specification for "
            "the program. If there are things that can be improved, please incorporate "
            "the improvements. If you are satisfied with the specification, just write "
            "out the specification word by word again."
        ),
    )

    dbs.memory["specification"] = messages.last_message_content()
    return messages


def gen_unit_tests(ai: AI, dbs: DBs) -> Messages:
    """
    Generate unit tests based on the specification, that should work.
    """
    messages = Messages(
        [
            Message(role=Role.SYSTEM, content=setup_sys_prompt(dbs)),
            Message(role=Role.USER, content=f"Instructions: {dbs.input['main_prompt']}"),
            Message(
                role=Role.USER, content=f"Specification:\n\n{dbs.memory['specification']}"
            ),
        ]
    )

    messages = ai.next(messages, user_prompt=dbs.identity["unit_tests"])

    dbs.memory["unit_tests"] = messages.last_message_content()
    to_files(dbs.memory["unit_tests"], dbs.workspace)

    return messages


def gen_clarified_code(ai: AI, dbs: DBs) -> Messages:
    # get the messages from previous step

    messages = ai.next(
        Messages(
            [Message(role=Role.SYSTEM, content=setup_sys_prompt(dbs))]
            + Messages.from_json(dbs.logs[clarify.__name__]).messages[1:]
        ),
        user_prompt=dbs.identity["use_qa"],
    )

    to_files(messages.last_message_content(), dbs.workspace)
    return messages


def gen_code(ai: AI, dbs: DBs) -> Messages:
    # get the messages from previous step

    messages = ai.next(
        Messages(
            [
                Message(role=Role.SYSTEM, content=setup_sys_prompt(dbs)),
                Message(
                    role=Role.USER, content=f"Instructions: {dbs.input['main_prompt']}"
                ),
                Message(
                    role=Role.USER,
                    content=f"Specification:\n\n{dbs.memory['specification']}",
                ),
                Message(
                    role=Role.USER, content=f"Unit tests:\n\n{dbs.memory['unit_tests']}"
                ),
            ]
        ),
        dbs.identity["use_qa"],
    )
    to_files(messages.last_message_content(), dbs.workspace)
    return messages


def execute_entrypoint(ai, dbs) -> Messages:
    command = dbs.workspace["run.sh"]

    print("Do you want to execute this code?")
    print()
    print(command)
    print()
    print('If yes, press enter. Otherwise, type "no"')
    print()
    if input() not in ["", "y", "yes"]:
        print("Ok, not executing the code.")
        return Messages(messages=[])
    print("Executing the code...")
    print(
        "\033[92m"  # green color
        + "Note: If it does not work as expected, please consider running the code'"
        + " in another way than above."
        + "\033[0m"
    )
    print()
    subprocess.run("bash run.sh", shell=True, cwd=dbs.workspace.path)
    return Messages(messages=[])


def gen_entrypoint(ai, dbs) -> Messages:
    messages = ai.start(
        Messages(
            [
                Message(
                    role=Role.SYSTEM,
                    content=(
                        "You will get information about a codebase that is currently on "
                        "disk in the current folder.\n From this you will answer with "
                        "code blocks that includes all the necessary unix terminal "
                        "commands to a) install dependencies b) run all necessary parts "
                        "of the codebase (in parallell if necessary).\n Do not install "
                        "globally. Do not use sudo.\n Do not explain the code, just give"
                        " the commands.\n Do not use placeholders, use example values "
                        "(like . for a folder argument) if necessary.\n"
                    ),
                ),
                Message(
                    role=Role.USER,
                    content=(
                        "Information about the codebase:\n\n"
                        + dbs.workspace["all_output.txt"]
                    ),
                ),
            ]
        )
    )
    print()
    regex = r"```\S*\n(.+?)```"
    matches = re.finditer(regex, messages.last_message_content(), re.DOTALL)
    dbs.workspace["run.sh"] = "\n".join(match.group(1) for match in matches)
    return messages


def use_feedback(ai: AI, dbs: DBs) -> Messages:
    messages = Messages(
        [
            Message(role=Role.SYSTEM, content=setup_sys_prompt(dbs)),
            Message(role=Role.USER, content=f"Instructions: {dbs.input['main_prompt']}"),
            Message(role=Role.ASSISTANT, content=dbs.workspace["all_output.txt"]),
            Message(role=Role.SYSTEM, content=dbs.identity["use_feedback"]),
        ]
    )
    messages = ai.next(messages, user_prompt=dbs.memory["feedback"])
    to_files(messages.last_message_content(), dbs.workspace)
    return messages


def fix_code(ai: AI, dbs: DBs) -> Messages:
    code_output = Messages.from_json(dbs.logs[gen_code.__name__]).last_message_content()
    messages = Messages(
        [
            Message(role=Role.SYSTEM, content=setup_sys_prompt(dbs)),
            Message(role=Role.USER, content=f"Instructions: {dbs.input['main_prompt']}"),
            Message(role=Role.USER, content=code_output),
            Message(role=Role.SYSTEM, content=dbs.identity["fix_code"]),
        ]
    )
    messages = ai.next(messages, user_prompt="Please fix any errors in the code above.")
    to_files(messages.last_message_content(), dbs.workspace)
    return messages


class Config(str, Enum):
    DEFAULT = "default"
    BENCHMARK = "benchmark"
    SIMPLE = "simple"
    TDD = "tdd"
    TDD_PLUS = "tdd+"
    CLARIFY = "clarify"
    RESPEC = "respec"
    EXECUTE_ONLY = "execute_only"
    USE_FEEDBACK = "use_feedback"


# Different configs of what steps to run
StepFunction = Callable[[AI, DBs], Messages]

STEPS: Dict[Config, List[StepFunction]] = {
    Config.DEFAULT: [
        clarify,
        gen_clarified_code,
        gen_entrypoint,
        execute_entrypoint,
    ],
    Config.BENCHMARK: [simple_gen, gen_entrypoint],
    Config.SIMPLE: [simple_gen, gen_entrypoint, execute_entrypoint],
    Config.TDD: [
        gen_spec,
        gen_unit_tests,
        gen_code,
        gen_entrypoint,
        execute_entrypoint,
    ],
    Config.TDD_PLUS: [
        gen_spec,
        gen_unit_tests,
        gen_code,
        fix_code,
        gen_entrypoint,
        execute_entrypoint,
    ],
    Config.CLARIFY: [
        clarify,
        gen_clarified_code,
        gen_entrypoint,
        execute_entrypoint,
    ],
    Config.RESPEC: [
        gen_spec,
        respec,
        gen_unit_tests,
        gen_code,
        gen_entrypoint,
        execute_entrypoint,
    ],
    Config.USE_FEEDBACK: [use_feedback, gen_entrypoint, execute_entrypoint],
    Config.EXECUTE_ONLY: [gen_entrypoint, execute_entrypoint],
}

# Future steps that can be added:
# run_tests_and_fix_files
# execute_entrypoint_and_fix_files_if_needed
