import os
import pytest
from disk_memory import DiskMemory

@pytest.fixture
def disk_memory(tmp_path):
    return DiskMemory(directory=str(tmp_path))

def test_write_and_read(disk_memory):
    disk_memory.write("test_key", "test_data")
    assert disk_memory.read("test_key") == "test_data"

def test_delete(disk_memory):
    disk_memory.write("test_key", "test_data")
    disk_memory.delete("test_key")
    assert disk_memory.read("test_key") is None