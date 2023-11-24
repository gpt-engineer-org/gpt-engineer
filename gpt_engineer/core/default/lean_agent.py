from gpt_engineer.core.code import Code
from gpt_engineer.core.ai import AI
from gpt_engineer.core.default.steps import (
    gen_code,
    gen_entrypoint,
    improve,
)
from gpt_engineer.core.default.git_version_manager import GitVersionManager
from gpt_engineer.core.base_repository import BaseRepository
from gpt_engineer.core.default.on_disk_repository import OnDiskRepository
from gpt_engineer.core.base_execution_env import BaseExecutionEnv
from gpt_engineer.core.default.on_disk_execution_env import OnDiskExecutionEnv
from gpt_engineer.core.default.paths import memory_path, ENTRYPOINT_FILE, PREPROMPTS_PATH
from gpt_engineer.core.base_agent import BaseAgent
from gpt_engineer.core.preprompts_holder import PrepromptsHolder


class LeanAgent(BaseAgent):
    """
    An agent that uses AI to generate and improve code based on a given prompt.

    This agent is capable of initializing a codebase from a prompt and improving an existing
    codebase based on user input. It uses an AI model to generate and refine code, and it
    interacts with a repository and an execution environment to manage and execute the code.

    Attributes:
        memory (BaseRepository): The repository where the code and related data are stored.
        execution_env (BaseExecutionEnv): The environment in which the code is executed.
        ai (AI): The AI model used for generating and improving code.
    """

    def __init__(
        self,
        memory: BaseRepository,
        execution_env: BaseExecutionEnv,
        ai: AI = None,
        preprompts_holder: PrepromptsHolder = None,
    ):
        self.preprompts_holder = preprompts_holder or PrepromptsHolder(PREPROMPTS_PATH)
        self.memory = memory
        self.execution_env = execution_env
        self.ai = ai or AI()

    @classmethod
    def with_default_config(
        cls, path: str, ai: AI = None, preprompts_holder: PrepromptsHolder = None
    ):
        return cls(
            memory=OnDiskRepository(memory_path(path)),
            execution_env=OnDiskExecutionEnv(GitVersionManager(path)),
            ai=ai,
            preprompts_holder=preprompts_holder or PrepromptsHolder(PREPROMPTS_PATH),
        )

    def init(self, prompt: str) -> Code:
        code = gen_code(self.ai, prompt, self.memory, self.preprompts_holder)
        entrypoint = gen_entrypoint(self.ai, code, self.memory, self.preprompts_holder)
        code = Code(code | entrypoint)
        code = self.execution_env.execute_program(code)
        return code

    def improve(
        self, code: Code, prompt: str, execution_command: str = ENTRYPOINT_FILE
    ) -> Code:
        code = improve(self.ai, prompt, code, self.memory, self.preprompts_holder)
        if not execution_command in code:
            entrypoint = gen_entrypoint(
                self.ai, code, self.memory, self.preprompts_holder
            )
            code = Code(code | entrypoint)
        code = self.execution_env.execute_program(code)
        return code
