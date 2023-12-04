import subprocess
import time

from gpt_engineer.core.base_execution_env import BaseExecutionEnv
from gpt_engineer.core.files_dict import FilesDict
from gpt_engineer.core.default.file_store import FileStore


class DiskExecutionEnv(BaseExecutionEnv):
    """
    An execution environment that runs code on the local file system.

    This class is responsible for executing code that is stored on disk. It ensures that
    the necessary entrypoint file exists and then runs the code using a subprocess. If the
    execution is interrupted by the user, it handles the interruption gracefully.

    Attributes:
        path (str): The file system path where the code is located and will be executed.
    """

    def __init__(self, path: str | None = None):
        self.store = FileStore(path)

    def upload(self, files: FilesDict) -> "DiskExecutionEnv":
        self.store.upload(files)
        return self

    def download(self) -> FilesDict:
        return self.store.download()

    def popen(self, command: str) -> subprocess.Popen:
        p = subprocess.Popen(
            command,
            shell=True,
            cwd=self.store.working_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return p

    def run(self, command: str, timeout: int | None = None) -> tuple[str, str, int]:
        start = time.time()
        print("\n--- Start of run ---")
        # while running, also print the stdout and stderr
        p = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.store.working_dir,
            text=True,
            shell=True,
        )
        print("$", command)
        stdout_full, stderr_full = "", ""

        try:
            while p.poll() is None:
                assert p.stdout is not None
                assert p.stderr is not None
                stdout = p.stdout.readline()
                stderr = p.stderr.readline()
                if stdout:
                    print(stdout, end="")
                    stdout_full += stdout
                if stderr:
                    print(stderr, end="")
                    stderr_full += stderr
                if timeout and time.time() - start > timeout:
                    print("Timeout!")
                    p.kill()
                    raise TimeoutError()
        except KeyboardInterrupt:
            print()
            print("Stopping execution.")
            print("Execution stopped.")
            p.kill()
            print()
            print("--- Finished run ---\n")

        return stdout_full, stderr_full, p.returncode
