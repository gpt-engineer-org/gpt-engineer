"""
Evaluation tools for assessing the performance of GPT-based models on code editing
and creation tasks. These tools provide low-level checks on the written code and
support higher-level tests for a comprehensive evaluation.

Currently, the scope is limited to a few programming languages, with the potential
for future expansion.

Functions
---------
check_language : function
    Checks if the specified language in the evaluation dictionary is supported.

assert_exists_in_source_code : function
    Checks if a specified string exists in the source code within the provided files dictionary.

run_code_class_has_property : function
    Executes the code and checks if the specified class has the desired property.

run_code_class_has_property_w_value : function
    Executes the code and checks if the specified class has the desired property with the expected value.

run_code_eval_function : function
    Executes the code and evaluates a function call, checking if it returns the expected value.

check_evaluation_component : function
    Dispatches the evaluation component based on the type specified in the evaluation dictionary.
"""

from gpt_engineer.core.files_dict import FilesDict

EVAL_LIST_NAME = "evaluations"  # the top level list in the YAML file


def check_language(eval_d: dict) -> None:
    """
    Checks if the specified language in the evaluation dictionary is supported.

    Parameters
    ----------
    eval_d : dict
        The evaluation dictionary containing the 'language' key.

    Raises
    ------
    Exception
        If the specified language is not supported.
    """
    if eval_d["language"] != "python":
        raise Exception(f"Language: {eval_d['language']} is not supported.")


def assert_exists_in_source_code(eval_d: dict, files_dict: FilesDict) -> bool:
    """
    Checks if a specified string exists in the source code within the provided files dictionary.

    Parameters
    ----------
    eval_d : dict
        The evaluation dictionary containing the 'source_file' and 'existing_string' keys.
    files_dict : FilesDict
        The dictionary of file names to their respective source code content.

    Returns
    -------
    bool
        True if the specified string exists in the source code, False otherwise.
    """

    source_body = files_dict[eval_d["source_file"]]
    return source_body.find(eval_d["existing_string"]) > -1


def run_code_class_has_property(eval_d: dict, files_dict: FilesDict) -> bool:
    """
    Executes the code and checks if the specified class has the desired property.

    Parameters
    ----------
    eval_d : dict
        The evaluation dictionary containing the 'source_file', 'class_name', and 'property_name' keys.
    files_dict : FilesDict
        The dictionary of file names to their respective source code content.

    Returns
    -------
    bool
        True if the class has the specified property, False otherwise.
    """

    check_language(eval_d)
    source_body = files_dict[eval_d["source_file"]]
    exec(source_body)

    class_ref = locals().get(eval_d["class_name"])
    ob = class_ref()
    return hasattr(ob, eval_d["property_name"])


def run_code_class_has_property_w_value(eval_d: dict, files_dict: FilesDict) -> bool:
    """
    Executes the code and checks if the specified class has the desired property with the expected value.

    Parameters
    ----------
    eval_d : dict
        The evaluation dictionary containing the 'source_file', 'class_name', 'property_name', and 'expected_value' keys.
    files_dict : FilesDict
        The dictionary of file names to their respective source code content.

    Returns
    -------
    bool
        True if the class has the specified property with the expected value, False otherwise.
    """

    check_language(eval_d)
    source_body = files_dict[eval_d["source_file"]]
    exec(source_body)

    class_ref = locals().get(eval_d["class_name"])
    ob = class_ref()

    assert hasattr(ob, eval_d["property_name"])

    return getattr(ob, eval_d["property_name"]) == eval_d["expected_value"]


def run_code_eval_function(eval_d: dict, files_dict: FilesDict) -> bool:
    """
    Executes the code and evaluates a function call, checking if it returns the expected value.

    Parameters
    ----------
    eval_d : dict
        The evaluation dictionary containing the 'source_file', 'function_name', and 'expected_value' keys.
    files_dict : FilesDict
        The dictionary of file names to their respective source code content.

    Returns
    -------
    bool
        True if the function call returns the expected value, False otherwise.
    """

    check_language(eval_d)
    source_body = files_dict[eval_d["source_file"]]
    exec(source_body)
    function_ref = globals().get(eval_d["function_name"])

    # TODO: add the ability to have function arguments
    return function_ref() == eval_d["expected_value"]


def check_evaluation_component(eval_d: dict, files_dict: FilesDict) -> bool:
    """
    Dispatches the evaluation component based on the type specified in the evaluation dictionary.

    Parameters
    ----------
    eval_d : dict
        The evaluation dictionary containing the 'type' key and other relevant information for the evaluation.
    files_dict : FilesDict
        The dictionary of file names to their respective source code content.

    Returns
    -------
    bool
        The result of the dispatched evaluation component.

    Raises
    ------
    Exception
        If the test type specified in the evaluation dictionary is not recognized.
    """

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
