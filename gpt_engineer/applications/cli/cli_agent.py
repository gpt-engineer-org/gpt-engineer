from gpt_engineer.core.files_dict import FilesDict

# from gpt_engineer.core.default.git_version_manager import GitVersionManager
from gpt_engineer.core.ai import AI
from gpt_engineer.core.default.steps import (
    gen_code,
    gen_entrypoint,
    execute_entrypoint,
    improve,
)
from gpt_engineer.core.base_memory import BaseMemory
from gpt_engineer.core.default.disk_memory import DiskMemory
from gpt_engineer.core.base_execution_env import BaseExecutionEnv
from gpt_engineer.core.default.disk_execution_env import DiskExecutionEnv
from gpt_engineer.core.default.paths import memory_path, ENTRYPOINT_FILE, PREPROMPTS_PATH
from gpt_engineer.core.base_agent import BaseAgent
from gpt_engineer.core.preprompts_holder import PrepromptsHolder
from typing import TypeVar, Callable, Union
from pathlib import Path

CodeGenType = TypeVar("CodeGenType", bound=Callable[[AI, str, BaseMemory], FilesDict])
CodeProcessor = TypeVar(
    "CodeProcessor", bound=Callable[[AI, BaseExecutionEnv, FilesDict], FilesDict]
)
ImproveType = TypeVar(
    "ImproveType", bound=Callable[[AI, str, FilesDict, BaseMemory], FilesDict]
)


class CliAgent(BaseAgent):
    """
    The `Agent` class is responsible for managing the lifecycle of code generation and improvement.

    Attributes:
        path (str): The file path where the `Agent` will operate, used for version management and
                    file operations.
        version_manager (BaseVersionManager): An object that adheres to the VersionManagerInterface,
                        responsible for version control of the generated code. Defaults to `VersionManager`
                        if not provided. PROBABLY GIT SHOULD BE USED IN THE DEFAULT
        step_bundle (StepBundleInterface): Workflows of code generation steps that define the behavior of gen_code and
        improve.
        ai (AI): Manages calls to the LLM.

    Methods:
        __init__(self, path: str, version_manager: VersionManagerInterface = None,
                 step_bundle: StepBundleInterface = None, ai: AI = None):
            Initializes a new instance of the Agent class with the provided path, version manager,
            step bundle, and AI. It falls back to default instances if specific components are not provided.

        init(self, prompt: str) -> Code:
            Generates a new piece of code using the AI and step bundle based on the provided prompt.
            It also snapshots the generated code using the version manager.

            Parameters:
                prompt (str): A string prompt that guides the code generation process.

            Returns:
                FilesDict: An instance of the `Code` class containing the generated code.

        improve(self, prompt: str) -> Code:
            Improves an existing piece of code using the AI and step bundle based on the provided prompt.
            It also snapshots the improved code using the version manager.

            Parameters:
                prompt (str): A string prompt that guides the code improvement process.

            Returns:
                FilesDict: An instance of the `Code` class containing the improved code.
    """

    def __init__(
        self,
        memory: BaseMemory,
        execution_env: BaseExecutionEnv,
        ai: AI = None,
        code_gen_fn: CodeGenType = gen_code,
        improve_fn: ImproveType = improve,
        process_code_fn: CodeProcessor = execute_entrypoint,
        preprompts_holder: PrepromptsHolder = None,
    ):
        self.memory = memory
        self.execution_env = execution_env
        self.ai = ai or AI()
        self.code_gen_fn = code_gen_fn
        self.process_code_fn = process_code_fn
        self.improve_fn = improve_fn
        self.preprompts_holder = preprompts_holder or PrepromptsHolder(PREPROMPTS_PATH)

    @classmethod
    def with_default_config(
        cls,
        memory: DiskMemory,
        execution_env: DiskExecutionEnv,
        ai: AI = None,
        code_gen_fn: CodeGenType = gen_code,
        improve_fn: ImproveType = improve,
        process_code_fn: CodeProcessor = execute_entrypoint,
        preprompts_holder: PrepromptsHolder = None,
    ):
        return cls(
            memory=memory,
            execution_env=execution_env,
            ai=ai,
            code_gen_fn=code_gen_fn,
            process_code_fn=process_code_fn,
            improve_fn=improve_fn,
            preprompts_holder=preprompts_holder or PrepromptsHolder(PREPROMPTS_PATH),
        )

    def init(self, prompt: str) -> FilesDict:
        files_dict = self.code_gen_fn(
            self.ai, prompt, self.memory, self.preprompts_holder
        )
        entrypoint = gen_entrypoint(
            self.ai, files_dict, self.memory, self.preprompts_holder
        )
        files_dict = FilesDict(files_dict | entrypoint)
        files_dict = self.process_code_fn(
            self.ai,
            self.execution_env,
            files_dict,
            preprompts_holder=self.preprompts_holder,
        )
        return files_dict

    def improve(
        self, files_dict: FilesDict, prompt: str, execution_command: str | None = None
    ) -> FilesDict:
        files_dict = self.improve_fn(
            self.ai, prompt, files_dict, self.memory, self.preprompts_holder
        )
        if not execution_command and ENTRYPOINT_FILE not in files_dict:
            entrypoint = gen_entrypoint(
                self.ai, files_dict, self.memory, self.preprompts_holder
            )
            files_dict = FilesDict(files_dict | entrypoint)
        files_dict = self.process_code_fn(
            self.ai,
            self.execution_env,
            files_dict,
            preprompts_holder=self.preprompts_holder,
        )
        return files_dict
