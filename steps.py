import json
import random

from ai import AI
from chat_to_files import to_files
from db import DBs
from typing import List

class Step:
    def __init__(self, name):
        self.name = name
        self.prev = None
        self.id = self.name.lower().replace(" ", "_") + str(random.randrange(1000, 9999))
    
    def __call__(self, runner: 'StepRunner' = None):
        self.prev = runner.prev_step
        self.messages = self.run(runner.ai, runner.dbs)
        return self.messages

    def run(self, ai: AI, dbs: DBs):
        pass

class StepRunner:
    def __init__(self, ai:AI, dbs: DBs, steps: List[Step]):
        self.ai = ai
        self.dbs = dbs
        self.steps = steps
        self.prev_step = None
    
    def run(self):
        for step in self.steps:
            messages = step(self)
            self.dbs.logs[step.id] = json.dumps(messages)
            self.prev_step = step

    

class ClarificationStep(Step):
    def __init__(self):
        Step.__init__(self, "Clarification")
    
    def run(self, ai:AI, dbs: DBs):
        '''
        Ask the user if they want to clarify anything and save the results to the workspace
        '''
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

class RunLatest(Step):
    def __init__(self):
        Step.__init__(self, "Run Latest")
    
    def run(self, ai: AI, dbs:DBs):
        # get the messages from previous step
        messages = self.prev.messages

        messages = [
            ai.fsystem(setup_sys_prompt(dbs)),
        ] + messages[1:]
        messages = ai.next(messages, dbs.identity['use_qa'])
        to_files(messages[-1]['content'], dbs.workspace)
        return messages

class RunMain(Step):
    def __init__(self):
        Step.__init__(self, "Run Main")
    
    def run(self, ai: AI, dbs:DBs):
        '''Run the AI on the main prompt and save the results'''
        messages = ai.start(
            setup_sys_prompt(dbs),
            dbs.input['main_prompt'],
        )
        to_files(messages[-1]['content'], dbs.workspace)
        return messages


def setup_sys_prompt(dbs):
    return dbs.identity['setup'] + '\nUseful to know:\n' + dbs.identity['philosophy']


def run(ai: AI, dbs: DBs):
    '''Run the AI on the main prompt and save the results'''
    messages = ai.start(
        setup_sys_prompt(dbs),
        dbs.input['main_prompt'],
    )
    to_files(messages[-1]['content'], dbs.workspace)
    return messages


def standard_runner(ai: AI, dbs: DBs):
    return StepRunner(ai, dbs, [
        ClarificationStep(),
        RunLatest()
    ])

# Future steps that can be added:
# improve_files,
# add_tests
# run_tests_and_fix_files,
# improve_based_on_in_file_feedback_comments
