from dataclasses import dataclass
from typing import List

from git import GitCommandError, Repo


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
    branch_changes: str
    staged_changes: str
    unstaged_changes: str
    tracked_files: List[str]


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
            tracked_files = self.repo.git.ls_files().split("\n")
            return tracked_files
        except GitCommandError as e:
            print(f"Error listing tracked files: {e}")
            return []

    def get_feature_branch_diff(self):
        """
        Get a consolidated diff for the entire feature branch from its divergence point.

        Returns:
        - str: The diff representing all changes from the feature branch since its divergence.
        """
        current_branch = self.repo.active_branch

        # Get the tracking branch (e.g., 'origin/master')
        tracking_branch = current_branch.tracking_branch()
        if tracking_branch is None:
            print("No tracking branch set, using 'master' as default base branch.")
            tracking_branch = self.repo.heads.master  # Fallback to 'master'

        try:
            # Find the merge base between the current branch and the tracking branch or master
            merge_base = self.repo.merge_base(tracking_branch, current_branch)
            if merge_base:
                merge_base = merge_base[
                    0
                ]  # GitPython might return a list of merge bases

            # Generate the diff from the merge base to the latest commit of the feature branch
            feature_diff = self.repo.git.diff(
                f"{merge_base}..{current_branch}", unified=0
            )
            return feature_diff
        except GitCommandError as e:
            print(f"Error generating diff: {e}")
            return ""

    def get_unstaged_changes(self):
        """
        Get the unstaged changes in the repository.

        Returns
        -------
        str
            The unstaged changes in the repository.
        """
        return self.repo.git.diff()

    def get_git_context(self):
        staged_changes = self.repo.git.diff("--cached")
        unstaged_changes = self.repo.git.diff()
        current_branch = self.repo.active_branch

        commits = list(self.repo.iter_commits(rev=current_branch.name))

        commit_objects = [
            Commit(
                commit.summary,
                (
                    commit.diff(commit.parents[0], create_patch=True)
                    if commit.parents
                    else commit.diff(None, create_patch=True)
                ),
            )
            for commit in commits
        ]

        branch_changes = self.get_feature_branch_diff()

        tracked_files = self.get_tracked_files()

        return GitContext(
            commit_objects,
            branch_changes,
            staged_changes,
            unstaged_changes,
            tracked_files,
        )

    def create_branch(self, branch_name):
        """
        Create a new branch in the repository.

        Parameters
        ----------
        branch_name : str
            The name of the new branch.
        """
        self.repo.git.checkout("-b", branch_name)

    def stage_all_changes(self):
        """
        Stage all changes in the repository.
        """
        self.repo.git.add("--all")

    def undo_unstaged_changes(self):
        """
        Undo all unstaged changes in the repository.
        """
        self.repo.git.checkout("--", ".")
