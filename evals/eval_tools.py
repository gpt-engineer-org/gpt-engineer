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

import yaml

EVAL_LIST_NAME = "evaluations"  # the top level list in the YAML file


def check_language(eval_d: dict) -> None:
    if eval_d["language"] != "python":
        raise Exception(f"Language: {eval_d['language']} is not supported.")


def assert_exists_in_source_code(eval_d: dict) -> bool:
    """Checks of some text exists in the source code."""
    source_body = open(eval_d["project_root"] / eval_d["source_file"]).read()
    return source_body.find(eval_d["existing_string"]) > -1


def run_code_class_has_property(eval_d: dict) -> bool:
    """Will execute code, then check if the code has the desired proprty."""
    check_language(eval_d)
    source_body = open(eval_d["project_root"] / eval_d["source_file"]).read()
    exec(source_body)

    class_ref = locals().get(eval_d["class_name"])
    ob = class_ref()
    return hasattr(ob, eval_d["property_name"])


def run_code_class_has_property_w_value(eval_d: dict) -> bool:
    """Will execute code, then check if the code has the desired proprty."""
    check_language(eval_d)
    source_body = open(eval_d["project_root"] / eval_d["source_file"]).read()
    exec(source_body)

    class_ref = locals().get(eval_d["class_name"])
    ob = class_ref()

    assert hasattr(ob, eval_d["property_name"])

    return getattr(ob, eval_d["property_name"]) == eval_d["expected_value"]


def run_code_eval_function(eval_d: dict) -> bool:
    """Similar to run_code_class_has_property() except is evaluates a function call."""
    check_language(eval_d)
    source_body = open(eval_d["project_root"] / eval_d["source_file"]).read()
    exec(source_body)
    function_ref = globals().get(eval_d["function_name"])

    # TODO: add the ability to have function arguments
    return function_ref() == eval_d["expected_value"]


def run_executable(eval_d: dict) -> subprocess.Popen:
    code_dir = eval_d["project_root"] / "workspace"
    process_args = eval_d["executable_name"].split(" ") + eval_d[
        "executable_arguments"
    ].split(" ")
    process = subprocess.Popen(
        process_args,
        bufsize=0,
        cwd=code_dir.absolute(),
        stdout=subprocess.PIPE,
    )
    process.wait()
    return process


def check_executable_exits_normally(eval_d: dict) -> bool:
    """This simply runs an executable with arguments and checks the process exit code."""
    process = run_executable(eval_d=eval_d)
    return process.returncode == 0


def check_executable_satisfies_function(eval_d: dict) -> bool:
    """This function allows the test writer to define in Python conditions for a passfail.
    The conditions are checked by a user defined function called tf with a single argument
    the output of the executable.  tf() can be defined as either a lambda or a regular function.
    tf() is set in the `output_satisfies` field.  Here is an example using lambdas:
    output_satisfies: "tf = lambda a : len(a) == 10"
    """
    process = run_executable(eval_d=eval_d)
    process_output = process.communicate()[0].strip()

    exec(eval_d["output_satisfies"])
    checking_function_ref = locals().get("tf")
    return checking_function_ref(process_output)


def check_evaluation_component(eval_d: dict) -> bool:
    """Switch on evaluation components"""
    test_type = eval_d.get("type")
    if test_type == "assert_exists_in_source_code":
        return assert_exists_in_source_code(eval_d)
    elif test_type == "run_code_class_has_property":
        return run_code_class_has_property(eval_d)
    elif test_type == "run_code_class_has_property_w_value":
        return run_code_class_has_property_w_value(eval_d)
    elif test_type == "run_code_eval_function":
        return run_code_eval_function(eval_d)
    # The following are for new code
    elif test_type == "check_executable_exits_normally":
        return check_executable_exits_normally(eval_d)
    elif test_type == "check_executable_satisfies_function":
        return check_executable_satisfies_function(eval_d)
    else:
        raise Exception(f"Test type '{test_type}' is not recognized.")


def load_evaluations_from_file(file_path):
    """Loads the evaluations from a YAML file."""
    try:
        with open(file_path, "r") as file:
            data = yaml.safe_load(file)
            if EVAL_LIST_NAME in data:
                return data[EVAL_LIST_NAME]
            else:
                print(f"'{EVAL_LIST_NAME}' not found in {file_path}")
    except FileNotFoundError:
        print(f"File not found: {file_path}")


def to_emoji(value: bool) -> str:
    return "\U00002705" if value else "\U0000274C"
