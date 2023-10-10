import datetime
import os

from unittest.mock import MagicMock

from gpt_engineer.core.db import DB, DBs, archive


def freeze_at(monkeypatch, time):
    """
    Mocks the current time.

    Parameters:
    monkeypatch: pytest's monkeypatch fixture
    time: datetime object representing the time to be mocked

    Returns:
    None
    """
    datetime_mock = MagicMock(wraps=datetime.datetime)
    datetime_mock.now.return_value = time
    monkeypatch.setattr(datetime, "datetime", datetime_mock)


def setup_dbs(tmp_path, dir_names):
    """
    Sets up DBs instance with given directory names.

    Parameters:
    tmp_path: pytest's tmp_path fixture, provides a temporary directory path
    dir_names: list of directory names to be created

    Returns:
    DBs instance
    """
    directories = [tmp_path / name for name in dir_names]

    # Create DB objects
    dbs = [DB(dir) for dir in directories]

    # Create DBs instance
    return DBs(*dbs)


def test_archive(tmp_path, monkeypatch):
    """
    Tests the archive function.

    This test checks if the archive function correctly moves the contents of the memory and workspace directories to the archive directory.
    It also checks if the memory and workspace directories are deleted after the archive operation.
    The test is run twice with different timestamps to check if the function can handle multiple archives.

    Parameters:
    tmp_path: pytest's tmp_path fixture, provides a temporary directory path
    monkeypatch: pytest's monkeypatch fixture

    Returns:
    None
    """
    dbs = setup_dbs(
        tmp_path,
        [
            "memory",
            "logs",
            "preprompts",
            "input",
            "workspace",
            "archive",
            "project_metadata",
        ],
    )
    freeze_at(monkeypatch, datetime.datetime(2020, 12, 25, 17, 5, 55))
    archive(dbs)
    assert not os.path.exists(tmp_path / "memory")
    assert not os.path.exists(tmp_path / "workspace")
    assert os.path.isdir(tmp_path / "archive" / "20201225_170555")

    dbs = setup_dbs(
        tmp_path,
        [
            "memory",
            "logs",
            "preprompts",
            "input",
            "workspace",
            "archive",
            "project_metadata",
        ],
    )
    freeze_at(monkeypatch, datetime.datetime(2022, 8, 14, 8, 5, 12))
    archive(dbs)
    assert not os.path.exists(tmp_path / "memory")
    assert not os.path.exists(tmp_path / "workspace")
    assert os.path.isdir(tmp_path / "archive" / "20201225_170555")
    assert os.path.isdir(tmp_path / "archive" / "20220814_080512")
