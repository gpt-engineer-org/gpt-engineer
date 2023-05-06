from ast import List
from dataclasses import dataclass
from typing import Callable
from ai import AI
from chat_to_files import to_files

from db import DBs
from db import DB

def setup_sys_prompt(dbs):
    return dbs.identity['setup'] + '\nUseful to know:\n' + dbs.identity['philosophy']

def setup(ai: AI, dbs: DBs):
    messages = ai.start(setup_sys_prompt(dbs), dbs.input['main_prompt'])
    to_files(messages[-1]['content'], dbs.workspace)
    return messages

def run_clarified(ai: AI, dbs: DBs):
    messages = ai.start(setup_sys_prompt(dbs), dbs.input['main_prompt'])
    to_files(messages[-1]['content'], DB(str(dbs.workspace.path)+'_clarified'))
    return messages

def clarify(ai: AI, dbs: DBs):
    messages = [ai.fsystem(dbs.identity['qa'])]
    user = dbs.input['main_prompt']
    while True:
        messages = ai.next(messages, user)
        print()
        user = input('Answer: ')
        if not user or user == 'q':
            break

        user += '\nIs anything else unclear? Please ask more questions until instructions are sufficient to write the code.'

    # TOOD: Stop using clarify prompt. Just append questions and answers to the main prompt.
    prompt = dbs.identity['clarify']
    messages = ai.next([ai.fsystem(prompt)] + messages[1:], prompt)
    dbs.memory['clarified_prompt'] = messages[-1]['content']
    return messages


# STEPS: List[Callable[[AI, DBs], List]] = [
STEPS=[
    setup,
    # clarify,
    # run_clarified
    # to_files,
    # improve_files,
    # run_tests,
    # ImproveBasedOnHumanComments
]
