import subprocess
import tempfile

from pathlib import Path

from gpt_engineer.core.git import (
    filter_by_gitignore,
    filter_files_with_uncommitted_changes,
    init_git_repo,
    is_git_installed,
    is_git_repo,
    stage_files,
)


def test_verify_git_installed():
    # If git isn't installed we can't run any git tests either way
    assert is_git_installed()


def test_init_git_repo():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir)
        init_git_repo(path)
        assert is_git_repo(path)


def test_stage_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir)
        init_git_repo(path)

        # Create a file and stage it
        file = path / "test.txt"
        file.write_text("test")

        stage_files(path, ["test.txt"])

        # Check if the file is staged
        assert (
            subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                cwd=path,
                stdout=subprocess.PIPE,
            )
            .stdout.decode()
            .strip()
            == "test.txt"
        )


def test_filter_by_gitignore():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir)
        init_git_repo(path)

        # Create a .gitignore file
        gitignore = path / ".gitignore"
        gitignore.write_text("*.txt")
        assert filter_by_gitignore(path, ["test.txt"]) == []


def test_filter_by_uncommitted_changes():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir)
        init_git_repo(path)

        # Create a file and commit it
        file = path / "test.txt"
        file.write_text("test")

        subprocess.run(["git", "add", "test.txt"], cwd=path)
        subprocess.run(["git", "commit", "-m", "test"], cwd=path)

        # Update the file
        file.write_text("test2")

        # Check if the file is staged
        assert filter_files_with_uncommitted_changes(path, {"test.txt": "test"}) == [
            "test.txt"
        ]


def test_filter_by_uncommitted_changes_ignore_staged_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir)
        init_git_repo(path)

        # Create a file but and stage it
        file = path / "test.txt"
        file.write_text("test")
        subprocess.run(["git", "add", "test.txt"], cwd=path)

        # Check if the file is staged
        assert filter_files_with_uncommitted_changes(path, {"test.txt": "test"}) == []


def test_filter_by_uncommitted_changes_ignore_untracked():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir)
        init_git_repo(path)

        # Create a file but don't track it
        file = path / "test.txt"
        file.write_text("test")

        # Check if the file is staged
        assert filter_files_with_uncommitted_changes(path, {"test.txt": "test"}) == []
