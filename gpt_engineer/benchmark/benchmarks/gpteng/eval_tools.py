"""
This library is used for the evaluation of gpt-engineer's performance, on
editing and creating code.  This is very low level in that it looks at the
code written.  It is possible that the AI could solve the problem in ways
that we cannot forsee, with this in mind higher level tests are always
better than lower.

The scope will bre relatively limited to a few languages but this could
be expanded.
"""

import subprocess

from datetime import datetime

import yaml

from tabulate import tabulate

from gpt_engineer.core.files_dict import FilesDict

EVAL_LIST_NAME = "evaluations"  # the top level list in the YAML file


def check_language(eval_d: dict) -> None:
    if eval_d["language"] != "python":
        raise Exception(f"Language: {eval_d['language']} is not supported.")


def assert_exists_in_source_code(eval_d: dict, files_dict: FilesDict) -> bool:
    """Checks of some text exists in the source code."""
    source_body = files_dict[eval_d["source_file"]]
    return source_body.find(eval_d["existing_string"]) > -1


def run_code_class_has_property(eval_d: dict, files_dict: FilesDict) -> bool:
    """Will execute code, then check if the code has the desired proprty."""
    check_language(eval_d)
    source_body = files_dict[eval_d["source_file"]]
    exec(source_body)

    class_ref = locals().get(eval_d["class_name"])
    ob = class_ref()
    return hasattr(ob, eval_d["property_name"])


def run_code_class_has_property_w_value(eval_d: dict, files_dict: FilesDict) -> bool:
    """Will execute code, then check if the code has the desired proprty."""
    check_language(eval_d)
    source_body = files_dict[eval_d["source_file"]]
    exec(source_body)

    class_ref = locals().get(eval_d["class_name"])
    ob = class_ref()

    assert hasattr(ob, eval_d["property_name"])

    return getattr(ob, eval_d["property_name"]) == eval_d["expected_value"]


def run_code_eval_function(eval_d: dict, files_dict: FilesDict) -> bool:
    """Similar to run_code_class_has_property() except is evaluates a function call."""
    check_language(eval_d)
    source_body = files_dict[eval_d["source_file"]]
    exec(source_body)
    function_ref = globals().get(eval_d["function_name"])

    # TODO: add the ability to have function arguments
    return function_ref() == eval_d["expected_value"]


def check_evaluation_component(eval_d: dict, files_dict: FilesDict) -> bool:
    """Switch on evaluation components"""
    test_type = eval_d.get("type")
    if test_type == "assert_exists_in_source_code":
        return assert_exists_in_source_code(eval_d, files_dict)
    elif test_type == "run_code_class_has_property":
        return run_code_class_has_property(eval_d, files_dict)
    elif test_type == "run_code_class_has_property_w_value":
        return run_code_class_has_property_w_value(eval_d, files_dict)
    elif test_type == "run_code_eval_function":
        return run_code_eval_function(eval_d, files_dict)
    # The following are for new code
    else:
        raise Exception(f"Test type '{test_type}' is not recognized.")
