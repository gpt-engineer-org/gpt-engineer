from gpt_engineer.core.code import Code
from gpt_engineer.core.state_saver import StateSaver
from gpt_engineer.core.step_bundle_interface import StepBundleInterface
from gpt_engineer.core.ai import AI

class Agent:

    def __init__(self, path: str, state_saver_class: StateSaver, steps_interface_class: StepBundleInterface, ai_class: AI = AI):
        self.path = path
        self.state_saver = state_saver_class()
        self.steps = steps_interface_class()
        self.ai = ai_class()

    def init(self, prompt: str) -> Code:
        '''

        Parameters
        ----------
        prompt

        Returns
        -------

        '''
        return self.steps.gen_code(self.ai, prompt)

    def improve(self, prompt: str) -> Code:
        return self.steps.improve_code(self.ai, prompt)

