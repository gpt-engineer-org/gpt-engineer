import textwrap

from gpt_engineer.core.chat_to_files import to_files


def test_to_files():
    """
    Test the function to_files with a simple chat input.
    The chat input contains two files: file1.py and file2.py.
    """
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

    workspace = {}
    to_files(chat, workspace)

    assert workspace["all_output.txt"] == chat

    expected_files = {
        "file1.py": 'print("Hello, World!")\n',
        "file2.py": "def add(a, b):\n    return a + b\n",
        "README.md": "\nThis is a sample program.\n\nfile1.py\n",
    }

    for file_name, file_content in expected_files.items():
        assert workspace[file_name] == file_content


def test_to_files_with_square_brackets():
    """
    Test the function to_files with a chat input where the file names are enclosed in square brackets.
    The chat input contains two files: file1.py and file2.py.
    """
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
    workspace = {}
    to_files(chat, workspace)

    assert workspace["all_output.txt"] == chat

    expected_files = {
        "file1.py": 'print("Hello, World!")\n',
        "file2.py": "def add(a, b):\n    return a + b\n",
        "README.md": "\nThis is a sample program.\n\n[file1.py]\n",
    }

    for file_name, file_content in expected_files.items():
        assert workspace[file_name] == file_content


def test_files_with_brackets_in_name():
    """
    Test the function to_files with a chat input where the file name contains brackets.
    The chat input contains one file: [id].jsx.
    """
    chat = textwrap.dedent(
        """
    This is a sample program.

    [id].jsx
    ```javascript
    console.log("Hello, World!")
    ```
    """
    )

    workspace = {}
    to_files(chat, workspace)

    assert workspace["all_output.txt"] == chat

    expected_files = {
        "[id].jsx": 'console.log("Hello, World!")\n',
        "README.md": "\nThis is a sample program.\n\n[id].jsx\n",
    }

    for file_name, file_content in expected_files.items():
        assert workspace[file_name] == file_content


def test_files_with_file_colon():
    """
    Test the function to_files with a chat input where the file name is preceded by 'FILE:'.
    The chat input contains one file: file1.py.
    """
    chat = textwrap.dedent(
        """
    This is a sample program.

    [FILE: file1.py]
    ```python
    print("Hello, World!")
    ```
    """
    )

    workspace = {}
    to_files(chat, workspace)

    assert workspace["all_output.txt"] == chat

    expected_files = {
        "file1.py": 'print("Hello, World!")\n',
        "README.md": "\nThis is a sample program.\n\n[FILE: file1.py]\n",
    }

    for file_name, file_content in expected_files.items():
        assert workspace[file_name] == file_content


def test_files_with_back_tick():
    """
    Test the function to_files with a chat input where the file name is enclosed in back ticks.
    The chat input contains one file: file1.py.
    """
    chat = textwrap.dedent(
        """
    This is a sample program.

    `file1.py`
    ```python
    print("Hello, World!")
    ```
    """
    )

    workspace = {}
    to_files(chat, workspace)

    assert workspace["all_output.txt"] == chat

    expected_files = {
        "file1.py": 'print("Hello, World!")\n',
        "README.md": "\nThis is a sample program.\n\n`file1.py`\n",
    }

    for file_name, file_content in expected_files.items():
        assert workspace[file_name] == file_content


def test_files_with_newline_between():
    """
    Test the function to_files with a chat input where there is a newline between the file name and the file content.
    The chat input contains one file: file1.py.
    """
    chat = textwrap.dedent(
        """
    This is a sample program.

    file1.py

    ```python
    print("Hello, World!")
    ```
    """
    )

    workspace = {}
    to_files(chat, workspace)

    assert workspace["all_output.txt"] == chat

    expected_files = {
        "file1.py": 'print("Hello, World!")\n',
        "README.md": "\nThis is a sample program.\n\nfile1.py\n\n",
    }

    for file_name, file_content in expected_files.items():
        assert workspace[file_name] == file_content


def test_files_with_newline_between_header():
    """
    Test the function to_files with a chat input where there is a newline between the file name (which is a header) and the file content.
    The chat input contains one file: file1.py.
    """
    chat = textwrap.dedent(
        """
    This is a sample program.

    ## file1.py

    ```python
    print("Hello, World!")
    ```
    """
    )

    workspace = {}
    to_files(chat, workspace)

    assert workspace["all_output.txt"] == chat

    expected_files = {
        "file1.py": 'print("Hello, World!")\n',
        "README.md": "\nThis is a sample program.\n\n## file1.py\n\n",
    }

    for file_name, file_content in expected_files.items():
        assert workspace[file_name] == file_content
