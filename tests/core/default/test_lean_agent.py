import pytest
import tempfile
from gpt_engineer.core.ai import AI
from gpt_engineer.core.default.lean_agent import LeanAgent
import os

from gpt_engineer.core.chat_to_files import parse_chat, Edit, parse_edits, apply_edits
from gpt_engineer.core.chat_to_files import logger as parse_logger
import logging


def test_init():
    temp_dir = tempfile.mkdtemp()
    lean_agent = LeanAgent.with_default_config(temp_dir)
    outfile = "output.txt"
    file_path = os.path.join(temp_dir, outfile)
    code = lean_agent.init(
        f"Make a program that prints 'Hello World!' to a file called '{outfile}'"
    )
    assert os.path.isfile(file_path)
    with open(file_path, "r") as file:
        assert file.read().strip() == "Hello World!"


def test_improve():
    string = '\nmain.py\n```\nfrom writer import FileWriter\n\ndef main():\n    file_writer = FileWriter(\'output.txt\')\n    file_writer.write(\'Hello World!\')\n\nif __name__ == \'__main__\':\n    main()\n            ```\n            \n\n\nwriter.py\n```\nclass FileWriter:\n    def __init__(self, file_path):\n        """\n        Initialize the FileWriter with a path to the file.\n        """\n        self.file_path = file_path\n\n    def write(self, content):\n        """\n        Write the given content to the file.\n        """\n        with open(self.file_path, \'w\') as file:\n            file.write(content)\n            ```\n            \n\n\nrequirements.txt\n```\n# No dependencies required\n            ```\n            \n\n\nrun.sh\n```\n# a) Since there are no dependencies, we don\'t need to install anything.\n\n# b) Run the main.py script\npython main.py\n\n            ```\n            \n'

    # now try and improve the program
    print(code.to_chat())
    code = lean_agent.improve(
        "Change the program so that it prints '!dlroW olleH' instead of 'Hello World!'",
        code,
    )
    assert os.path.isfile(file_path)
    with open(file_path, "r") as file:
        file_content = file.read().strip()
        assert file_content == "!dlroW olleH"


if __name__ == "__main__":
    pytest.main()
