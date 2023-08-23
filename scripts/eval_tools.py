from pathlib import Path


def assert_exists_in_source_code(fpath: Path, existing_code: str):
    source_body = open(fpath).read()
    return source_body.find(existing_code) > -1
