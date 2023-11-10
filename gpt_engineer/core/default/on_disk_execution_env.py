import subprocess
from gpt_engineer.core.base_execution_env import BaseExecutionEnv
from gpt_engineer.core.code import Code
from gpt_engineer.core.default.paths import ENTRYPOINT_FILE
from gpt_engineer.core.default.on_disk_repository import OnDiskRepository


class OnDiskExecutionEnv(BaseExecutionEnv):
    def __init__(self, path: str):
        self.path = path

    def execute_program(self, code: Code) -> subprocess.Popen:

        if not ENTRYPOINT_FILE in code:
            raise FileNotFoundError(
                "The required entrypoint "
                + ENTRYPOINT_FILE
                + " does not exist in the code."
            )

        workspace = OnDiskRepository(self.path)
        for file_name, file_content in code.items():
            workspace[file_name] = file_content

        p = subprocess.Popen("bash " + ENTRYPOINT_FILE, shell=True, cwd=self.path)
        try:
            p.wait()
        except KeyboardInterrupt:
            print()
            print("Stopping execution.")
            print("Execution stopped.")
            p.kill()
            print()
        return p
