import os
import shutil

from typing import List

import pytest

from langchain_core.messages import AIMessage

from gpt_engineer.core.default.disk_memory import DiskMemory
from gpt_engineer.core.default.paths import memory_path
from gpt_engineer.core.default.steps import salvage_correct_hunks
from gpt_engineer.core.files_dict import FilesDict

TEST_FILES_DIR = os.path.dirname(os.path.abspath(__file__))
memory = DiskMemory(memory_path("."))


def get_file_content(file_path: str) -> str:
    with open(
        os.path.join(TEST_FILES_DIR, "improve_function_test_cases", file_path), "r"
    ) as f:
        return f.read()


def message_builder(chat_path: str) -> List[AIMessage]:
    chat_content = get_file_content(chat_path)

    json = {
        "lc": 1,
        "type": "constructor",
        "id": ["langchain", "schema", "messages", "AIMessage"],
        "kwargs": {
            "content": chat_content,
            "additional_kwargs": {},
            "response_metadata": {"finish_reason": "stop"},
            "name": None,
            "id": None,
            "example": False,
        },
    }

    return [AIMessage(**json["kwargs"])]


def test_validation_and_apply_complex_diff():
    files = FilesDict({"taskmaster.py": get_file_content("task_master_code")})
    salvage_correct_hunks(message_builder("task_master_chat"), files, memory)


def test_validation_and_apply_long_diff():
    files = FilesDict({"VMClonetest.ps1": get_file_content("wheaties_example_code")})
    salvage_correct_hunks(message_builder("wheaties_example_chat"), files, memory)


def test_validation_and_apply_wrong_diff():
    files = FilesDict(
        {"src/components/SocialLinks.tsx": get_file_content("vgvishesh_example_code")}
    )
    salvage_correct_hunks(message_builder("vgvishesh_example_chat"), files, memory)


def test_validation_and_apply_non_change_diff():
    files = FilesDict({"src/App.tsx": get_file_content("vgvishesh_example_2_code")})
    salvage_correct_hunks(message_builder("vgvishesh_example_2_chat"), files, memory)


def test_validation_and_apply_diff_on_apps_benchmark_6():
    files = FilesDict({"main.py": get_file_content("apps_benchmark_6_code")})
    salvage_correct_hunks(message_builder("apps_benchmark_6_chat"), files, memory)


def test_validation_and_apply_diff_on_apps_benchmark_6_v2():
    files = FilesDict({"main.py": get_file_content("apps_benchmark_6_v2_code")})
    salvage_correct_hunks(message_builder("apps_benchmark_6_v2_chat"), files, memory)


def test_create_two_new_files():
    files = FilesDict({"main.py": get_file_content("create_two_new_files_code")})
    salvage_correct_hunks(message_builder("create_two_new_files_chat"), files, memory)


def test_theo_case():
    files = FilesDict({"dockerfile": get_file_content("theo_case_code")})
    updated_files, _ = salvage_correct_hunks(
        message_builder("theo_case_chat"), files, memory
    )
    print(updated_files["dockerfile"])
    print(updated_files["run.py"])


def test_zbf_yml_missing():
    files = FilesDict(
        {"src/main/resources/application.yml": get_file_content("zbf_yml_missing_code")}
    )
    updated_files, _ = salvage_correct_hunks(
        message_builder("zbf_yml_missing_chat"), files, memory
    )
    print(updated_files["src/main/resources/application.yml"])
    print(updated_files["src/main/resources/application-local.yml"])


def test_clean_up_folder(clean_up_folder):
    # The folder should be deleted after the test is run
    assert True


@pytest.fixture
def clean_up_folder():
    yield
    # Teardown code: delete a folder and all its contents
    print("cleaning up")
    folder_path = os.path.join(os.path.dirname(__file__), ".gpteng")
    shutil.rmtree(folder_path, ignore_errors=True)


if __name__ == "__main__":
    pytest.main()
