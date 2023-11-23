import pytest
import tempfile
from tests.caching_ai import CachingAI
from gpt_engineer.applications.cli.cli_agent import CliAgent
from gpt_engineer.tools.custom_steps import self_heal, lite_gen, clarified_gen
from gpt_engineer.core.code import Code
import os

from gpt_engineer.core.chat_to_files import parse_chat, Edit, parse_edits, apply_edits
from gpt_engineer.core.chat_to_files import logger as parse_logger
import logging


def test_init_standard_config(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda: "y")
    temp_dir = tempfile.mkdtemp()
    cli_agent = CliAgent.with_default_config(temp_dir, CachingAI())
    outfile = "output.txt"
    file_path = os.path.join(temp_dir, outfile)
    code = cli_agent.init(
        f"Make a program that prints 'Hello World!' to a file called '{outfile}'"
    )
    assert os.path.isfile(file_path)
    with open(file_path, "r") as file:
        assert file.read().strip() == "Hello World!"

def test_init_lite_config(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda: "y")
    temp_dir = tempfile.mkdtemp()
    cli_agent = CliAgent.with_default_config(temp_dir, CachingAI(), code_gen_fn=lite_gen)
    outfile = "output.txt"
    file_path = os.path.join(temp_dir, outfile)
    code = cli_agent.init(
        f"Make a program that prints 'Hello World!' to a file called '{outfile}'"
    )
    assert os.path.isfile(file_path)
    with open(file_path, "r") as file:
        assert file.read().strip() == "Hello World!"

def test_init_clarified_gen_config(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda: "y")
    temp_dir = tempfile.mkdtemp()
    cli_agent = CliAgent.with_default_config(temp_dir, CachingAI(), code_gen_fn=clarified_gen)
    outfile = "output.txt"
    file_path = os.path.join(temp_dir, outfile)
    code = cli_agent.init(
        f"Make a program that prints 'Hello World!' to a file called '{outfile} either using python or javascript'"
    )
    assert os.path.isfile(file_path)
    with open(file_path, "r") as file:
        assert file.read().strip() == "Hello World!"

def test_init_self_heal_config(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda: "y")
    temp_dir = tempfile.mkdtemp()

    cli_agent = CliAgent.with_default_config(temp_dir, CachingAI(), execute_entrypoint_fn=self_heal)
    outfile = "output.txt"
    file_path = os.path.join(temp_dir, outfile)
    code = cli_agent.init(
        f"Make a program that prints 'Hello World!' to a file called '{outfile}' (sf_var_manipulated_cache)"
    )
    assert os.path.isfile(file_path)
    with open(file_path, "r") as file:
        assert file.read().strip() == "Hello World!"


def test_improve_standard_config(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda: "y")
    temp_dir = tempfile.mkdtemp()
    code = Code(
        {
            "main.py": "def write_hello_world_to_file(filename):\n    \"\"\"\n    Writes 'Hello World!' to the specified file.\n    \n    :param filename: The name of the file to write to.\n    \"\"\"\n    with open(filename, 'w') as file:\n        file.write('Hello World!')\n\nif __name__ == \"__main__\":\n    output_filename = 'output.txt'\n    write_hello_world_to_file(output_filename)",
            "requirements.txt": "# No dependencies required",
            "run.sh": "python3 main.py\n",
        }
    )
    cli_agent = CliAgent.with_default_config(temp_dir, CachingAI())
    cli_agent.improve(
        code,
        "Change the program so that it prints '!dlroW olleH' instead of 'Hello World!'",
    )
    outfile = "output.txt"
    file_path = os.path.join(temp_dir, outfile)
    assert os.path.isfile(file_path)
    with open(file_path, "r") as file:
        file_content = file.read().strip()
        assert file_content == "!dlroW olleH"




if __name__ == "__main__":
    pytest.main()
