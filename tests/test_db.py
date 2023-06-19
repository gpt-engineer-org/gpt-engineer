import os
import pytest
from gpt_engineer.db import DB

@pytest.fixture
def setup_db():
    # setup: use /tmp for testing
    path = '/tmp/test_db'
    db = DB(path)
    yield db, path

    # teardown: clean up files created during test
    for file in ['test', 'test2', 'int_value', 'bool_value']:
        try:
            os.remove(path + '/' + file)
        except FileNotFoundError:
            pass


def test_db_operations(setup_db):
    db, _ = setup_db
    db['test'] = 'test'
    assert db['test'] == 'test'
    db['test'] = 'test2'
    assert db['test'] == 'test2'
    db['test2'] = 'test2'
    assert db['test2'] == 'test2'
    assert db['test'] == 'test2'


def test_non_existent_key(setup_db):
    db, _ = setup_db
    with pytest.raises(KeyError):
        db['non_existent_key']


def test_different_data_types(setup_db):
    db, _ = setup_db
    db['int_value'] = '123'
    assert db['int_value'] == '123'
    db['bool_value'] = 'True'
    assert db['bool_value'] == 'True'
