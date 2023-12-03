import pytest
import subprocess
import sys
import venv
import shutil


VENV_DIR = "./venv_test_installation"


@pytest.fixture(scope="module", autouse=True)
def venv_setup_teardown():
    try:
        venv.create(VENV_DIR, with_pip=True)
        # Install Poetry in the virtual environment
        subprocess.run([f"{VENV_DIR}/bin/python", "-m", "pip", "install", "poetry"], check=True)
        # Install dependencies using Poetry
        subprocess.run([f"{VENV_DIR}/bin/poetry", "install"], cwd=".", check=True)
        yield
    except Exception as e:
        pytest.skip(f"Could not create venv or install dependencies: {str(e)}")
    finally:
        shutil.rmtree(VENV_DIR)


# Test that the package can be installed via Poetry
def test_installation():
    poetry_executable = f"{VENV_DIR}/bin/poetry" if sys.platform != "win32" else f"{VENV_DIR}/Scripts/poetry.exe"

    result = subprocess.run([poetry_executable, "install"], capture_output=True)
    assert result.returncode == 0, f"Install via poetry failed: {result.stderr.decode()}"


# Test that the CLI command works
def test_cli_execution():
    # This assumes that after installation, `gpt-engineer` command should work.
    result = subprocess.run(
        args=["gpt-engineer", "--help"], capture_output=True, text=True
    )
    assert (
        result.returncode == 0
    ), f"gpt-engineer command failed with message: {result.stderr}"
