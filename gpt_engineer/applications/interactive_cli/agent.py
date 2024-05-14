from feature import Feature
from file_selection import FileSelection
from repository import Repository
from files import Files
from agent_steps import (
    initialize_new_feature,
    update_user_file_selection,
    check_for_unstaged_changes,
    confirm_feature_context_and_task_with_user,
    run_improve_function,
)
from generation_tools import build_context_string

from gpt_engineer.core.ai import AI
from gpt_engineer.core.base_agent import BaseAgent


class FeatureAgent(BaseAgent):
    """
    A cli agent which implements a feature as a set of incremental tasks
    """

    def __init__(
        self,
        project_path: str,
        feature: Feature,
        repository: Repository,
        ai: AI = None,
    ):
        self.project_path = project_path
        self.feature = feature
        self.repository = repository
        self.ai = ai or AI()

        self.file_selection = FileSelection(project_path, repository)

    def init(self):

        initialize_new_feature(self.ai, self.feature)

        update_user_file_selection(self.file_selection)

        self.resume()

    def resume(self):

        check_for_unstaged_changes(self.repository)

        confirm_feature_context_and_task_with_user(self.feature, self.file_selection)

        run_improve_function(
            self.project_path,
            self.feature,
            self.repository,
            self.ai,
            self.file_selection,
        )

    def improve(self):
        self.resume()
