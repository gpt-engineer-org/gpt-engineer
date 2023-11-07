from gpt_engineer.core.ai import AI
from gpt_engineer.core.code import Code
from gpt_engineer.data.file_repository import FileRepository
from gpt_engineer.core.step_bundle_interface import StepBundleInterface
from gpt_engineer.core.default.steps import gen_code, gen_entrypoint, execute_entrypoint
from gpt_engineer.core.default.paths import memory_path
from gpt_engineer.applications.cli.learning import human_review


class CliStepBundle(StepBundleInterface):

    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path
        self.memory = FileRepository(memory_path(workspace_path))


    def gen_code(self, ai: AI, prompt: str) -> Code:
        code = gen_code(ai, prompt, self.memory, self.workspace_path)
        #TODO: evaluate whether it makes more sense to send the code than the memory to gen_entrypoint
        entrypoint = gen_entrypoint(ai, self.memory)
        code = Code(code | entrypoint)
        execute_entrypoint(self.workspace_path, entrypoint)
        human_review(self.memory)
        return code


    def improve_code(self, ai: AI, prompt: str) -> Code:
        pass
