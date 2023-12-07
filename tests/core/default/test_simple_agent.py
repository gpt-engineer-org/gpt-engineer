import pytest
import tempfile
from gpt_engineer.core.ai import AI
from gpt_engineer.core.default.simple_agent import SimpleAgent
from gpt_engineer.core.files_dict import FilesDict
import os

from gpt_engineer.core.default.disk_execution_env import DiskExecutionEnv
from gpt_engineer.core.default.paths import ENTRYPOINT_FILE
from tests.caching_ai import CachingAI

from gpt_engineer.core.chat_to_files import (
    chat_to_files_dict,
    Edit,
    parse_edits,
    apply_edits,
)
from gpt_engineer.core.chat_to_files import logger as parse_logger
import logging


def test_init():
    temp_dir = tempfile.mkdtemp()

    lean_agent = SimpleAgent.with_default_config(temp_dir, CachingAI())
    outfile = "output.txt"
    code = lean_agent.init(
        f"Make a program that prints 'Hello World!' to a file called '{outfile}'"
    )

    env = DiskExecutionEnv()
    env.upload(code).run(f"bash {ENTRYPOINT_FILE}")
    code = env.download()

    assert outfile in code
    assert code[outfile] == "Hello World!"


def test_improve():
    temp_dir = tempfile.mkdtemp()
    code = FilesDict(
        {
            "main.py": "def write_hello_world_to_file(filename):\n    \"\"\"\n    Writes 'Hello World!' to the specified file.\n    \n    :param filename: The name of the file to write to.\n    \"\"\"\n    with open(filename, 'w') as file:\n        file.write('Hello World!')\n\nif __name__ == \"__main__\":\n    output_filename = 'output.txt'\n    write_hello_world_to_file(output_filename)",
            "requirements.txt": "# No dependencies required",
            "run.sh": "python3 main.py\n",
        }
    )
    lean_agent = SimpleAgent.with_default_config(temp_dir, CachingAI())
    lean_agent.improve(
        code,
        "Change the program so that it prints '!dlroW olleH' instead of 'Hello World!'",
        f"bash {ENTRYPOINT_FILE}",
    )

    env = DiskExecutionEnv()
    env.upload(code).run(f"bash {ENTRYPOINT_FILE}")
    code = env.download()

    outfile = "output.txt"
    assert outfile in code
    assert code[outfile] == "!dlroW olleH"


if __name__ == "__main__":
    pytest.main()
