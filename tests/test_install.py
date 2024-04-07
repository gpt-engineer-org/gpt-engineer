"""
Tests for successful installation of the package.
"""

import shutil
import subprocess
import sys
import venv

from pathlib import Path

import pytest

# Define the directory for the virtual environment.
VENV_DIR = "./venv_test_installation"


@pytest.fixture(scope="module", autouse=True)
def venv_setup_teardown():
    """
    A pytest fixture that sets up and tears down a virtual environment for testing.
    This fixture is automatically used for all tests in this module.

    The fixture:
    - Creates a virtual environment.
    - Installs Poetry in the virtual environment.
    - Installs dependencies using Poetry.
    - Cleans up by removing the virtual environment after tests are completed.
    """
    try:
        # Create a virtual environment with pip available.
        venv.create(VENV_DIR, with_pip=True, clear=True)

        # Install Poetry in the virtual environment.
        subprocess.run(
            [f"{VENV_DIR}/bin/python", "-m", "pip", "install", "poetry"], check=True
        )

        # Install the package and its dependencies using Poetry.
        subprocess.run([f"{VENV_DIR}/bin/poetry", "install"], cwd=".", check=True)

        # Provide the setup environment to the test functions.
        yield
    except Exception as e:
        # Skip tests if the environment setup fails.
        pytest.skip(f"Could not create venv or install dependencies: {str(e)}")
    finally:
        # Clean up by removing the virtual environment after tests.
        shutil.rmtree(VENV_DIR)


def test_installation():
    """
    Test to ensure that the package can be installed using Poetry in the virtual environment.
    """
    # Determine the correct Poetry executable path based on the operating system.
    poetry_executable = (
        f"{VENV_DIR}/bin/poetry"
        if sys.platform != "win32"
        else f"{VENV_DIR}/Scripts/poetry.exe"
    )

    # Run Poetry install and capture its output.
    result = subprocess.run([poetry_executable, "install"], capture_output=True)

    # Assert that the installation was successful.
    assert (
        result.returncode == 0
    ), f"Install via poetry failed: {result.stderr.decode()}"


def test_cli_execution():
    """
    Test to verify that the command-line interface (CLI) of the package works as expected.
    This test assumes that the 'gpt-engineer' command is available and operational after installation.
    """
    # Run the 'gpt-engineer' command with the '--help' option and capture its output.
    result = subprocess.run(
        args=["gpt-engineer", "--help"], capture_output=True, text=True
    )

    # Assert that the CLI command executed successfully.
    assert (
        result.returncode == 0
    ), f"gpt-engineer command failed with message: {result.stderr}"


@pytest.mark.requires_key
def test_installed_main_execution(tmp_path, monkeypatch):
    # Ignore git installation check
    monkeypatch.setattr("gpt_engineer.core.git.is_git_installed", lambda: False)
    tmp_path = Path(tmp_path)
    p = tmp_path / "projects/example"
    p.mkdir(parents=True)
    (p / "prompt").write_text("make a program that prints the outcome of 4+4")
    proc = subprocess.Popen(
        ["gpte", str(p)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
        cwd=tmp_path,
    )

    inputs = "Y\nn"
    output, _ = proc.communicate(inputs)

    assert "8" in output
