from gpt_engineer.db import DB


def test_db():
    # use /tmp for testing
    db = DB("/tmp/test_db")
    db["test"] = "test"
    assert db["test"] == "test"
    db["test"] = "test2"
    assert db["test"] == "test2"
    db["test2"] = "test2"
    assert db["test2"] == "test2"
    assert db["test"] == "test2"
    print("test_db passed")
