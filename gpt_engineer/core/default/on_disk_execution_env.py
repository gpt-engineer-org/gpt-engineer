import subprocess
from gpt_engineer.core.base_execution_env import BaseExecutionEnv
from gpt_engineer.core.code import Code
from gpt_engineer.core.default.paths import ENTRYPOINT_FILE


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

        p = subprocess.Popen("bash run.sh", shell=True, cwd=self.path)
        try:
            p.wait()
        except KeyboardInterrupt:
            print()
            print("Stopping execution.")
            print("Execution stopped.")
            p.kill()
            print()
        return p
