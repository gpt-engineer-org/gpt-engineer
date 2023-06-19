from enum import Enum
import json
import re
import subprocess
from typing import Any, Callable, Dict, List, Tuple

from gpt_engineer.ai.ai import AI
from gpt_engineer.chat_to_files import to_files
from gpt_engineer.db import DBs
from gpt_engineer.models import Message, Role, Step


def setup_sys_prompt(dbs: DBs) -> str:
    """Constructs the system setup prompt."""
    return dbs.identity["generate"] + "\nUseful to know:\n" + dbs.identity["philosophy"]

def parse_message_json(x: Dict[str, Any]) -> Tuple[Role, Message]:
    return Role(x["role"]), Message(x["content"])



### Steps

def clarify(ai: AI, dbs: DBs) -> List[Tuple[Role, Message]]:
    """
    Ask the user if they want to clarify anything and save the results to the workspace.
    """
    user_msg = dbs.input['main_prompt']
    messages = [(Role.SYSTEM, Message(dbs.identity['qa']))]
    while True:
        messages = ai.next(messages=messages, user_prompt=Message(user_msg))

        response_content: str =messages[-1][1].content
        if response_content.strip().lower() == 'no':
            break

        print(f"Help clarify: {response_content}")
        user_msg = input('(answer in text, or "q" to move on)\n')
        print()

        if not user_msg or user_msg == 'q':
            break

        user += (
            "\n\n"
            "Is anything else unclear? If yes, only answer in the form:\n"
            "{remaining unclear areas} remaining questions.\n"
            "{Next question}\n"
            'If everything is sufficiently clear, only answer "no".'
        )
    print()
    return messages 


def simple_gen(ai: AI, dbs: DBs) -> List[Tuple[Role, Message]]:
    """Run the AI on the main prompt and save the results"""
    messages = ai.start([
        (Role.SYSTEM, Message(setup_sys_prompt(dbs))),
        (Role.USER, dbs.input["main_prompt"])
    ])
    to_files(messages[-1][1].content, dbs.workspace)
    return messages


def run_clarified(ai: AI, dbs: DBs) -> List[Tuple[Role, Message]]:
    """
    Run the AI using the messages clarified in the previous step.
    """
    # get the messages from previous step
    messages = json.loads(dbs.logs[Step.CLARIFY.value])

    # TODO
    print(messages)

    messages = [
        (Role.SYSTEM, Message(setup_sys_prompt(dbs))),
    ] + [parse_message_json(m) for m in  messages[1:]]

    messages = ai.next(messages, user_prompt=dbs.identity['use_qa'])
    to_files(messages[-1][1].content, dbs.workspace)
    return messages


def gen_spec(ai: AI, dbs: DBs) -> List[Tuple[Role, Message]]:
    """
    Generate a spec from the main prompt + clarifications and save the results to
    the workspace
    """
    messages = [
        (Role.SYSTEM, Message(setup_sys_prompt(dbs))),
        (Role.SYSTEM, f"Instructions: {dbs.input['main_prompt']}")
    ]

    messages = ai.next(messages, user_prompt=dbs.identity["spec"])

    dbs.memory["specification"] = messages[-1][1].content

    return messages


def respec(ai: AI, dbs: DBs) -> List[Tuple[Role, Message]]:
    messages = [(Role.SYSTEM, Message(log)) for log in dbs.logs[gen_spec.__name__]]
    messages += [(Role.SYSTEM, Message(dbs.identity["respec"]))]

    messages = ai.next(messages)
    messages = ai.next(
        messages,
        user_prompt=(
            "Based on the conversation so far, please reiterate the specification for the program. "
            "If there are things that can be improved, please incorporate the improvements. If you "
            "are satisfied with the specification, just write out the specification word by word again."
        )
    )

    dbs.memory["specification"] = messages[-1][1].content
    return messages


def gen_unit_tests(ai: AI, dbs: DBs) -> List[Tuple[Role, Message]]:
    """
    Generate unit tests based on the specification, that should work.
    """
    messages = [
        (Role.SYSTEM, Message(setup_sys_prompt(dbs))),
        (Role.USER, Message(f"Instructions: {dbs.input['main_prompt']}")),
        (Role.USER, Message(f"Specification:\n\n{dbs.memory['specification']}")),
    ]

    messages = ai.next(messages, user_prompt=dbs.identity["unit_tests"])

    dbs.memory["unit_tests"] = messages[-1][1].content
    to_files(dbs.memory["unit_tests"], dbs.workspace)

    return messages


def gen_clarified_code(ai: AI, dbs: DBs) -> List[Tuple[Role, Message]]:
    # get the messages from previous step

    # TODO: 
    messages = json.loads(dbs.logs[clarify.__name__])

    messages = [
        (Role.SYSTEM, Message(setup_sys_prompt(dbs))),
    ] + [parse_message_json(m) for m in  messages[1:]]
    messages = ai.next(messages, dbs.identity["use_qa"])

    to_files(messages[-1][1].content, dbs.workspace)
    return messages


def gen_code(ai: AI, dbs: DBs) -> List[Tuple[Role, Message]]:
    # get the messages from previous step

    messages = [
        (Role.SYSTEM, Message(setup_sys_prompt(dbs))),
        (Role.USER, Message(f"Instructions: {dbs.input['main_prompt']}")),
        (Role.USER, Message(f"Specification:\n\n{dbs.memory['specification']}")),
        (Role.USER, Message(f"Unit tests:\n\n{dbs.memory['unit_tests']}")),
    ]
    messages = ai.next(messages, dbs.identity["use_qa"])
    to_files(messages[-1][1].content, dbs.workspace)
    return messages


def execute_entrypoint(ai, dbs) -> List[Tuple[Role, Message]]:
    command = dbs.workspace["run.sh"]

    print("Do you want to execute this code?")
    print()
    print(command)
    print()
    print('If yes, press enter. Otherwise, type "no"')
    print()
    if input() != "":
        print("Ok, not executing the code.")
        return []
    print("Executing the code...")
    print()
    subprocess.run("bash run.sh", shell=True, cwd=dbs.workspace.path)
    return []


def gen_entrypoint(ai, dbs) -> List[Tuple[Role, Message]]:
    messages = ai.start(
        [(Role.SYSTEM, Message(
            "You will get information about a codebase that is currently on disk in "
            "the current folder.\n"
            "From this you will answer with code blocks that includes all the necessary "
            "unix terminal commands to "
            "a) install dependencies "
            "b) run all necessary parts of the codebase (in parallell if necessary).\n"
            "Do not install globally. Do not use sudo.\n"
            "Do not explain the code, just give the commands.\n"
        )),
        (Role.USER, Message("Information about the codebase:\n\n" + dbs.workspace["all_output.txt"]))
        ]
    )
    print()

    regex = r"```\S*\n(.+?)```"
    matches = re.finditer(regex, messages[-1][1].content, re.DOTALL)
    dbs.workspace["run.sh"] = "\n".join(match.group(1) for match in matches)
    return messages


def use_feedback(ai: AI, dbs: DBs) -> List[Tuple[Role, Message]]:
    messages = [
        (Role.SYSTEM, Message(setup_sys_prompt(dbs))),
        (Role.USER, Message(f"Instructions: {dbs.input['main_prompt']}")),
        (Role.ASSISTANT, Message(dbs.workspace["all_output.txt"])),
        (Role.SYSTEM, Message(dbs.identity["use_feedback"])),
    ]
    messages = ai.next(messages, user_prompt=dbs.memory["feedback"])
    to_files(messages[-1][1].content, dbs.workspace)
    return messages


def fix_code(ai: AI, dbs: DBs) -> List[Tuple[Role, Message]]:
    code_ouput = json.loads(dbs.logs[gen_code.__name__])[-1]["content"]
    messages = [
        (Role.SYSTEM, Message(setup_sys_prompt(dbs))),
        (Role.USER, Message(f"Instructions: {dbs.input['main_prompt']}")),
        (Role.USER, Message(code_ouput)),
        (Role.SYSTEM, Message(dbs.identity["fix_code"])),
    ]
    messages = ai.next(messages, user_prompt="Please fix any errors in the code above.")
    to_files(messages[-1][1].content, dbs.workspace)
    return messages


# Different configs of what steps to run
StepFunction = Callable[[AI, DBs], List[Tuple[Role, Message]]]
STEPS: Dict[str, List[StepFunction]] = {
    "default": [gen_spec, gen_unit_tests, gen_code, gen_entrypoint, execute_entrypoint],
    "benchmark": [gen_spec, gen_unit_tests, gen_code, fix_code, gen_entrypoint],
    "simple": [simple_gen, gen_entrypoint, execute_entrypoint],
    "clarify": [clarify, gen_clarified_code, gen_entrypoint, execute_entrypoint],
    "respec": [
        gen_spec,
        respec,
        gen_unit_tests,
        gen_code,
        gen_entrypoint,
        execute_entrypoint,
    ],
    "execute_only": [execute_entrypoint],
    "use_feedback": [use_feedback],
}

# Future steps that can be added:
# self_reflect_and_improve_files,
# add_tests
# run_tests_and_fix_files,
# improve_based_on_in_file_feedback_comments
