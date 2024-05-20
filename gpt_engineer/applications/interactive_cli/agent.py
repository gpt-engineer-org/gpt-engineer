from gpt_engineer.applications.interactive_cli.feature import Feature
from gpt_engineer.applications.interactive_cli.file_selection import FileSelector
from gpt_engineer.applications.interactive_cli.repository import Repository
from gpt_engineer.applications.interactive_cli.domain import Settings
from gpt_engineer.applications.interactive_cli.agent_steps import (
    initialize_new_feature,
    update_user_file_selection,
    check_for_unstaged_changes,
    confirm_feature_context_and_task_with_user,
    run_task_loop,
    adjust_feature_task_or_files,
    update_task_description,
)

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

        self.file_selector = FileSelector(project_path, repository)

    def init(self, settings: Settings):

        initialize_new_feature(
            self.ai, self.feature, self.repository, settings.no_branch
        )

        update_user_file_selection(self.file_selector)

        update_task_description(self.feature)

        self.resume(settings)

    def resume(self, settings: Settings):

        implement = False

        while not implement:
            implement = confirm_feature_context_and_task_with_user(
                self.feature, self.file_selector
            )

            adjust_feature_task_or_files()

        check_for_unstaged_changes(self.repository)

        run_task_loop(
            self.project_path,
            self.feature,
            self.repository,
            self.ai,
            self.file_selector,
        )

    def improve(self):
        self.resume()
