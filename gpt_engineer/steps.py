import json
import re
import subprocess

from enum import Enum
from typing import List

from termcolor import colored

from gpt_engineer.ai import AI
from gpt_engineer.chat_to_files import to_files
from gpt_engineer.db import DBs
from gpt_engineer.learning import human_input


def setup_sys_prompt(dbs: DBs) -> str:
    return (
        dbs.preprompts["generate"] + "\nUseful to know:\n" + dbs.preprompts["philosophy"]
    )


def get_prompt(dbs: DBs) -> str:
    """While we migrate we have this fallback getter"""
    assert (
        "prompt" in dbs.input or "main_prompt" in dbs.input
    ), "Please put your prompt in the file `prompt` in the project directory"

    if "prompt" not in dbs.input:
        print(
            colored("Please put the prompt in the file `prompt`, not `main_prompt", "red")
        )
        print()
        return dbs.input["main_prompt"]

    return dbs.input["prompt"]


# All steps below have the signature Step


def simple_gen(ai: AI, dbs: DBs) -> List[dict]:
    """Run the AI on the main prompt and save the results"""
    messages = ai.start(setup_sys_prompt(dbs), get_prompt(dbs))
    to_files(messages[-1]["content"], dbs.workspace)
    return messages


def clarify(ai: AI, dbs: DBs) -> List[dict]:
    """
    Ask the user if they want to clarify anything and save the results to the workspace
    """
    messages = [ai.fsystem(dbs.preprompts["qa"])]
    user_input = get_prompt(dbs)
    while True:
        messages = ai.next(messages, user_input)

        if messages[-1]["content"].strip() == "Nothing more to clarify.":
            break

        if messages[-1]["content"].strip().lower().startswith("no"):
            print("Nothing more to clarify.")
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
            )
            print()
            return messages

        user_input += (
            "\n\n"
            "Is anything else unclear? If yes, only answer in the form:\n"
            "{remaining unclear areas} remaining questions.\n"
            "{Next question}\n"
            'If everything is sufficiently clear, only answer "Nothing more to clarify.".'
        )

    print()
    return messages


def gen_spec(ai: AI, dbs: DBs) -> List[dict]:
    """
    Generate a spec from the main prompt + clarifications and save the results to
    the workspace
    """
    messages = [
        ai.fsystem(setup_sys_prompt(dbs)),
        ai.fsystem(f"Instructions: {dbs.input['prompt']}"),
    ]

    messages = ai.next(messages, dbs.preprompts["spec"])

    dbs.memory["specification"] = messages[-1]["content"]

    return messages


def respec(ai: AI, dbs: DBs) -> List[dict]:
    messages = json.loads(dbs.logs[gen_spec.__name__])
    messages += [ai.fsystem(dbs.preprompts["respec"])]

    messages = ai.next(messages)
    messages = ai.next(
        messages,
        (
            "Based on the conversation so far, please reiterate the specification for "
            "the program. "
            "If there are things that can be improved, please incorporate the "
            "improvements. "
            "If you are satisfied with the specification, just write out the "
            "specification word by word again."
        ),
    )

    dbs.memory["specification"] = messages[-1]["content"]
    return messages


def gen_unit_tests(ai: AI, dbs: DBs) -> List[dict]:
    """
    Generate unit tests based on the specification, that should work.
    """
    messages = [
        ai.fsystem(setup_sys_prompt(dbs)),
        ai.fuser(f"Instructions: {dbs.input['prompt']}"),
        ai.fuser(f"Specification:\n\n{dbs.memory['specification']}"),
    ]

    messages = ai.next(messages, dbs.preprompts["unit_tests"])

    dbs.memory["unit_tests"] = messages[-1]["content"]
    to_files(dbs.memory["unit_tests"], dbs.workspace)

    return messages


def gen_clarified_code(ai: AI, dbs: DBs) -> List[dict]:
    """Takes clarification and generates code"""

    messages = json.loads(dbs.logs[clarify.__name__])

    messages = [
        ai.fsystem(setup_sys_prompt(dbs)),
    ] + messages[1:]
    messages = ai.next(messages, dbs.preprompts["use_qa"])

    to_files(messages[-1]["content"], dbs.workspace)
    return messages


def gen_code(ai: AI, dbs: DBs) -> List[dict]:
    # get the messages from previous step

    messages = [
        ai.fsystem(setup_sys_prompt(dbs)),
        ai.fuser(f"Instructions: {dbs.input['prompt']}"),
        ai.fuser(f"Specification:\n\n{dbs.memory['specification']}"),
        ai.fuser(f"Unit tests:\n\n{dbs.memory['unit_tests']}"),
    ]
    messages = ai.next(messages, dbs.preprompts["use_qa"])
    to_files(messages[-1]["content"], dbs.workspace)
    return messages


def execute_entrypoint(ai: AI, dbs: DBs) -> List[dict]:
    command = dbs.workspace["run.sh"]

    print("Do you want to execute this code?")
    print()
    print(command)
    print()
    print('If yes, press enter. Otherwise, type "no"')
    print()
    if input() not in ["", "y", "yes"]:
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

    p = subprocess.Popen("bash run.sh", shell=True, cwd=dbs.workspace.path)
    try:
        p.wait()
    except KeyboardInterrupt:
        print()
        print("Stopping execution.")
        print("Execution stopped.")
        p.kill()
        print()

    return []


def gen_entrypoint(ai: AI, dbs: DBs) -> List[dict]:
    messages = ai.start(
        system=(
            "You will get information about a codebase that is currently on disk in "
            "the current folder.\n"
            "From this you will answer with code blocks that includes all the necessary "
            "unix terminal commands to "
            "a) install dependencies "
            "b) run all necessary parts of the codebase (in parallel if necessary).\n"
            "Do not install globally. Do not use sudo.\n"
            "Do not explain the code, just give the commands.\n"
            "Do not use placeholders, use example values (like . for a folder argument) "
            "if necessary.\n"
        ),
        user="Information about the codebase:\n\n" + dbs.workspace["all_output.txt"],
    )
    print()

    regex = r"```\S*\n(.+?)```"
    matches = re.finditer(regex, messages[-1]["content"], re.DOTALL)
    dbs.workspace["run.sh"] = "\n".join(match.group(1) for match in matches)
    return messages


def use_feedback(ai: AI, dbs: DBs):
    messages = [
        ai.fsystem(setup_sys_prompt(dbs)),
        ai.fuser(f"Instructions: {dbs.input['prompt']}"),
        ai.fassistant(dbs.workspace["all_output.txt"]),
        ai.fsystem(dbs.preprompts["use_feedback"]),
    ]
    messages = ai.next(messages, dbs.input["feedback"])
    to_files(messages[-1]["content"], dbs.workspace)
    return messages


def fix_code(ai: AI, dbs: DBs):
    code_output = json.loads(dbs.logs[gen_code.__name__])[-1]["content"]
    messages = [
        ai.fsystem(setup_sys_prompt(dbs)),
        ai.fuser(f"Instructions: {dbs.input['prompt']}"),
        ai.fuser(code_output),
        ai.fsystem(dbs.preprompts["fix_code"]),
    ]
    messages = ai.next(messages, "Please fix any errors in the code above.")
    to_files(messages[-1]["content"], dbs.workspace)
    return messages


def human_review(ai: AI, dbs: DBs):
    review = human_input()
    dbs.memory["review"] = review.to_json()  # type: ignore
    return []


class Config(str, Enum):
    DEFAULT = "default"
    BENCHMARK = "benchmark"
    SIMPLE = "simple"
    TDD = "tdd"
    TDD_PLUS = "tdd+"
    CLARIFY = "clarify"
    RESPEC = "respec"
    EXECUTE_ONLY = "execute_only"
    EVALUATE = "evaluate"
    USE_FEEDBACK = "use_feedback"


# Different configs of what steps to run
STEPS = {
    Config.DEFAULT: [
        clarify,
        gen_clarified_code,
        gen_entrypoint,
        execute_entrypoint,
        human_review,
    ],
    Config.BENCHMARK: [simple_gen, gen_entrypoint],
    Config.SIMPLE: [simple_gen, gen_entrypoint, execute_entrypoint],
    Config.TDD: [
        gen_spec,
        gen_unit_tests,
        gen_code,
        gen_entrypoint,
        execute_entrypoint,
        human_review,
    ],
    Config.TDD_PLUS: [
        gen_spec,
        gen_unit_tests,
        gen_code,
        fix_code,
        gen_entrypoint,
        execute_entrypoint,
        human_review,
    ],
    Config.CLARIFY: [
        clarify,
        gen_clarified_code,
        gen_entrypoint,
        execute_entrypoint,
        human_review,
    ],
    Config.RESPEC: [
        gen_spec,
        respec,
        gen_unit_tests,
        gen_code,
        fix_code,
        gen_entrypoint,
        execute_entrypoint,
        human_review,
    ],
    Config.USE_FEEDBACK: [use_feedback, gen_entrypoint, execute_entrypoint, human_review],
    Config.EXECUTE_ONLY: [execute_entrypoint],
    Config.EVALUATE: [execute_entrypoint, human_review],
}

# Future steps that can be added:
# run_tests_and_fix_files
# execute_entrypoint_and_fix_files_if_it_results_in_error
