import pytest
from gpt_engineer.core.chat_to_files import (
    chat_to_files_dict,
    Edit,
    parse_edits,
    apply_edits,
)
from gpt_engineer.core.chat_to_files import logger as parse_logger
import logging


def test_standard_input():
    chat = """
    Some text describing the code
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
    expected = {
        "file1.py": 'print("Hello, World!")',
        "file2.py": "def add(a, b):\n    return a + b",
    }
    assert chat_to_files_dict(chat) == expected


def test_no_code_blocks():
    chat = "Just some regular chat without code."
    expected = {}
    assert chat_to_files_dict(chat) == expected


def test_special_characters_in_filename():
    chat = """
    file[1].py
    ```python
    print("File 1")
    ```

    file`2`.py
    ```python
    print("File 2")
    ```
    """
    expected = {"file[1].py": 'print("File 1")', "file`2`.py": 'print("File 2")'}
    parsed = chat_to_files_dict(chat)
    assert parsed == expected


def test_empty_code_blocks():
    chat = """
    empty.py
    ```
    ```
    """
    expected = {"empty.py": ""}
    assert chat_to_files_dict(chat) == expected


def test_mixed_content():
    chat = """
    script.sh
    ```bash
    echo "Hello"
    ```

    script.py
    ```python
    print("World")
    ```
    """
    expected = {"script.sh": 'echo "Hello"', "script.py": 'print("World")'}
    assert chat_to_files_dict(chat) == expected


def test_filename_line_break():
    chat = """
    file1.py

    ```python
    print("Hello, World!")
    ```
    """
    expected = {"file1.py": 'print("Hello, World!")'}
    assert chat_to_files_dict(chat) == expected


def test_filename_in_backticks():
    chat = """
    `file1.py`
    ```python
    print("Hello, World!")
    ```
    """
    expected = {"file1.py": 'print("Hello, World!")'}
    assert chat_to_files_dict(chat) == expected


def test_filename_with_file_tag():
    chat = """
    [FILE: file1.py]
    ```python
    print("Hello, World!")
    ```
    """
    expected = {"file1.py": 'print("Hello, World!")'}
    assert chat_to_files_dict(chat) == expected


def test_filename_with_different_extension():
    chat = """
    [id].jsx
    ```javascript
    console.log("Hello, World!")
    ```
    """
    expected = {"[id].jsx": 'console.log("Hello, World!")'}
    assert chat_to_files_dict(chat) == expected


# Helper function to capture log messages
@pytest.fixture
def log_capture():
    class LogCaptureHandler(logging.Handler):
        def __init__(self):
            super().__init__()
            self.messages = []

        def emit(self, record):
            self.messages.append(record.getMessage())

    handler = LogCaptureHandler()
    parse_logger.addHandler(handler)
    yield handler
    parse_logger.removeHandler(handler)


def test_parse_with_additional_text():
    chat = """
Some introductory text.

```python
some/dir/example_1.py
<<<<<<< HEAD
    def mul(a,b)
=======
    def add(a,b):
>>>>>>> updated
```

Text between patches.

```python
some/dir/example_2.py
<<<<<<< HEAD
    class DBS:
        db = 'aaa'
=======
    class DBS:
        db = 'bbb'
>>>>>>> updated
```

Ending text.
    """
    expected = [
        Edit("some/dir/example_1.py", "def mul(a,b)", "def add(a,b):"),
        Edit(
            "some/dir/example_2.py",
            "class DBS:\n        db = 'aaa'",
            "class DBS:\n        db = 'bbb'",
        ),
    ]
    parsed = parse_edits(chat)
    assert parsed == expected


def test_apply_edit_new_file(log_capture):
    edits = [Edit("new_file.py", "", "print('Hello, World!')")]
    code = {"new_file.py": "some content"}
    apply_edits(edits, code)
    assert code == {"new_file.py": "print('Hello, World!')"}
    assert "file will be overwritten" in log_capture.messages[0]


def test_apply_edit_no_match(log_capture):
    edits = [Edit("file.py", "non-existent content", "new content")]
    code = {"file.py": "some content"}
    apply_edits(edits, code)
    assert code == {"file.py": "some content"}  # No change
    assert "code block to be replaced was not found" in log_capture.messages[0]


def test_apply_edit_multiple_matches(log_capture):
    edits = [Edit("file.py", "repeat", "new")]
    code = {"file.py": "repeat repeat repeat"}
    apply_edits(edits, code)
    assert code == {"file.py": "new new new"}
    assert "code block to be replaced was found multiple times" in log_capture.messages[0]


if __name__ == "__main__":
    pytest.main()
