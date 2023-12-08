from gpt_engineer.benchmark.types import Benchmark, Task
from gpt_engineer.core.files_dict import FilesDict
from gpt_engineer.core.base_execution_env import BaseExecutionEnv


def load_gptme():
    return Benchmark(
        name="gptme",
        tasks=[
            Task(
                name="hello",
                initial_code=FilesDict({"hello.py": "print('Hello, world!')"}),
                command="python hello.py",
                prompt="Change the code in hello.py to print 'Hello, human!'",
                assertions={
                    "correct output": lambda assertable: assertable.stdout
                    == "Hello, human!\n",
                    "correct file": lambda assertable: assertable.files[
                        "hello.py"
                    ].strip()
                    == "print('Hello, human!')",
                },
            ),
            Task(
                name="hello-patch",
                initial_code=FilesDict({"hello.py": "print('Hello, world!')"}),
                command="python hello.py",
                prompt="Patch the code in hello.py to print 'Hello, human!'",
                assertions={
                    "correct output": lambda assertable: assertable.stdout
                    == "Hello, human!\n",
                    "correct file": lambda assertable: assertable.files[
                        "hello.py"
                    ].strip()
                    == "print('Hello, human!')",
                },
            ),
            Task(
                name="hello-ask",
                initial_code=FilesDict({"hello.py": "print('Hello, world!')"}),
                command="echo 'Erik' | python hello.py",
                prompt="modify hello.py to ask the user for their name and print 'Hello, <name>!'. don't try to execute it",
                assertions={
                    "correct output": lambda assertable: "Hello, Erik!"
                    in assertable.stdout,
                },
            ),
            Task(
                name="prime100",
                initial_code=FilesDict(
                    {}
                ),  # Empty dictionary since no initial code is provided
                command="python prime.py",
                prompt="write a script prime.py that computes and prints the 100th prime number",
                assertions={
                    "correct output": lambda assertable: "541"
                    in assertable.stdout.split(),
                },
            ),
            Task(
                name="init-git",
                initial_code=FilesDict(
                    {}
                ),  # Empty dictionary since no initial code is provided
                command="git status",
                prompt="initialize a git repository, write a main.py file, and commit it",
                assertions={
                    "clean exit": lambda assertable: assertable.process.returncode == 0,
                    "clean working tree": lambda assertable: "nothing to commit, working tree clean"
                    in assertable.stdout,
                    "main.py exists": lambda assertable: "main.py" in assertable.files,
                    "we have a commit": lambda assertable: "No commits yet"
                    not in assertable.stdout,
                },
            ),
        ],
    )
