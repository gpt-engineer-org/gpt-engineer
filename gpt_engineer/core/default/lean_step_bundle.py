from gpt_engineer.core.ai import AI
from gpt_engineer.core.code import Code
from gpt_engineer.data.file_repository import FileRepository
from gpt_engineer.core.step_bundle_interface import StepBundleInterface
from gpt_engineer.core.default.steps import gen_code, gen_entrypoint, execute_entrypoint
from gpt_engineer.core.default.paths import memory_path

class LeanStepBundle(StepBundleInterface):

    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path
        self.memory = FileRepository(memory_path(workspace_path))


    def gen_code(self, ai: AI, prompt: str) -> Code:
        code = gen_code(self.workspace_path, ai, prompt, self.memory)
        #TODO: evaluate whether it makes more sense to send the code than the memory to gen_entrypoint
        entrypoint = gen_entrypoint(self.workspace_path, ai, self.memory)
        code = Code(code | entrypoint)
        execute_entrypoint(self.workspace_path, entrypoint)
        return code


    def improve_code(self, ai: AI, prompt: str) -> Code:
        pass
