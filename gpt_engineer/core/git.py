import shutil
import subprocess

from pathlib import Path


def is_git_installed():
    return shutil.which("git") is not None


def is_git_repo(path: Path):
    return (path / ".git").exists()


def init_git_repo(path: Path):
    subprocess.run(["git", "init"], cwd=path)


def has_uncommitted_changes(path: Path):
    return bool(
        subprocess.run(
            ["git", "diff", "--exit-code"],
            cwd=path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).returncode
    )


def get_gitignore_rules(path: Path):
    gitignore = path / ".gitignore"
    ret = []
    if gitignore.exists():
        with gitignore.open() as f:
            # Read lines, strip whitespace, remove empty lines and filter out comments
            ret = list(
                filter(
                    lambda x: x and not x.startswith("#"),
                    map(lambda x: x.strip(), f.readlines()),
                )
            )
    return ret
