import textwrap

from gpt_engineer.core.chat_to_files import to_files
from gpt_engineer.core.db import DB, DBs

from typing import Union
from pathlib import Path


class StubDB(DB):
    def __init__(self, path: Union[str, Path]):
        self.data = {}

    def __setitem__(self, key, value):
        self.data[key] = value

    def __getitem__(self, key):
        return self.data[key]


def test_to_files():
    chat = textwrap.dedent(
        """
    This is a sample program.

    file1.py
    ```python
    print("Hello, World!")
    ```

    file2.py
    ```python
    def add(a, b):
        return a + b
    ```
    """
    )

    dbs = DBs(
        StubDB("/tmp1"),
        StubDB("/tmp2"),
        StubDB("/tmp3"),
        StubDB("/tmp4"),
        StubDB("/tmp5"),
        StubDB("/tmp6"),
        StubDB("/tmp7"),
    )
    to_files(chat, dbs)

    assert dbs.memory["all_output.txt"] == chat

    expected_files = {
        "file1.py": 'print("Hello, World!")\n',
        "file2.py": "def add(a, b):\n    return a + b\n",
        "README.md": "\nThis is a sample program.\n\nfile1.py\n",
    }

    for file_name, file_content in expected_files.items():
        assert dbs.workspace[file_name] == file_content


def test_to_files_with_square_brackets():
    chat = textwrap.dedent(
        """
    This is a sample program.

    [file1.py]
    ```python
    print("Hello, World!")
    ```

    [file2.py]
    ```python
    def add(a, b):
        return a + b
    ```
    """
    )

    dbs = DBs(
        StubDB("/tmp1"),
        StubDB("/tmp2"),
        StubDB("/tmp3"),
        StubDB("/tmp4"),
        StubDB("/tmp5"),
        StubDB("/tmp6"),
        StubDB("/tmp7"),
    )
    to_files(chat, dbs)

    assert dbs.memory["all_output.txt"] == chat

    expected_files = {
        "file1.py": 'print("Hello, World!")\n',
        "file2.py": "def add(a, b):\n    return a + b\n",
        "README.md": "\nThis is a sample program.\n\n[file1.py]\n",
    }

    for file_name, file_content in expected_files.items():
        assert dbs.workspace[file_name] == file_content


def test_files_with_brackets_in_name():
    chat = textwrap.dedent(
        """
    This is a sample program.

    [id].jsx
    ```javascript
    console.log("Hello, World!")
    ```
    """
    )

    dbs = DBs(
        StubDB("/tmp1"),
        StubDB("/tmp2"),
        StubDB("/tmp3"),
        StubDB("/tmp4"),
        StubDB("/tmp5"),
        StubDB("/tmp6"),
        StubDB("/tmp7"),
    )
    to_files(chat, dbs)

    assert dbs.memory["all_output.txt"] == chat

    expected_files = {
        "[id].jsx": 'console.log("Hello, World!")\n',
        "README.md": "\nThis is a sample program.\n\n[id].jsx\n",
    }

    for file_name, file_content in expected_files.items():
        assert dbs.workspace[file_name] == file_content


def test_files_with_file_colon():
    chat = textwrap.dedent(
        """
    This is a sample program.

    [FILE: file1.py]
    ```python
    print("Hello, World!")
    ```
    """
    )

    dbs = DBs(
        StubDB("/tmp1"),
        StubDB("/tmp2"),
        StubDB("/tmp3"),
        StubDB("/tmp4"),
        StubDB("/tmp5"),
        StubDB("/tmp6"),
        StubDB("/tmp7"),
    )
    to_files(chat, dbs)

    assert dbs.memory["all_output.txt"] == chat

    expected_files = {
        "file1.py": 'print("Hello, World!")\n',
        "README.md": "\nThis is a sample program.\n\n[FILE: file1.py]\n",
    }

    for file_name, file_content in expected_files.items():
        assert dbs.workspace[file_name] == file_content


def test_files_with_back_tick():
    chat = textwrap.dedent(
        """
    This is a sample program.

    `file1.py`
    ```python
    print("Hello, World!")
    ```
    """
    )

    dbs = DBs(
        StubDB("/tmp1"),
        StubDB("/tmp2"),
        StubDB("/tmp3"),
        StubDB("/tmp4"),
        StubDB("/tmp5"),
        StubDB("/tmp6"),
        StubDB("/tmp7"),
    )
    to_files(chat, dbs)

    assert dbs.memory["all_output.txt"] == chat

    expected_files = {
        "file1.py": 'print("Hello, World!")\n',
        "README.md": "\nThis is a sample program.\n\n`file1.py`\n",
    }

    for file_name, file_content in expected_files.items():
        assert dbs.workspace[file_name] == file_content


def test_files_with_newline_between():
    chat = textwrap.dedent(
        """
    This is a sample program.

    file1.py

    ```python
    print("Hello, World!")
    ```
    """
    )

    dbs = DBs(
        StubDB("/tmp1"),
        StubDB("/tmp2"),
        StubDB("/tmp3"),
        StubDB("/tmp4"),
        StubDB("/tmp5"),
        StubDB("/tmp6"),
        StubDB("/tmp7"),
    )
    to_files(chat, dbs)

    assert dbs.memory["all_output.txt"] == chat

    expected_files = {
        "file1.py": 'print("Hello, World!")\n',
        "README.md": "\nThis is a sample program.\n\nfile1.py\n\n",
    }

    for file_name, file_content in expected_files.items():
        assert dbs.workspace[file_name] == file_content


def test_files_with_newline_between_header():
    chat = textwrap.dedent(
        """
    This is a sample program.

    ## file1.py

    ```python
    print("Hello, World!")
    ```
    """
    )

    dbs = DBs(
        StubDB("/tmp1"),
        StubDB("/tmp2"),
        StubDB("/tmp3"),
        StubDB("/tmp4"),
        StubDB("/tmp5"),
        StubDB("/tmp6"),
        StubDB("/tmp7"),
    )
    to_files(chat, dbs)

    assert dbs.memory["all_output.txt"] == chat

    expected_files = {
        "file1.py": 'print("Hello, World!")\n',
        "README.md": "\nThis is a sample program.\n\n## file1.py\n\n",
    }

    for file_name, file_content in expected_files.items():
        assert dbs.workspace[file_name] == file_content


if __name__ == "__main__":
    test_to_files()
    test_to_files_with_square_brackets()
    test_files_with_brackets_in_name()
    test_files_with_file_colon()
    test_files_with_back_tick()
    test_files_with_newline_between()
    test_files_with_newline_between_header()
    print("Everything passed")
