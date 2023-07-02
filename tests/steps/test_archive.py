import datetime
import os

from unittest.mock import MagicMock

from gpt_engineer.db import DB, DBs, archive


def freeze_at(monkeypatch, time):
    datetime_mock = MagicMock(wraps=datetime.datetime)
    datetime_mock.now.return_value = time
    monkeypatch.setattr(datetime, "datetime", datetime_mock)


def setup_dbs(tmp_path, dir_names):
    directories = [tmp_path / name for name in dir_names]

    # Create DB objects
    dbs = [DB(dir) for dir in directories]

    # Create DBs instance
    return DBs(*dbs)


def test_archive(tmp_path, monkeypatch):
    dbs = setup_dbs(
        tmp_path, ["memory", "logs", "preprompts", "input", "workspace", "archive"]
    )
    freeze_at(monkeypatch, datetime.datetime(2020, 12, 25, 17, 5, 55))
    archive(dbs)
    assert not os.path.exists(tmp_path / "memory")
    assert not os.path.exists(tmp_path / "workspace")
    assert os.path.isdir(tmp_path / "archive" / "20201225_170555")

    dbs = setup_dbs(
        tmp_path, ["memory", "logs", "preprompts", "input", "workspace", "archive"]
    )
    freeze_at(monkeypatch, datetime.datetime(2022, 8, 14, 8, 5, 12))
    archive(dbs)
    assert not os.path.exists(tmp_path / "memory")
    assert not os.path.exists(tmp_path / "workspace")
    assert os.path.isdir(tmp_path / "archive" / "20201225_170555")
    assert os.path.isdir(tmp_path / "archive" / "20220814_080512")
