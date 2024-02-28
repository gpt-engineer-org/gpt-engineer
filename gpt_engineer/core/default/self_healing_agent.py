"""
Module for defining a simple agent that uses AI to manage code generation and improvement.

This module provides a class that represents an agent capable of initializing and improving
a codebase using AI. It handles interactions with the AI model, memory, and execution
environment to generate and refine code based on user prompts.

"""

import tempfile
from subprocess import Popen

from typing import Optional

from gpt_engineer.core.ai import AI
from gpt_engineer.core.base_agent import BaseAgent
from gpt_engineer.core.base_execution_env import BaseExecutionEnv
from gpt_engineer.core.base_memory import BaseMemory
from gpt_engineer.core.default.disk_execution_env import DiskExecutionEnv
from gpt_engineer.core.default.disk_memory import DiskMemory
from gpt_engineer.core.default.paths import PREPROMPTS_PATH, memory_path
from gpt_engineer.core.default.steps import gen_code, gen_entrypoint, improve
from gpt_engineer.core.files_dict import FilesDict
from gpt_engineer.core.preprompts_holder import PrepromptsHolder


SUCCESS = 0
NO_RESPONSE = 2


class SelfHealingAgent:
    ai: AI
    memory: BaseMemory
    preprompts_holder: PrepromptsHolder

    # Base self-heal
    def self_heal(self,
                  files_dict: FilesDict,
                  prompt: str,
                  stdout_full: str,
                  stderr_full: str,
                  ) -> FilesDict:
        """
        Attempts to execute the code and if it fails,
        sends the error output back to the AI with instructions to fix.
        """
        new_prompt = f"A program with this specification was requested:\n{prompt}\n, but running it produced the following output:\n{stdout_full}\n and the following errors:\n{stderr_full}. Please change it so that it fulfills the requirements."

        return improve(
            self.ai, new_prompt, files_dict, self.memory, self.preprompts_holder
        )