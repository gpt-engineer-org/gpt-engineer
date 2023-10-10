"""
Tests for successful import and installation of the package.
"""
import subprocess
import sys
import venv
import shutil

# Setup the test environment
VENV_DIR = "./venv_test_installation"
venv.create(VENV_DIR, with_pip=True)


# Test that the package can be installed via pip
def test_installation():
    # Use pip from the virtual environment directly
    pip_executable = f"{VENV_DIR}/bin/pip"
    if sys.platform == "win32":
        pip_executable = f"{VENV_DIR}/Scripts/pip.exe"

    result = subprocess.run([pip_executable, "install", "."], capture_output=True)
    assert result.returncode == 0, f"Install via pip failed: {result.stderr.decode()}"


# Test that the package can be imported
def test_import():
    try:
        from gpt_engineer import (
            ai,
            domain,
            chat_to_files,
            steps,
            db,
        )
    except ImportError as e:
        assert False, f"Failed to import {e.name}"


# Test that the CLI command works
def test_cli_execution():
    # This assumes that after installation, `gpt-engineer` command should work.
    result = subprocess.run(
        args=["gpt-engineer", "--help"], capture_output=True, text=True
    )
    assert (
        result.returncode == 0
    ), f"gpt-engineer command failed with message: {result.stderr}"


# Cleanup the test environment
def test_cleanup():
    shutil.rmtree(VENV_DIR)


# Run the tests using pytest
if __name__ == "__main__":
    test_installation()
    test_import()
    test_cli_execution()
    test_cleanup()
