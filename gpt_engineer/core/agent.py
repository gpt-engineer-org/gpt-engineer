from gpt_engineer.core.domain import Code
from gpt_engineer.core.state_saver import StateSaver
from gpt_engineer.core.steps_interface import StepsInterface

class Agent:

    def __init__(self, path: str, state_saver_class: StateSaver, steps_interface_class: StepsInterface):
        self.path = path
        self.state_saver = state_saver_class()
        self.steps = steps_interface_class()

    def init(self, prompt: str) -> Code:
        return self.steps.gen_code(prompt)

    def improve(self, prompt: str) -> Code:
        return self.steps.improve(prompt)

