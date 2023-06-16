from enum import Enum
import json
from typing import Any, Callable, Dict, List, Tuple

from gpt_engineer.ai import AI
from gpt_engineer.chat_to_files import to_files
from gpt_engineer.db import DBs
from gpt_engineer.models import Message, Role, Step



def setup_sys_prompt(dbs: DBs) -> str:
    """Constructs the system setup prompt."""
    return dbs.identity['setup'] + '\nUseful to know:\n' + dbs.identity['philosophy']


def clarify(ai: AI, dbs: DBs) -> List[Tuple[Role, Message]]:
    """
    Ask the user if they want to clarify anything and save the results to the workspace.
    """
    user_msg = dbs.input['main_prompt']
    messages = [(Role.SYSTEM, Message(dbs.identity['qa']))]
    while True:
        messages = ai.next(messages=messages, prompt=Message(user_msg))

        response_content: str =messages[-1][1].content
        if response_content.strip().lower() == 'no':
            break

        print(f"Help clarify: {response_content}")
        user_msg = input('(answer in text, or "q" to move on)\n')
        print()

        if not user_msg or user_msg == 'q':
            break

        user_msg += (
            '\n\n'
            'Is anything else unclear? If yes, only answer in the form:\n'
            '{remaining unclear areas} remaining questions.\n'
            '{Next question}\n'
            'If everything is sufficiently clear, only answer "no".'
        )

    print()
    return messages


def run_clarified(ai: AI, dbs: DBs) -> List[Tuple[Role, Message]]:
    """
    Run the AI using the messages clarified in the previous step.
    """
    # get the messages from previous step
    messages = json.loads(dbs.logs[Step.CLARIFY.value])

    messages = [
        (Role.SYSTEM, Message(setup_sys_prompt(dbs))),
    ] + [parse_message_json(m) for m in  messages[1:]]

    messages = ai.next(messages, dbs.identity['use_qa'])
    to_files(messages[-1][1].content, dbs.workspace)
    return messages


def parse_message_json(x: Dict[str, Any]) -> Tuple[Role, Message]:
    return Role(x["role"]), Message(x["content"])
    


STEPS: List[Callable[[AI, DBs], List[Tuple[Role, Message]]]] = [clarify, run_clarified]

# Future steps that can be added:
# improve_files,
# add_tests
# run_tests_and_fix_files,
# improve_based_on_in_file_feedback_comments