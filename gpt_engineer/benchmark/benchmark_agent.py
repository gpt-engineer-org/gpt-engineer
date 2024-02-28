"""
Module for defining a simple agent that uses AI to manage code generation and improvement.

This module provides a class that represents an agent capable of initializing and improving
a codebase using AI. It handles interactions with the AI model, memory, and execution
environment to generate and refine code based on user prompts.

"""
import tempfile

from typing import Optional

from gpt_engineer.core.ai import AI
from gpt_engineer.core.base_agent import BaseAgent
from gpt_engineer.core.base_execution_env import BaseExecutionEnv
from gpt_engineer.core.base_memory import BaseMemory
from gpt_engineer.core.default.disk_execution_env import DiskExecutionEnv
from gpt_engineer.core.default.disk_memory import DiskMemory
from gpt_engineer.core.default.paths import (
    PREPROMPTS_PATH,
    memory_path,
)
from gpt_engineer.core.default.self_healing_agent import SelfHealingAgent
from gpt_engineer.core.default.steps import improve
from gpt_engineer.core.files_dict import FilesDict
from gpt_engineer.core.preprompts_holder import PrepromptsHolder


ARGUMENT_ERRORS = [
    'EOF'
    'not enough values to unpack',
    'index out of range'
]

# TODO: Suit for other benchmarks or call class `BenchmarkAppsAgent`
POST_PROMPT = f"When run with `python main.py`, the program should not require user " \
              "input and instead read undefined amount of command-line arguments " \
              "passed one by one and delimited with whitespace as in the following example: " \
              "`python main.py 59 9 11 'string_argument'`"


class BenchmarkAgent(BaseAgent, SelfHealingAgent):
    """
    An agent that uses AI to generate and improve code based on a given prompt.

    This agent is capable of initializing a codebase from a prompt and improving an existing
    codebase based on user input. It uses an AI model to generate and refine code, and it
    interacts with a repository and an execution environment to manage and execute the code.

    Attributes
    ----------
    memory : BaseMemory
        The memory interface where the code and related data are stored.
    execution_env : BaseExecutionEnv
        The execution environment in which the code is executed.
    ai : AI
        The AI model used for generating and improving code.
    preprompts_holder : PrepromptsHolder
        The holder for preprompt messages that guide the AI model.
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
        raise NotImplementedError

    def improve(
        self,
        files_dict: FilesDict,
        prompt: str,
        execution_command: Optional[str] = None,
    ) -> FilesDict:
        benchmark_prompt = f"{prompt}. {POST_PROMPT}"

        files_dict = improve(
            self.ai, benchmark_prompt, files_dict, self.memory, self.preprompts_holder
        )

        return files_dict

    def self_heal(self,
                  files_dict: FilesDict,
                  prompt: str,
                  stdout_full: str,
                  stderr_full: str,
                  ) -> FilesDict:
        self.execution_env.upload(files_dict)  # Load into execution_env in case it was cleared

        if any(error in stderr_full for error in ARGUMENT_ERRORS):
            stdout_full = f"{stdout_full}. {POST_PROMPT}"

        super().self_heal(files_dict, prompt, stdout_full, stderr_full)

        return files_dict


def default_config_agent():
    """
    Creates an instance of SimpleAgent with default configuration.

    Returns
    -------
    SimpleAgent
        An instance of SimpleAgent with a temporary directory as its base path.
    """
    return BenchmarkAgent.with_default_config(tempfile.mkdtemp())
