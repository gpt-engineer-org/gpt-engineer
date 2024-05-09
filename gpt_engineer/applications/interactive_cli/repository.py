from dataclasses import dataclass
from typing import List

from git import Repo, GitCommandError
import os

@dataclass
class Commit:
    """
    Represents a single Git commit with a description and a diff.
    """
    description: str
    diff: str

    def __str__(self) -> str:
        diff_str = "\n".join(str(d) for d in self.diff)
        return f"Commit Description: {self.description}\nDiff:\n{diff_str}"


@dataclass
class GitContext:
    """
    Represents the Git context of an in progress feature.
    """
    commits: List[Commit]
    staged_changes: str
    unstaged_changes: str



class Repository:
    """
    Manages a git repository, providing functionalities to get repo status,
    list files considering .gitignore, and interact with repository history.
    """
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.repo = Repo(repo_path)
        assert not self.repo.bare

    def get_tracked_files(self) -> List[str]:
        """
        List all files that are currently tracked by Git in the repository.
        """
        try:
            tracked_files = self.repo.git.ls_files().split('\n')
            return tracked_files
        except GitCommandError as e:
            print(f"Error listing tracked files: {e}")
            return []


    def get_git_context(self):
        staged_changes = self.repo.git.diff('--cached')
        unstaged_changes = self.repo.git.diff()
        current_branch = self.repo.active_branch

        commits = list(self.repo.iter_commits(rev=current_branch.name))

        commit_objects = [
            Commit(
                commit.summary,
                commit.diff(commit.parents[0], create_patch=True) if commit.parents else commit.diff(None, create_patch=True)
            )
            for commit in commits
        ]

        return GitContext(commit_objects, staged_changes, unstaged_changes)