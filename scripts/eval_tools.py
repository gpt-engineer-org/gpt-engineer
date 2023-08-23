from pathlib import Path


def assert_exists_in_source_code(eval: dict) -> bool:
    source_body = open(eval['fpath']).read()
    return source_body.find(eval['existing_code']) > -1


def run_python_code(eval: dict) -> bool:
    # Placeholder function
    return True


def run_code_class_has_property(eval: dict) -> bool:
    if eval['language'] == 'python':
        return run_python_code(eval)
    else:
        raise Exception(f"Language '{eval['language']}' is not supported.")


def check_evaluation_component(eval: dict):
    """Switch on evaluation components"""
    test_type = eval.get('type')
    if test_type == 'assert_exists_in_source_code':
        return assert_exists_in_source_code(eval.get('fpath'), eval.get('existing_code'))
    elif test_type == 'run_code_class_has_property':
        return run_code_class_has_property()
    else:
        raise Exception(f"Test type '{test_type}' is not recognized.")

