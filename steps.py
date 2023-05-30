from ast import List
from dataclasses import dataclass
from typing import Callable
from ai import AI
from chat_to_files import to_files
import json

from db import DBs
from db import DB

def setup_sys_prompt(dbs):
    return dbs.identity['setup'] + '\nUseful to know:\n' + dbs.identity['philosophy']

def setup(ai: AI, dbs: DBs):
    messages = ai.start(setup_sys_prompt(dbs), dbs.input['main_prompt'])
    to_files(messages[-1]['content'], dbs.workspace)
    return messages

def clarify(ai: AI, dbs: DBs):
    messages = [ai.fsystem(dbs.identity['qa'])]
    user = dbs.input['main_prompt']
    while True:
        messages = ai.next(messages, user)

        if messages[-1]['content'].strip().lower() == 'no':
            break

        print()
        user = input('Answer: ')
        if not user or user == 'q':
            break

        user += '\n\nIs anything else unclear? If everything is sufficiently clear to write the code, just answer "no".'

    return messages

def run_clarified(ai: AI, dbs: DBs):
    # get the messages from previous step
    messages = json.loads(dbs.logs[clarify.__name__])

    messages = (
        [
            ai.fsystem(setup_sys_prompt(dbs)),
        ] +
        messages[1:]
    )
    messages = ai.next(messages, dbs.identity['use_qa'])
    to_files(messages[-1]['content'], DB(str(dbs.workspace.path)+'_clarified'))
    return messages


# STEPS: List[Callable[[AI, DBs], List]] = [
STEPS=[
    # setup,
    clarify,
    run_clarified
    # improve_files,
    # run_tests,
    # ImproveBasedOnHumanComments
]
