from gpt_engineer.core.code import Code
from gpt_engineer.core.ai import AI
from gpt_engineer.core.default.steps import (
    gen_code,
    gen_entrypoint,
    improve,
)
from gpt_engineer.core.base_repository import BaseRepository
from gpt_engineer.core.default.on_disk_repository import OnDiskRepository
from gpt_engineer.core.base_execution_env import BaseExecutionEnv
from gpt_engineer.core.default.on_disk_execution_env import OnDiskExecutionEnv
from gpt_engineer.core.default.paths import memory_path, ENTRYPOINT_FILE
from gpt_engineer.core.base_agent import BaseAgent


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
    ):
        self.memory = memory
        self.execution_env = execution_env
        self.ai = ai or AI()

    @classmethod
    def with_default_config(cls, path: str, ai: AI = None):
        return cls(
            memory=OnDiskRepository(memory_path(path)),
            execution_env=OnDiskExecutionEnv(path),
            ai=ai,
        )

    def init(self, prompt: str) -> Code:
        code = gen_code(self.ai, prompt, self.memory)
        entrypoint = gen_entrypoint(self.ai, code, self.memory)
        code = Code(code | entrypoint)
        self.execution_env.execute_program(code)
        return code

    def improve(
        self, code: Code, prompt: str, execution_command: str = ENTRYPOINT_FILE
    ) -> Code:
        code = improve(self.ai, prompt, code, self.memory)
        if not execution_command in code:
            entrypoint = gen_entrypoint(self.ai, code, self.memory)
            code = Code(code | entrypoint)
        self.execution_env.execute_program(code)
        return code
