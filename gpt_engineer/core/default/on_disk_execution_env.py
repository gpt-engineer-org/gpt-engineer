import subprocess
import tempfile
import time
from pathlib import Path

from gpt_engineer.core.default.git_version_manager import GitVersionManager
from gpt_engineer.core.base_execution_env import ExecutionEnv
from gpt_engineer.core.code import Code
from gpt_engineer.core.default.paths import ENTRYPOINT_FILE
from gpt_engineer.core.default.on_disk_repository import OnDiskRepository


class FileStore:
    def __init__(self):
        self.working_dir = Path(tempfile.mkdtemp(prefix="gptme-evals-"))
        self.working_dir.mkdir(parents=True, exist_ok=True)
        self.id = self.working_dir.name.split("-")[-1]

    def upload(self, files: Code):
        for name, content in files.items():
            path = self.working_dir / name
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w") as f:
                f.write(content)
        return self

    def download(self) -> Code:
        files = {}
        for path in self.working_dir.glob("**/*"):
            if path.is_file():
                with open(path, "r") as f:
                    try:
                        content = f.read()
                    except UnicodeDecodeError:
                        content = "binary file"
                    files[str(path.relative_to(self.working_dir))] = content
        return Code(files)


class OnDiskExecutionEnv(FileStore, ExecutionEnv):
    """
    An execution environment that runs code on the local file system.

    This class is responsible for executing code that is stored on disk. It ensures that
    the necessary entrypoint file exists and then runs the code using a subprocess. If the
    execution is interrupted by the user, it handles the interruption gracefully.

    Attributes:
        path (str): The file system path where the code is located and will be executed.
    """

    def popen(self, command: str) -> subprocess.Popen:
        p = subprocess.Popen(
            command,
            shell=True,
            cwd=self.working_dir,
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

    def run(self, command: str, timeout: int | None = None) -> tuple[str, str, int]:
        start = time.time()
        print("\n--- Start of run ---")
        # while running, also print the stdout and stderr
        p = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.working_dir,
            text=True,
            shell=True,
        )
        print("$", command)
        stdout_full, stderr_full = "", ""
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
        print("--- Finished run ---\n")
        return stdout_full, stderr_full, p.returncode
