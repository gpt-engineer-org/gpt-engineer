from gpt_engineer.core.code import Code
from gpt_engineer.core.version_manager_interface import VersionManagerInterface
from gpt_engineer.core.step_bundle_interface import StepBundleInterface
from gpt_engineer.core.ai import AI
from gpt_engineer.core.default.step_bundle import StepBundle
from gpt_engineer.core.default.version_manager import VersionManager

class Agent:

    def __init__(self, path: str, version_manager: VersionManagerInterface = None, step_bundle: StepBundleInterface = None, ai: AI = None):
        self.path = path
        self.version_manager = version_manager or VersionManager()
        self.step_bundle = step_bundle or StepBundle(self.path)
        self.ai = ai or AI()

    def init(self, prompt: str) -> Code:
        return self.step_bundle.gen_code(self.ai, prompt)

    def improve(self, prompt: str) -> Code:
        return self.step_bundle.improve_code(self.ai, prompt)

