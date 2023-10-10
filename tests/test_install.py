"""
Tests for successful import and installation of the package.
"""
import subprocess
import sys
import venv
import shutil

# Test that the package can be installed via pip
def test_installation():
    # Create a virtual environment
    venv_dir = "./venv_test_installation"
    venv.create(venv_dir, with_pip=True)

    # Use pip from the virtual environment directly
    pip_executable = f"{venv_dir}/bin/pip"
    if sys.platform == "win32":
        pip_executable = f"{venv_dir}/Scripts/pip.exe"
    
    try:
        result = subprocess.run(
            [pip_executable, "install", "."], 
            capture_output=True
        )
        assert result.returncode == 0, f"Install via pip failed: {result.stderr.decode()}"
    finally:
        # Cleanup
        shutil.rmtree(venv_dir)


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
