import tempfile

from gpt_engineer.core.files_dict import FilesDict
from gpt_engineer.core.ai import AI
from gpt_engineer.core.default.steps import (
    gen_code,
    gen_entrypoint,
    improve,
)
from gpt_engineer.core.base_memory import BaseMemory
from gpt_engineer.core.default.disk_memory import DiskMemory
from gpt_engineer.core.base_execution_env import BaseExecutionEnv
from gpt_engineer.core.default.disk_execution_env import DiskExecutionEnv
from gpt_engineer.core.default.paths import memory_path, PREPROMPTS_PATH
from gpt_engineer.core.base_agent import BaseAgent
from gpt_engineer.core.preprompts_holder import PrepromptsHolder


class SimpleAgent(BaseAgent):
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
        memory: BaseMemory,
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
            memory=DiskMemory(memory_path(path)),
            execution_env=DiskExecutionEnv(),
            ai=ai,
            preprompts_holder=preprompts_holder or PrepromptsHolder(PREPROMPTS_PATH),
        )

    def init(self, prompt: str) -> FilesDict:
        files_dict = gen_code(self.ai, prompt, self.memory, self.preprompts_holder)
        entrypoint = gen_entrypoint(
            self.ai, files_dict, self.memory, self.preprompts_holder
        )
        files_dict = FilesDict(files_dict | entrypoint)
        return files_dict

    def improve(
        self,
        files_dict: FilesDict,
        prompt: str,
        execution_command: str | None = None,
    ) -> FilesDict:
        files_dict = improve(
            self.ai, prompt, files_dict, self.memory, self.preprompts_holder
        )
        return files_dict


def default_config_agent():
    return SimpleAgent.with_default_config(tempfile.mkdtemp())
