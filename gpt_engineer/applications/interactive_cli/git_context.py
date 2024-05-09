from typing import List
from git import Repo, GitCommandError

class Commit:
    """
    Represents a single Git commit with a description and a diff.
    """
    def __init__(self, description: str, diff: str):
        self.description = description
        self.diff = diff

    def __str__(self):
        diff_str = "\n".join(str(d) for d in self.diff)
        return f"Commit Description: {self.description}\nDiff:\n{diff_str}"

class GitContext:
    """
    Represents the Git context of a project directory, including a list of commits,
    and staged and unstaged changes.
    """
    def __init__(self, commits: List[Commit], staged_changes: str, unstaged_changes: str):
        self.commits = commits
        self.staged_changes = staged_changes
        self.unstaged_changes = unstaged_changes

    @classmethod
    def load_from_directory(cls, project_path: str) -> "GitContext":
        """
        Load the Git context from the specified project directory using GitPython.

        Parameters
        ----------
        project_path : str
            The path to the project directory.

        Returns
        -------
        GitContext
            An instance of GitContext populated with commit details and changes.
        """
        try:
            # Initialize the repository object
            repo = Repo(project_path)
            assert not repo.bare  # Ensure it is not a bare repository

            # Staged changes
            staged_changes = repo.git.diff('--cached')

            # Unstaged changes
            unstaged_changes = repo.git.diff()

            # Identify the current branch
            current_branch = repo.active_branch

            commits = list(repo.iter_commits(rev=current_branch.name))

            # Create Commit objects with descriptions and diffs
            commit_objects = [
                Commit(
                    commit.summary,
                    commit.diff(commit.parents[0], create_patch=True) if commit.parents else commit.diff(None, create_patch=True)
                )
                for commit in commits
            ]

            return cls(commit_objects, staged_changes, unstaged_changes)
        
        except (AssertionError, GitCommandError, IndexError) as e:
            print(f"Error accessing repository: {e}")
            return cls([], '', '')

