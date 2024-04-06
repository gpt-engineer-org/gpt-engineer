import dataclasses
import functools
import inspect
import os
import shutil
import tempfile

from argparse import Namespace
from unittest.mock import patch

import pytest
import typer

import gpt_engineer.applications.cli.main as main

from gpt_engineer.applications.cli.main import load_prompt
from gpt_engineer.core.default.disk_memory import DiskMemory
from gpt_engineer.core.prompt import Prompt


@functools.wraps(dataclasses.make_dataclass)
def dcommand(typer_f, **kwargs):
    required = True

    def field_desc(name, param):
        nonlocal required

        t = param.annotation or "typing.Any"
        if param.default.default is not ...:
            required = False
            return name, t, dataclasses.field(default=param.default.default)

        if not required:
            raise ValueError("Required value after optional")

        return name, t

    kwargs.setdefault("cls_name", typer_f.__name__)

    params = inspect.signature(typer_f).parameters
    kwargs["fields"] = [field_desc(k, v) for k, v in params.items()]

    @functools.wraps(typer_f)
    def dcommand_decorator(function_or_class):
        assert callable(function_or_class)

        ka = dict(kwargs)
        ns = Namespace(**(ka.pop("namespace", None) or {}))
        if isinstance(function_or_class, type):
            ka["bases"] = *ka.get("bases", ()), function_or_class
        else:
            ns.__call__ = function_or_class

        ka["namespace"] = vars(ns)
        return dataclasses.make_dataclass(**ka)

    return dcommand_decorator


@dcommand(main.main)
class DefaultArgumentsMain:
    def __call__(self):
        attribute_dict = vars(self)
        main.main(**attribute_dict)


def input_generator():
    yield "y"  # First response
    while True:
        yield "n"  # Subsequent responses


prompt_text = "Make a python program that writes 'hello' to a file called 'output.txt'"


class TestMain:
    #  Runs gpt-engineer cli interface for many parameter configurations, BUT DOES NOT CODEGEN! Only testing cli.
    def test_default_settings_generate_project(self, tmp_path, monkeypatch):
        p = tmp_path / "projects/example"
        p.mkdir(parents=True)
        (p / "prompt").write_text(prompt_text)
        args = DefaultArgumentsMain(str(p), llm_via_clipboard=True, no_execution=True)
        args()

    #  Runs gpt-engineer with improve mode and improves an existing project in the specified path.
    def test_improve_existing_project(self, tmp_path, monkeypatch):
        p = tmp_path / "projects/example"
        p.mkdir(parents=True)
        (p / "prompt").write_text(prompt_text)
        args = DefaultArgumentsMain(
            str(p), improve_mode=True, llm_via_clipboard=True, no_execution=True
        )
        args()

        # def improve_generator():
        #     yield "y"
        #     while True:
        #         yield "n"  # Subsequent responses
        #
        # gen = improve_generator()
        # monkeypatch.setattr("builtins.input", lambda _: next(gen))
        # p = tmp_path / "projects/example"
        # p.mkdir(parents=True)
        # (p / "prompt").write_text(prompt_text)
        # (p / "main.py").write_text("The program will be written in this file")
        # meta_p = p / META_DATA_REL_PATH
        # meta_p.mkdir(parents=True)
        # (meta_p / "file_selection.toml").write_text(
        #     """
        # [files]
        # "main.py" = "selected"
        #             """
        # )
        # os.environ["GPTE_TEST_MODE"] = "True"
        # simplified_main(str(p), "improve")
        # DiskExecutionEnv(path=p)
        # del os.environ["GPTE_TEST_MODE"]

    #  Runs gpt-engineer with lite mode and generates a project with only the main prompt.
    def test_lite_mode_generate_project(self, tmp_path, monkeypatch):
        p = tmp_path / "projects/example"
        p.mkdir(parents=True)
        (p / "prompt").write_text(prompt_text)
        args = DefaultArgumentsMain(
            str(p), lite_mode=True, llm_via_clipboard=True, no_execution=True
        )
        args()

    #  Runs gpt-engineer with clarify mode and generates a project after discussing the specification with the AI.
    def test_clarify_mode_generate_project(self, tmp_path, monkeypatch):
        p = tmp_path / "projects/example"
        p.mkdir(parents=True)
        (p / "prompt").write_text(prompt_text)
        args = DefaultArgumentsMain(
            str(p), clarify_mode=True, llm_via_clipboard=True, no_execution=True
        )
        args()

    #  Runs gpt-engineer with self-heal mode and generates a project after discussing the specification with the AI and self-healing the code.
    def test_self_heal_mode_generate_project(self, tmp_path, monkeypatch):
        p = tmp_path / "projects/example"
        p.mkdir(parents=True)
        (p / "prompt").write_text(prompt_text)
        args = DefaultArgumentsMain(
            str(p), self_heal_mode=True, llm_via_clipboard=True, no_execution=True
        )
        args()

    def test_clarify_lite_improve_mode_generate_project(self, tmp_path, monkeypatch):
        p = tmp_path / "projects/example"
        p.mkdir(parents=True)
        (p / "prompt").write_text(prompt_text)
        args = DefaultArgumentsMain(
            str(p),
            improve_mode=True,
            lite_mode=True,
            clarify_mode=True,
            llm_via_clipboard=True,
            no_execution=True,
        )
        pytest.raises(typer.Exit, args)

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
