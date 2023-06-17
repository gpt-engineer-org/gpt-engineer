from typing import List
from gpt_engineer.chat_to_files import to_files
from gpt_engineer.ai import AI
from gpt_engineer.db import DB, DBs
import json
import random

class Step:
    step_id: str = "undefined"
    def __init__(self, name):
        self.name = name
        self.prev = None
    
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
            self.dbs.logs[step.step_id] = json.dumps(messages)
            self.prev_step = step

def setup_sys_prompt(dbs):
    return dbs.identity["generate"] + "\nUseful to know:\n" + dbs.identity["philosophy"]

class ClarificationStep(Step):
    step_id: str = "clarification"
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
    step_id: str = "run_latest"
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

class Planning(Step):
    step_id: str = "planning"
    def __init__(self):
        Step.__init__(self, "Planning")
    
    def run(self, ai: AI, dbs:DBs):
        # get the messages from previous step
        messages = self.prev.messages

        messages = [
            ai.fsystem("You provide additional creative information about the project."),
        ] + messages[1:]
        messages = ai.next(messages, dbs.identity['planning'])
        return messages

class RunMain(Step):
    step_id: str = "run_main"
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

class GenerateSpec(Step):
    step_id: str = "gen_spec"
    def __init__(self):
        Step.__init__(self, "Generate Specification")
    
    def run(self, ai: AI, dbs: DBs):
        """
        Generate a spec from the main prompt + clarifications and save the results to the workspace
        """
        messages = [
            ai.fsystem(setup_sys_prompt(dbs)),
            ai.fsystem(f"### Instruction: {dbs.input['main_prompt']}"),
        ]

        messages = ai.next(messages, dbs.identity["spec"])

        dbs.memory["specification"] = messages[-1]["content"]

        return messages

class ReSpec(Step):
    step_id: str = "respec"
    def __init__(self):
        Step.__init__(self, "Regenerate Specification")
    
    def run(self, ai: AI, dbs: DBs):
        messages = dbs.logs[GenerateSpec.step_id]
        messages += [ai.fsystem(dbs.identity["respec"])]

        messages = ai.next(messages)
        messages = ai.next(
            messages,
            (
                'Based on the conversation so far, please reiterate the specification for the program. '
                'If there are things that can be improved, please incorporate the improvements. '
                "If you are satisfied with the specification, just write out the specification word by word again."
            )
        )

        dbs.memory["specification"] = messages[-1]["content"]
        return messages

class GenerateUnitTests(Step):
    step_id: str = "gen_unit_tests"
    def __init__(self):
        Step.__init__(self, "Generate Unit Tests")

    def run(self, ai: AI, dbs: DBs):
        """
        Generate unit tests based on the specification, that should work.
        """
        messages = [
            ai.fsystem(setup_sys_prompt(dbs)),
            ai.fuser(f"Instructions: {dbs.input['main_prompt']}"),
            ai.fuser(f"Specification:\n\n{dbs.memory['specification']}"),
        ]

        messages = ai.next(messages, dbs.identity["unit_tests"])

        dbs.memory["unit_tests"] = messages[-1]["content"]
        to_files(dbs.memory["unit_tests"], dbs.workspace)

        return messages

class GenerateCode(Step):
    step_id: str = "gen_code"
    def __init__(self):
        Step.__init__(self, "Generate Code")
    
    def run(self, ai: AI, dbs: DBs):
        # get the messages from previous step

        messages = [
            ai.fsystem(setup_sys_prompt(dbs)),
            ai.fuser(f"Instructions: {dbs.input['main_prompt']}"),
            ai.fuser(f"Specification:\n\n{dbs.memory['specification']}"),
            ai.fuser(f"Unit tests:\n\n{dbs.memory['unit_tests']}"),
        ]
        messages = ai.next(messages, dbs.identity["use_qa"])
        to_files(messages[-1]["content"], dbs.workspace)
        return messages

class ExecuteWorkspace(Step):
    step_id: str = "exec_workspace"
    def __init__(self):
        Step.__init__(self, "Execute Workspace")

    def run(self, ai: AI, dbs: DBs):
        messages = gen_entrypoint(ai, dbs)
        execute_entrypoint(ai, dbs)
        return messages

class ExecuteEntrypoint(Step):
    step_id: str = "exec_entrypoint"
    def __init__(self):
        Step.__init__(self, "Execute Entrypoint")

    def run(self, ai: AI, dbs: DBs):
        command = dbs.workspace["run.sh"]

        print("Do you want to execute this code?")
        print()
        print(command)
        print()
        print('If yes, press enter. If no, type "no"')
        print()
        if input() == "no":
            print("Ok, not executing the code.")
        print("Executing the code...")
        print()
        subprocess.run("bash run.sh", shell=True, cwd=dbs.workspace.path)
        return []

class GenerateEntrypoint(Step):
    step_id: str = "gen_entry_point"
    def __init__(self):
        Step.__init__(self, "Generate Entrypoint")

    def run(self, ai: AI, dbs: DBs):
        messages = ai.start(
            system=(
                f"You will get information about a codebase that is currently on disk in the current folder.\n"
                "From this you will answer with one code block that includes all the necessary macos terminal commands to "
                "a) install dependencies "
                "b) run all necessary parts of the codebase (in parallell if necessary).\n"
                "Do not install globally. Do not use sudo.\n"
                "Do not explain the code, just give the commands.\n"
            ),
            user="Information about the codebase:\n\n" + dbs.workspace["all_output.txt"],
        )
        print()
        [[lang, command]] = parse_chat(messages[-1]["content"])
        assert lang in ["", "bash", "sh"]
        dbs.workspace["run.sh"] = command
        return messages