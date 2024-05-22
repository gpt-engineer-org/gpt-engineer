from gpt_engineer.applications.interactive_cli.feature import Feature
from gpt_engineer.applications.interactive_cli.repository import Repository
from gpt_engineer.applications.interactive_cli.domain import Settings
from gpt_engineer.applications.interactive_cli.agents.agent_steps import (
    initialize_new_feature,
    update_user_file_selection,
    check_for_unstaged_changes,
    run_task_loop,
    run_adjust_loop,
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
        feature: Feature,
        repository: Repository,
        ai: AI = None,
    ):
        self.feature = feature
        self.repository = repository
        self.ai = ai or AI()

    def init(self, settings: Settings):

        initialize_new_feature(
            self.ai, self.feature, self.repository, settings.no_branch
        )

        update_user_file_selection(self.file_selector)

        update_task_description(self.feature)

        self.resume(settings)

    def resume(self, settings: Settings):

        run_adjust_loop(self.feature, self.file_selector)

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
