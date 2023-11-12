from gpt_engineer.core.code import Code
from gpt_engineer.core.base_version_manager import BaseVersionManager
from gpt_engineer.core.ai import AI
from abc import ABC, abstractmethod


class BaseAgent(ABC):
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
                Code: An instance of the `Code` class containing the generated code.

        improve(self, prompt: str) -> Code:
            Improves an existing piece of code using the AI and step bundle based on the provided prompt.
            It also snapshots the improved code using the version manager.

            Parameters:
                prompt (str): A string prompt that guides the code improvement process.

            Returns:
                Code: An instance of the `Code` class containing the improved code.
    """

    @abstractmethod
    def init(self, prompt: str) -> Code:
        pass

    @abstractmethod
    def improve(self, prompt: str, code: Code) -> Code:
        pass
