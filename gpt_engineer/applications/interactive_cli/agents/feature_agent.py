from gpt_engineer.applications.interactive_cli.feature import Feature
from gpt_engineer.applications.interactive_cli.repository import Repository
from gpt_engineer.applications.interactive_cli.domain import Settings
from gpt_engineer.applications.interactive_cli.file_selection import FileSelector
from gpt_engineer.applications.interactive_cli.agents.agent_steps import (
    initialize_new_feature,
    update_user_file_selection,
    check_for_unstaged_changes,
    run_task_loop,
    run_adjust_loop,
    initiate_new_task,
)
from prompt_toolkit import prompt as cli_input

from gpt_engineer.core.ai import AI
from gpt_engineer.core.base_agent import BaseAgent


class FeatureAgent(BaseAgent):
    """
    A cli agent which implements a feature as a set of incremental tasks
    """

    def __init__(
        self,
        ai: AI,
        project_path: str,
        feature: Feature,
        repository: Repository,
        file_selector: FileSelector,
    ):
        self.ai = ai
        self.project_path = project_path
        self.feature = feature
        self.repository = repository
        self.file_selector = file_selector

    def init(self, settings: Settings):

        initialize_new_feature(
            self.ai, self.feature, self.repository, settings.no_branch
        )

        update_user_file_selection(self.file_selector)

        initiate_new_task(self.ai, self.feature, None, self.file_selector)

        self.resume(settings)

    def resume(self, settings: Settings):
        if self.feature.has_task():
            if cli_input(
                "Complete current task and initiate new task? y/n: "
            ).lower() in [
                "n",
                "no",
            ]:
                check_for_unstaged_changes(self.repository)

                run_task_loop(
                    self.project_path,
                    self.feature,
                    self.repository,
                    self.ai,
                    self.file_selector,
                )

        initiate_new_task(self.ai, self.feature, None, self.file_selector)

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
