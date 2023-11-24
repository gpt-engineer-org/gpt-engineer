import subprocess
from gpt_engineer.core.default.git_version_manager import GitVersionManager
from gpt_engineer.core.base_execution_env import BaseExecutionEnv
from gpt_engineer.core.code import Code
from gpt_engineer.core.default.paths import ENTRYPOINT_FILE
from gpt_engineer.core.default.on_disk_repository import OnDiskRepository


class OnDiskExecutionEnv(BaseExecutionEnv):
    """
    An execution environment that runs code on the local file system.

    This class is responsible for executing code that is stored on disk. It ensures that
    the necessary entrypoint file exists and then runs the code using a subprocess. If the
    execution is interrupted by the user, it handles the interruption gracefully.

    Attributes:
        path (str): The file system path where the code is located and will be executed.
    """

    def __init__(self, version_manager: GitVersionManager):
        self.version_manager = version_manager

    def execute_program(self, code: Code) -> subprocess.Popen:
        if not ENTRYPOINT_FILE in code:
            raise FileNotFoundError(
                "The required entrypoint "
                + ENTRYPOINT_FILE
                + " does not exist in the code."
            )
        # ToDo: The fact that execution is the de-facto way of saving the code to disk presently should change once version manager is implemented.
        self.version_manager.snapshot(code)

        p = subprocess.Popen(
            "bash " + ENTRYPOINT_FILE,
            shell=True,
            cwd=self.version_manager.path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        try:
            p.wait()
        except KeyboardInterrupt:
            print()
            print("Stopping execution.")
            print("Execution stopped.")
            p.kill()
            print()
        return p
