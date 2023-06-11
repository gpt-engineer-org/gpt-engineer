from ai import AI
from chat_to_files import to_files
from db import DBs
import json


def setup_sys_prompt(dbs):
    return dbs.identity['setup'] + '\nUseful to know:\n' + dbs.identity['philosophy']

def run(ai: AI, dbs: DBs):
    '''Run the AI on the main prompt and save the results'''
    messages = ai.start(setup_sys_prompt(dbs), dbs.input['main_prompt'])
    to_files(messages[-1]['content'], dbs.workspace)
    return messages

def clarify(ai: AI, dbs: DBs):
    '''Ask the user if they want to clarify anything and save the results to the workspace'''
    messages = [ai.fsystem(dbs.identity['qa'])]
    user = dbs.input['main_prompt']
    while True:
        messages = ai.next(messages, user)

        if messages[-1]['content'].strip().lower() == 'no':
            break

        print()
        user = input('(answer in text, or "q" to move on)\n')
        print()

        if not user or user == 'q':
            break

        user += (
           '\n\n'
           'Is anything else unclear? If yes, only answer in the form:\n'
            '{remaining unclear areas} remaining questions.\n'
            '{Next question}\n'
            'If everything is sufficiently clear, only answer "no".'
         )

    print()
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
    to_files(messages[-1]['content'], dbs.workspace)
    return messages


STEPS=[
    clarify,
    run_clarified
]

# Future steps that can be added:
# improve_files,
# add_tests
# run_tests_and_fix_files,
# improve_based_on_in_file_feedback_comments
