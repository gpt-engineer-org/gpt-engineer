import os

import pytest

from gpt_engineer.core.chat_to_files import chat_to_files_dict, parse_diffs
from gpt_engineer.core.diff import is_similar
from gpt_engineer.core.files_dict import file_to_lines_dict

THIS_FILE_DIR = os.path.dirname(os.path.abspath(__file__))

example_diff = """
Irrelevant line to be ignored

another irrelevant line to be ignored
```diff
--- example.txt
+++ example.txt
@@ -12,3 +12,4 @@
     sample text 1
     sample text 2
+    added extra line here
-    original text A
+    updated original text A with changes
@@ -35,4 +36,5 @@
         checking status:
-            perform operation X
+            perform operation X only if specific condition holds
+                new operation related to condition
         evaluating next step:
-            execute step Y
+            revised execution of step Y
```
"""

example_line_dist_diff = """
Irrelevant line to be ignored

another irrelevant line to be ignored
```diff
--- example.txt
+++ example.txt
@@ -10,4 +13,5 @@
     sample text 1
     sample text 2
+    added extra line here
-    original text A
+    updated original text A with changes
@@ -33,14 +363,5 @@
         checking status:
-            perform operation X
+            perform operation X only if specific condition holds
+                new operation related to condition
         evaluating next step:
-            execute step Y
+            revised execution of step Y
```
"""


add_example = """
Uninteresting stuff
```diff
--- /dev/null
+++ new_file.txt
@@ -0,0 +1,3 @@
+First example line
+
+Last example line
```
"""

file_example = """# Introduction

@Analysis
Overview: outcomes
%
Background: *context*

Method: []
!
Theories: ?
> Leading up...
    sample text 1
    sample text 2
    original text A
a
Challenges: ~

Perspectives: <>

Strategy: {#}
+
Outcomes: ^^^

Future: |||

x

Y

Z



code
         checking status:
            perform operation X
         evaluating next step:
            execute step Y
End.

Conclusion: ***
"""


def insert_string_in_lined_string(string, to_insert, line_number):
    split_string = string.split("\n")
    split_string.insert(line_number - 1, to_insert)
    return "\n".join(split_string)


def test_diff_changing_one_file():
    diffs = parse_diffs(example_diff)
    for filename, diff in diffs.items():
        string_diff = diff.diff_to_string()
    correct_diff = "\n".join(example_diff.strip().split("\n")[4:-1])
    assert string_diff == correct_diff


def test_diff_adding_one_file():
    add_diff = parse_diffs(add_example)
    for filename, diff in add_diff.items():
        string_add_diff = diff.diff_to_string()
    correct_add_diff = "\n".join(add_example.strip().split("\n")[2:-1])
    assert string_add_diff == correct_add_diff


def test_diff_changing_two_files():
    merged_diff = parse_diffs(example_diff + add_example)
    correct_diff = "\n".join(example_diff.strip().split("\n")[4:-1])
    correct_add_diff = "\n".join(add_example.strip().split("\n")[2:-1])
    assert merged_diff["example.txt"].diff_to_string() == correct_diff
    assert merged_diff["new_file.txt"].diff_to_string() == correct_add_diff


def test_validate_diff_correct():
    lines_dict = file_to_lines_dict(file_example)
    diffs = parse_diffs(example_diff)
    # This is a test in its own right since it full of exceptions, would something go wrong
    list(diffs.values())[0].validate_and_correct(lines_dict)


def test_correct_distorted_numbers():
    lines_dict = file_to_lines_dict(file_example)
    diffs = parse_diffs(example_line_dist_diff)
    # This is a test in its own right since it full of exceptions, would something go wrong
    list(diffs.values())[0].validate_and_correct(lines_dict)
    correct_diff = "\n".join(example_diff.strip().split("\n")[4:-1])
    assert diffs["example.txt"].diff_to_string() == correct_diff


def test_correct_skipped_lines():
    distorted_example = insert_string_in_lined_string(
        file_example, "\n#comment\n\n", 14
    )
    diffs = parse_diffs(example_diff)
    list(diffs.values())[0].validate_and_correct(file_to_lines_dict(distorted_example))
    with open(
        os.path.join(
            THIS_FILE_DIR,
            "chat_to_files_test_cases",
            "corrected_diff_from_missing_lines",
        ),
        "r",
    ) as f:
        corrected_diff_from_missing_lines = f.read()
    assert diffs["example.txt"].diff_to_string() == corrected_diff_from_missing_lines


def test_correct_skipped_lines_and_number_correction():
    distorted_example = insert_string_in_lined_string(
        file_example, "\n#comment\n\n", 14
    )
    diffs = parse_diffs(example_line_dist_diff)
    list(diffs.values())[0].validate_and_correct(file_to_lines_dict(distorted_example))
    with open(
        os.path.join(
            THIS_FILE_DIR,
            "chat_to_files_test_cases",
            "corrected_diff_from_missing_lines",
        ),
        "r",
    ) as f:
        corrected_diff_from_missing_lines = f.read()
    assert diffs["example.txt"].diff_to_string() == corrected_diff_from_missing_lines


def test_controller_diff():
    with open(
        os.path.join(THIS_FILE_DIR, "chat_to_files_test_cases", "diff_controller"), "r"
    ) as f:
        controller_diff = f.read()
    with open(
        os.path.join(THIS_FILE_DIR, "chat_to_files_test_cases", "controller_code"), "r"
    ) as f:
        controller_code = f.read()
    diffs = parse_diffs(controller_diff)
    list(diffs.values())[0].validate_and_correct(file_to_lines_dict(controller_code))


def test_simple_calculator_diff():
    simple_calculator_diff = None
    simple_calculator_code = None
    with open(
        os.path.join(
            THIS_FILE_DIR, "chat_to_files_test_cases", "diff_simple_calculator"
        ),
        "r",
    ) as f:
        simple_calculator_diff = f.read()
    with open(
        os.path.join(
            THIS_FILE_DIR, "chat_to_files_test_cases", "simple_calculator_code"
        ),
        "r",
    ) as f:
        simple_calculator_code = f.read()
    diffs = parse_diffs(simple_calculator_diff)
    list(diffs.values())[0].validate_and_correct(
        file_to_lines_dict(simple_calculator_code)
    )


def test_complex_temperature_converter_diff():
    temperature_converter_diff = None
    temperature_converter_code = None
    with open(
        os.path.join(
            THIS_FILE_DIR, "chat_to_files_test_cases", "diff_temperature_converter"
        ),
        "r",
    ) as f:
        temperature_converter_diff = f.read()
    with open(
        os.path.join(
            THIS_FILE_DIR, "chat_to_files_test_cases", "temperature_converter_code"
        ),
        "r",
    ) as f:
        temperature_converter_code = f.read()
    diffs = parse_diffs(temperature_converter_diff)
    list(diffs.values())[0].validate_and_correct(
        file_to_lines_dict(temperature_converter_code)
    )


def test_complex_task_master_diff():
    task_master_diff = None
    task_master_code = None
    with open(
        os.path.join(THIS_FILE_DIR, "chat_to_files_test_cases", "diff_task_master"), "r"
    ) as f:
        task_master_diff = f.read()
    with open(
        os.path.join(THIS_FILE_DIR, "chat_to_files_test_cases", "task_master_code"), "r"
    ) as f:
        task_master_code = f.read()
    diffs = parse_diffs(task_master_diff)
    list(diffs.values())[0].validate_and_correct(file_to_lines_dict(task_master_code))


def test_standard_input():
    chat = """
    Some text describing the code
file1.py
```python
1 + print("Hello, World!")
```

file2.py
```python
1 + def add(a, b):
2 +    return a + b
```
    """
    expected = {
        "file1.py": '1 + print("Hello, World!")',
        "file2.py": "1 + def add(a, b):\n2 +    return a + b",
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
    1 + print("File 1")
    ```

    file`2`.py
    ```python
    1 + print("File 2")
    ```
    """
    expected = {
        "file[1].py": '1 + print("File 1")',
        "file`2`.py": '1 + print("File 2")',
    }
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
    1 + echo "Hello"
    ```

    script.py
    ```python
    1 + print("World")
    ```
    """
    expected = {"script.sh": '1 + echo "Hello"', "script.py": '1 + print("World")'}
    assert chat_to_files_dict(chat) == expected


def test_filename_line_break():
    chat = """
    file1.py

    ```python
    1 + print("Hello, World!")
    ```
    """
    expected = {"file1.py": '1 + print("Hello, World!")'}
    assert chat_to_files_dict(chat) == expected


def test_filename_in_backticks():
    chat = """
    `file1.py`
    ```python
    1 + print("Hello, World!")
    ```
    """
    expected = {"file1.py": '1 + print("Hello, World!")'}
    assert chat_to_files_dict(chat) == expected


def test_filename_with_file_tag():
    chat = """
    [FILE: file1.py]
    ```python
    1 + print("Hello, World!")
    ```
    """
    expected = {"file1.py": '1 + print("Hello, World!")'}
    assert chat_to_files_dict(chat) == expected


def test_filename_with_different_extension():
    chat = """
    [id].jsx
    ```javascript
    1 + console.log("Hello, World!")
    ```
    """
    expected = {"[id].jsx": '1 + console.log("Hello, World!")'}
    assert chat_to_files_dict(chat) == expected


#
#
# # Helper function to capture log messages
# @pytest.fixture
# def log_capture():
#     class LogCaptureHandler(logging.Handler):
#         def __init__(self):
#             super().__init__()
#             self.messages = []
#
#         def emit(self, record):
#             self.messages.append(record.getMessage())
#
#     handler = LogCaptureHandler()
#     parse_logger.addHandler(handler)
#     yield handler
#     parse_logger.removeHandler(handler)
#
#
# def test_parse_with_additional_text():
#     chat = """
# Some introductory text.
#
# ```python
# File: some/dir/example_1.py
# 1 -     def mul(a,b)
# 1 +     def add(a,b):
# ```
#
# Text between patches.
#
# ```python
# File: some/dir/example_2.py
# 1 -     class DBS:
# 2 -         db = 'aaa'
# 1 +     class DBS:
# 2 +        db = 'bbb'
# ```
#
# Ending text.
#     """
#     expected = [
#         Edit(
#             filename="some/dir/example_1.py",
#             line_number=1,
#             content="    def mul(a,b)",
#             is_before=True,
#         ),
#         Edit(
#             filename="some/dir/example_1.py",
#             line_number=1,
#             content="    def add(a,b):",
#             is_before=False,
#         ),
#         Edit(
#             filename="some/dir/example_2.py",
#             line_number=1,
#             content="    class DBS:",
#             is_before=True,
#         ),
#         Edit(
#             filename="some/dir/example_2.py",
#             line_number=1,
#             content="    class DBS:",
#             is_before=False,
#         ),
#         Edit(
#             filename="some/dir/example_2.py",
#             line_number=2,
#             content="        db = 'aaa'",
#             is_before=True,
#         ),
#         Edit(
#             filename="some/dir/example_2.py",
#             line_number=2,
#             content="       db = 'bbb'",
#             is_before=False,
#         ),
#     ]
#     parsed = parse_edits(chat)
#     assert parsed == expected
#
#
# def test_apply_overwrite_existing_file(log_capture):
#     edits = [
#         Edit(filename="existing_file.py", line_number=1, content="", is_before=True),
#         Edit(
#             filename="existing_file.py",
#             line_number=1,
#             content="print('Hello, World!')",
#             is_before=False,
#         ),
#     ]
#     code = {"existing_file.py": "some content"}
#     apply_edits(edits, code)
#     assert code == {"existing_file.py": "some content"}
#     assert "not found in existing_file.py where should be" in log_capture.messages[0]
#     assert "is discarded for wrong line number" in log_capture.messages[1]
#
#
# def test_apply_edit_new_file(log_capture):
#     edits = [
#         Edit(filename="new_file.py", line_number=1, content="", is_before=True),
#         Edit(
#             filename="new_file.py",
#             line_number=1,
#             content="print('Hello, World!')",
#             is_before=False,
#         ),
#     ]
#     code = {}
#     apply_edits(edits, code)
#     assert code == {"new_file.py": "print('Hello, World!')"}
#
#
# def test_apply_edit_no_match(log_capture):
#     edits = [
#         Edit(
#             filename="file.py",
#             line_number=1,
#             content="non-existent content",
#             is_before=True,
#         ),
#         Edit(filename="file.py", line_number=1, content="new content", is_before=False),
#     ]
#     code = {"file.py": "some content"}
#     apply_edits(edits, code)
#     assert code == {"file.py": "some content"}  # No change
#     assert "not found" in log_capture.messages[0]
#
#
def test_basic_similarity():
    assert is_similar("abc", "cab")
    assert not is_similar("abc", "def")


def test_case_insensitivity_and_whitespace():
    assert is_similar("A b C", "c a b")
    assert not is_similar("Abc", "D e F")


def test_length_and_character_frequency():
    assert is_similar("aabbc", "bacba")
    assert not is_similar("aabbcc", "abbcc")


def test_edge_cases():
    assert not is_similar("", "a")
    assert is_similar("a", "a")


if __name__ == "__main__":
    pytest.main()
