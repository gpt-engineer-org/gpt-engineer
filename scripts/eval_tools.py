from pathlib import Path


def assert_exists_in_source_code(fpath: Path, existing_code: str):
    source_body = open(fpath).read()
    return source_body.find(existing_code) > -1


def run_code_class_has_property():
    # Placeholder function
    pass


def run_tests(tests: dict):
    test_type = tests.get('type')
    if test_type == 'assert_exists_in_source_code':
        return assert_exists_in_source_code(tests.get('fpath'), tests.get('existing_code'))
    elif test_type == 'run_code_class_has_property':
        return run_code_class_has_property()
    else:
        raise Exception(f"Test type '{test_type}' is not recognized.")
