import os

from typing import Dict, Tuple

import pytest

from gpt_engineer.core.chat_to_files import parse_diffs
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

example_multiple_diffs = """
I apologize for the oversight. Let's correct the `calculator.py` file with the proper git diff format, ensuring that the context lines match the original code exactly.

```diff
--- calculator.py
+++ calculator.py
@@ -1,3 +1,3 @@
 class Calculator:
-    def add(self, a, b):
-        return a - b  # Logical
+    def add(self, a, b):  # Adds two numbers
+        return a + b
```

Now, let's create the `main.py` file with the correct git diff format:

```diff
--- /dev/null
+++ main.py
@@ -0,0 +1,7 @@
+from calculator import Calculator
+
+# Function to demonstrate the usage of the Calculator class
+def main():
+    calc = Calculator()
+if __name__ == "__main__":
+    main()
```

These changes should now correctly apply to the provided code and create a simple calculator program with a command-line interface.


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

single_diff = """
```
--- a/file1.txt
+++ a/file1.txt
@@ -1,3 +1,3 @@
-old line
+new line
```
"""
multi_diff = """
```
--- a/file1.txt
+++ a/file1.txt
@@ -1,3 +1,3 @@
-old line
+new line
```
```
--- a/file1.txt
+++ a/file1.txt
@@ -2,3 +2,3 @@
-another old line
+another new line
```
"""


# Single function tests
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
        file_example, "#\n#comment\n#\n#", 14
    )
    diffs = parse_diffs(example_diff)
    list(diffs.values())[0].validate_and_correct(file_to_lines_dict(distorted_example))
    with open(
        os.path.join(
            THIS_FILE_DIR,
            "improve_function_test_cases",
            "corrected_diff_from_missing_lines",
        ),
        "r",
    ) as f:
        corrected_diff_from_missing_lines = f.read()
    assert (
        diffs["example.txt"].diff_to_string().strip()
        == corrected_diff_from_missing_lines.strip()
    )


def test_correct_skipped_lines_and_number_correction():
    distorted_example = insert_string_in_lined_string(
        file_example, "#\n#comment\n#\n#", 14
    )
    diffs = parse_diffs(example_line_dist_diff)
    # list(diffs.values())[0].validate_and_correct(file_to_lines_dict(distorted_example))
    for diff in diffs.values():
        problems = diff.validate_and_correct(file_to_lines_dict(distorted_example))
        print(problems)
    with open(
        os.path.join(
            THIS_FILE_DIR,
            "improve_function_test_cases",
            "corrected_diff_from_missing_lines",
        ),
        "r",
    ) as f:
        corrected_diff_from_missing_lines = f.read()
    assert (
        diffs["example.txt"].diff_to_string().strip()
        == corrected_diff_from_missing_lines.strip()
    )


def test_diff_regex():
    diff = parse_diffs(example_diff)
    assert len(diff) == 1

    diffs = parse_diffs(example_multiple_diffs)
    assert len(diffs) == 2


def parse_chats_with_regex(
    diff_file_name: str, code_file_name: str
) -> Tuple[str, str, Dict]:
    # Load the diff
    with open(
        os.path.join(THIS_FILE_DIR, "improve_function_test_cases", diff_file_name), "r"
    ) as f:
        diff_content = f.read()

    # Load the corresponding code
    with open(
        os.path.join(THIS_FILE_DIR, "improve_function_test_cases", code_file_name), "r"
    ) as f:
        code_content = f.read()

    # Parse the diffs
    diffs = parse_diffs(diff_content)

    return diff_content, code_content, diffs


def capture_print_output(func):
    import io
    import sys

    captured_output = io.StringIO()
    sys.stdout = captured_output
    func()
    sys.stdout = sys.__stdout__
    return captured_output


def test_single_diff():
    diffs = parse_diffs(single_diff)
    correct_diff = "\n".join(single_diff.strip().split("\n")[1:-1])
    assert diffs["a/file1.txt"].diff_to_string() == correct_diff


def test_multi_diff_discard():
    captured_output = capture_print_output(lambda: parse_diffs(multi_diff))
    diffs = parse_diffs(multi_diff)
    correct_diff = "\n".join(multi_diff.strip().split("\n")[1:8]).replace(
        "```\n```", ""
    )
    assert (
        "Multiple diffs found for a/file1.txt. Only the first one is kept."
        in captured_output.getvalue()
    )
    assert diffs["a/file1.txt"].diff_to_string().strip() == correct_diff.strip()


# test parse diff
def test_controller_diff():
    parse_chats_with_regex("controller_chat", "controller_code")


def test_simple_calculator_diff():
    parse_chats_with_regex("simple_calculator_chat", "simple_calculator_code")


def test_complex_temperature_converter_diff():
    parse_chats_with_regex("temperature_converter_chat", "temperature_converter_code")


def test_complex_task_master_diff():
    parse_chats_with_regex("task_master_chat", "task_master_code")


def test_long_file_diff():
    parse_chats_with_regex("wheaties_example_chat", "wheaties_example_code")


if __name__ == "__main__":
    pytest.main()
