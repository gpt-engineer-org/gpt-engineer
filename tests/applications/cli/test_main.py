import os
import shutil
import tempfile

from unittest.mock import patch

import pytest

import gpt_engineer.applications.cli.main as main

from gpt_engineer.applications.cli.main import load_prompt
from gpt_engineer.core.default.disk_execution_env import DiskExecutionEnv
from gpt_engineer.core.default.disk_memory import DiskMemory
from gpt_engineer.core.default.paths import ENTRYPOINT_FILE, META_DATA_REL_PATH
from gpt_engineer.core.prompt import Prompt
from tests.caching_ai import CachingAI

main.AI = CachingAI


def simplified_main(path: str, mode: str = ""):
    model = "gpt-4-1106-preview"
    lite_mode = False
    clarify_mode = False
    improve_mode = False
    self_heal_mode = False
    azure_endpoint = ""
    verbose = False
    if mode == "lite":
        lite_mode = True
    elif mode == "clarify":
        clarify_mode = True
    elif mode == "improve":
        improve_mode = True
    elif mode == "self-heal":
        self_heal_mode = True
    main.main(
        path,
        model=model,
        lite_mode=lite_mode,
        clarify_mode=clarify_mode,
        improve_mode=improve_mode,
        self_heal_mode=self_heal_mode,
        azure_endpoint=azure_endpoint,
        use_custom_preprompts=False,
        prompt_file="prompt",
        image_directory="",
        entrypoint_prompt_file="",
        use_cache=False,
        verbose=verbose,
        llm_via_clipboard=False,
    )


def input_generator():
    yield "y"  # First response
    while True:
        yield "n"  # Subsequent responses


prompt_text = "Make a python program that writes 'hello' to a file called 'output.txt'"


class TestMain:
    #  Runs gpt-engineer with default settings and generates a project in the specified path.
    def test_default_settings_generate_project(self, tmp_path, monkeypatch):
        gen = input_generator()
        monkeypatch.setattr("builtins.input", lambda _: next(gen))
        p = tmp_path / "projects/example"
        p.mkdir(parents=True)
        (p / "prompt").write_text(prompt_text)
        simplified_main(str(p), "")
        ex_env = DiskExecutionEnv(path=p)
        ex_env.run(f"bash {ENTRYPOINT_FILE}")
        assert (p / "output.txt").exists()
        text = (p / "output.txt").read_text().strip()
        assert text == "hello"

    #  Runs gpt-engineer with improve mode and improves an existing project in the specified path.
    def test_improve_existing_project(self, tmp_path, monkeypatch):
        def improve_generator():
            yield "y"
            while True:
                yield "n"  # Subsequent responses

        gen = improve_generator()
        monkeypatch.setattr("builtins.input", lambda _: next(gen))
        p = tmp_path / "projects/example"
        p.mkdir(parents=True)
        (p / "prompt").write_text(prompt_text)
        (p / "main.py").write_text("The program will be written in this file")
        meta_p = p / META_DATA_REL_PATH
        meta_p.mkdir(parents=True)
        (meta_p / "file_selection.toml").write_text(
            """
        [files]
        "main.py" = "selected"
                    """
        )
        os.environ["GPTE_TEST_MODE"] = "True"
        simplified_main(str(p), "improve")
        DiskExecutionEnv(path=p)
        del os.environ["GPTE_TEST_MODE"]

    #  Runs gpt-engineer with lite mode and generates a project with only the main prompt.
    def test_lite_mode_generate_project(self, tmp_path, monkeypatch):
        gen = input_generator()
        monkeypatch.setattr("builtins.input", lambda _: next(gen))
        p = tmp_path / "projects/example"
        p.mkdir(parents=True)
        (p / "prompt").write_text(prompt_text)
        simplified_main(str(p), "lite")
        ex_env = DiskExecutionEnv(path=p)
        ex_env.run(f"bash {ENTRYPOINT_FILE}")
        assert (p / "output.txt").exists()
        text = (p / "output.txt").read_text().strip()
        assert text == "hello"

    #  Runs gpt-engineer with clarify mode and generates a project after discussing the specification with the AI.
    def test_clarify_mode_generate_project(self, tmp_path, monkeypatch):
        gen = input_generator()
        monkeypatch.setattr("builtins.input", lambda _: next(gen))
        p = tmp_path / "projects/example"
        p.mkdir(parents=True)
        (p / "prompt").write_text(prompt_text)
        simplified_main(str(p), "clarify")
        ex_env = DiskExecutionEnv(path=p)
        ex_env.run(f"bash {ENTRYPOINT_FILE}")
        assert (p / "output.txt").exists()
        text = (p / "output.txt").read_text().strip()
        assert text == "hello"

    #  Runs gpt-engineer with self-heal mode and generates a project after discussing the specification with the AI and self-healing the code.
    def test_self_heal_mode_generate_project(self, tmp_path, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: next(input_generator()))
        p = tmp_path / "projects/example"
        p.mkdir(parents=True)
        (p / "prompt").write_text(prompt_text)
        simplified_main(str(p), "self-heal")
        ex_env = DiskExecutionEnv(path=p)
        ex_env.run(f"bash {ENTRYPOINT_FILE}")
        assert (p / "output.txt").exists()
        text = (p / "output.txt").read_text().strip()
        assert text == "hello"

    #  Tests the creation of a log file in improve mode.


class TestLoadPrompt:
    #  Load prompt from existing file in input_repo
    def test_load_prompt_existing_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            input_repo = DiskMemory(tmp_dir)
            prompt_file = "prompt.txt"
            prompt_content = "This is the prompt"
            input_repo[prompt_file] = prompt_content

            improve_mode = False
            image_directory = ""

            result = load_prompt(input_repo, improve_mode, prompt_file, image_directory)

            assert isinstance(result, Prompt)
            assert result.text == prompt_content
            assert result.image_urls is None

    #  Prompt file does not exist in input_repo, and improve_mode is False
    def test_load_prompt_no_file_improve_mode_false(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            input_repo = DiskMemory(tmp_dir)
            prompt_file = "prompt.txt"

            improve_mode = False
            image_directory = ""

            with patch(
                "builtins.input",
                return_value="What application do you want gpt-engineer to generate?",
            ):
                result = load_prompt(
                    input_repo, improve_mode, prompt_file, image_directory
                )

            assert isinstance(result, Prompt)
            assert (
                result.text == "What application do you want gpt-engineer to generate?"
            )
            assert result.image_urls is None

    #  Prompt file is a directory
    def test_load_prompt_directory_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            input_repo = DiskMemory(tmp_dir)
            prompt_file = os.path.join(tmp_dir, "prompt")

            os.makedirs(os.path.join(tmp_dir, prompt_file))

            improve_mode = False
            image_directory = ""

            with pytest.raises(ValueError):
                load_prompt(input_repo, improve_mode, prompt_file, image_directory)

    #  Prompt file is empty
    def test_load_prompt_empty_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            input_repo = DiskMemory(tmp_dir)
            prompt_file = "prompt.txt"
            input_repo[prompt_file] = ""

            improve_mode = False
            image_directory = ""

            with patch(
                "builtins.input",
                return_value="What application do you want gpt-engineer to generate?",
            ):
                result = load_prompt(
                    input_repo, improve_mode, prompt_file, image_directory
                )

            assert isinstance(result, Prompt)
            assert (
                result.text == "What application do you want gpt-engineer to generate?"
            )
            assert result.image_urls is None

    #  image_directory does not exist in input_repo
    def test_load_prompt_no_image_directory(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            input_repo = DiskMemory(tmp_dir)
            prompt_file = "prompt.txt"
            prompt_content = "This is the prompt"
            input_repo[prompt_file] = prompt_content

            improve_mode = False
            image_directory = "tests/test_data"
            shutil.copytree(image_directory, os.path.join(tmp_dir, image_directory))

            result = load_prompt(input_repo, improve_mode, prompt_file, image_directory)

            assert isinstance(result, Prompt)
            assert result.text == prompt_content
            assert "mona_lisa.jpg" in result.image_urls


#     def test_log_creation_in_improve_mode(self, tmp_path, monkeypatch):
#         def improve_generator():
#             yield "y"
#             while True:
#                 yield "n"  # Subsequent responses
#
#         gen = improve_generator()
#         monkeypatch.setattr("builtins.input", lambda _: next(gen))
#         p = tmp_path / "projects/example"
#         p.mkdir(parents=True)
#         (p / "prompt").write_text(prompt_text)
#         (p / "main.py").write_text("The program will be written in this file")
#         meta_p = p / META_DATA_REL_PATH
#         meta_p.mkdir(parents=True)
#         (meta_p / "file_selection.toml").write_text(
#             """
#         [files]
#         "main.py" = "selected"
#                     """
#         )
#         os.environ["GPTE_TEST_MODE"] = "True"
#         simplified_main(str(p), "improve")
#         DiskExecutionEnv(path=p)
#         assert (
#             (p / f".gpteng/memory/{DEBUG_LOG_FILE}").read_text().strip()
#             == """UPLOADED FILES:
# ```
# File: main.py
# 1 The program will be written in this file
#
# ```
# PROMPT:
# Make a python program that writes 'hello' to a file called 'output.txt'
# CONSOLE OUTPUT:"""
#         )
#         del os.environ["GPTE_TEST_MODE"]
#
#     def test_log_creation_in_improve_mode_with_failing_diff(
#         self, tmp_path, monkeypatch
#     ):
#         def improve_generator():
#             yield "y"
#             while True:
#                 yield "n"  # Subsequent responses
#
#         def mock_salvage_correct_hunks(
#             messages: List, files_dict: FilesDict, error_message: List
#         ) -> FilesDict:
#             # create a falling diff
#             messages[
#                 -1
#             ].content = """To create a Python program that writes 'hello' to a file called 'output.txt', we will need to perform the following steps:
#
# 1. Open the file 'output.txt' in write mode.
# 2. Write the string 'hello' to the file.
# 3. Close the file to ensure the data is written and the file is not left open.
#
# Here is the implementation of the program in the `main.py` file:
#
# ```diff
# --- main.py
# +++ main.py
# @@ -0,0 +1,9 @@
# -create falling diff
# ```
#
# This concludes a fully working implementation."""
#             # Call the original function with modified messages or define your own logic
#             return salvage_correct_hunks(messages, files_dict, error_message)
#
#         gen = improve_generator()
#         monkeypatch.setattr("builtins.input", lambda _: next(gen))
#         monkeypatch.setattr(
#             "gpt_engineer.core.default.steps.salvage_correct_hunks",
#             mock_salvage_correct_hunks,
#         )
#         p = tmp_path / "projects/example"
#         p.mkdir(parents=True)
#         (p / "prompt").write_text(prompt_text)
#         (p / "main.py").write_text("The program will be written in this file")
#         meta_p = p / META_DATA_REL_PATH
#         meta_p.mkdir(parents=True)
#         (meta_p / "file_selection.toml").write_text(
#             """
#         [files]
#         "main.py" = "selected"
#                     """
#         )
#         os.environ["GPTE_TEST_MODE"] = "True"
#         simplified_main(str(p), "improve")
#         DiskExecutionEnv(path=p)
#         assert (
#             (p / f".gpteng/memory/{DEBUG_LOG_FILE}").read_text().strip()
#             == """UPLOADED FILES:
# ```
# File: main.py
# 1 The program will be written in this file
#
# ```
# PROMPT:
# Make a python program that writes 'hello' to a file called 'output.txt'
# CONSOLE OUTPUT:
# Invalid hunk: @@ -0,0 +1,9 @@
# -create falling diff
#
# Invalid hunk: @@ -0,0 +1,9 @@
# -create falling diff"""
#         )
#         del os.environ["GPTE_TEST_MODE"]
#
#     def test_log_creation_in_improve_mode_with_unexpected_exceptions(
#         self, tmp_path, monkeypatch
#     ):
#         def improve_generator():
#             yield "y"
#             while True:
#                 yield "n"  # Subsequent responses
#
#         def mock_salvage_correct_hunks(
#             messages: List, files_dict: FilesDict, error_message: List
#         ) -> FilesDict:
#             raise Exception("Mock exception in salvage_correct_hunks")
#
#         gen = improve_generator()
#         monkeypatch.setattr("builtins.input", lambda _: next(gen))
#         monkeypatch.setattr(
#             "gpt_engineer.core.default.steps.salvage_correct_hunks",
#             mock_salvage_correct_hunks,
#         )
#         p = tmp_path / "projects/example"
#         p.mkdir(parents=True)
#         (p / "prompt").write_text(prompt_text)
#         (p / "main.py").write_text("The program will be written in this file")
#         meta_p = p / META_DATA_REL_PATH
#         meta_p.mkdir(parents=True)
#         (meta_p / "file_selection.toml").write_text(
#             """
#         [files]
#         "main.py" = "selected"
#                     """
#         )
#         os.environ["GPTE_TEST_MODE"] = "True"
#         simplified_main(str(p), "improve")
#         DiskExecutionEnv(path=p)
#         assert (
#             (p / f".gpteng/memory/{DEBUG_LOG_FILE}").read_text().strip()
#             == """UPLOADED FILES:
# ```
# File: main.py
# 1 The program will be written in this file
#
# ```
# PROMPT:
# Make a python program that writes 'hello' to a file called 'output.txt'
# CONSOLE OUTPUT:
# Error while improving the project: Mock exception in salvage_correct_hunks"""
#         )
#         del os.environ["GPTE_TEST_MODE"]
