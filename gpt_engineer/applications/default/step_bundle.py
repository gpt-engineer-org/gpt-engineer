from gpt_engineer.core.ai import AI
from gpt_engineer.core.code import Code
from gpt_engineer.core.step_bundle_interface import StepBundleInterface

class StepBundle(StepBundleInterface):

    def __init__(self):
        pass

    def gen_code(self, ai: AI, prompt: str) -> Code:
        pass

    def improve_code(self, ai: AI, prompt: str) -> Code:
        pass
