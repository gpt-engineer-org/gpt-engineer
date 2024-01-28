import pytest
from gpt_engineer.core.chat_to_files import parse_diff

example_diff = """
Irrelevant line to be ignored

another irrelevant line to be ignored

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
"""


add_example = """
Uninteresting stuff

--- /dev/null
+++ new_file.txt
@@ -0,0 +1,3 @@
+First example line
+
+Last example line
"""


def test_diff_changing_one_file():
    diffs = parse_diff(example_diff)
    for filename, diff in diffs.items():
        string_diff = diff.diff_to_string()
    correct_diff = "\n".join(example_diff.strip().split("\n")[4:])
    assert string_diff == correct_diff


def test_diff_adding_one_file():
    add_diff = parse_diff(add_example)
    for filename, diff in add_diff.items():
        string_add_diff = diff.diff_to_string()
    correct_add_diff = "\n".join(add_example.strip().split("\n")[2:])
    assert string_add_diff == correct_add_diff


def test_diff_changing_two_files():
    merged_diff = parse_diff(example_diff + add_example)
    correct_diff = "\n".join(example_diff.strip().split("\n")[4:])
    correct_add_diff = "\n".join(add_example.strip().split("\n")[2:])
    assert merged_diff["example.txt"].diff_to_string() == correct_diff
    assert merged_diff["new_file.txt"].diff_to_string() == correct_add_diff


# def test_standard_input():
#     chat = """
#     Some text describing the code
# file1.py
# ```python
# 1 + print("Hello, World!")
# ```
#
# file2.py
# ```python
# 1 + def add(a, b):
# 2 +    return a + b
# ```
#     """
#     expected = {
#         "file1.py": '1 + print("Hello, World!")',
#         "file2.py": "1 + def add(a, b):\n2 +    return a + b",
#     }
#     assert chat_to_files_dict(chat) == expected
#
#
# def test_no_code_blocks():
#     chat = "Just some regular chat without code."
#     expected = {}
#     assert chat_to_files_dict(chat) == expected
#
#
# def test_special_characters_in_filename():
#     chat = """
#     file[1].py
#     ```python
#     1 + print("File 1")
#     ```
#
#     file`2`.py
#     ```python
#     1 + print("File 2")
#     ```
#     """
#     expected = {
#         "file[1].py": '1 + print("File 1")',
#         "file`2`.py": '1 + print("File 2")',
#     }
#     parsed = chat_to_files_dict(chat)
#     assert parsed == expected
#
#
# def test_empty_code_blocks():
#     chat = """
#     empty.py
#     ```
#     ```
#     """
#     expected = {"empty.py": ""}
#     assert chat_to_files_dict(chat) == expected
#
#
# def test_mixed_content():
#     chat = """
#     script.sh
#     ```bash
#     1 + echo "Hello"
#     ```
#
#     script.py
#     ```python
#     1 + print("World")
#     ```
#     """
#     expected = {"script.sh": '1 + echo "Hello"', "script.py": '1 + print("World")'}
#     assert chat_to_files_dict(chat) == expected
#
#
# def test_filename_line_break():
#     chat = """
#     file1.py
#
#     ```python
#     1 + print("Hello, World!")
#     ```
#     """
#     expected = {"file1.py": '1 + print("Hello, World!")'}
#     assert chat_to_files_dict(chat) == expected
#
#
# def test_filename_in_backticks():
#     chat = """
#     `file1.py`
#     ```python
#     1 + print("Hello, World!")
#     ```
#     """
#     expected = {"file1.py": '1 + print("Hello, World!")'}
#     assert chat_to_files_dict(chat) == expected
#
#
# def test_filename_with_file_tag():
#     chat = """
#     [FILE: file1.py]
#     ```python
#     1 + print("Hello, World!")
#     ```
#     """
#     expected = {"file1.py": '1 + print("Hello, World!")'}
#     assert chat_to_files_dict(chat) == expected
#
#
# def test_filename_with_different_extension():
#     chat = """
#     [id].jsx
#     ```javascript
#     1 + console.log("Hello, World!")
#     ```
#     """
#     expected = {"[id].jsx": '1 + console.log("Hello, World!")'}
#     assert chat_to_files_dict(chat) == expected


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
# def test_basic_similarity():
#     assert is_similar("abc", "cab")
#     assert not is_similar("abc", "def")
#
#
# def test_case_insensitivity_and_whitespace():
#     assert is_similar("A b C", "c a b")
#     assert not is_similar("Abc", "D e F")
#
#
# def test_length_and_character_frequency():
#     assert is_similar("aabbc", "bacba")
#     assert not is_similar("aabbcc", "abbcc")
#
#
# def test_edge_cases():
#     assert not is_similar("", "a")
#     assert is_similar("a", "a")


if __name__ == "__main__":
    pytest.main()
