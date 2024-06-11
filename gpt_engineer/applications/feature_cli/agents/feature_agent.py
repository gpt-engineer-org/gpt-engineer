from gpt_engineer.applications.feature_cli.feature import Feature
from gpt_engineer.applications.feature_cli.repository import Repository
from gpt_engineer.applications.feature_cli.file_selection import FileSelector
from gpt_engineer.applications.feature_cli.agents.agent_steps import (
    initialize_new_feature,
    update_user_file_selection,
    print_feature_state,
    update_feature,
    initiate_new_task,
    generate_code_for_task,
    review_changes,
    check_existing_task,
    check_for_unstaged_changes,
    get_git_context,
)

# Bottom comment for testing!
from gpt_engineer.core.ai import AI

from yaspin import yaspin


class FeatureAgent:
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

    def initialize_feature(self):
        initialize_new_feature(self.ai, self.feature, self.repository)

        update_user_file_selection(self.file_selector)

        print("\nFeature Initialized. Run gptf task to begin working on it.")

    def update_feature(self):

        print_feature_state(self.feature, self.file_selector)

        if not self.feature.has_description():
            self.initialize_feature()
        else:
            update_feature(self.feature, self.repository)

    def run_task(self):
        print_feature_state(self.feature, self.file_selector)

        if not self.feature.has_description():
            print(
                """Run gptf to initialize new feature.

or

Run gptf task --no-feature to implement task without a feature"""
            )
            return

        if self.feature.has_task():
            cont = check_existing_task(self.feature, self.file_selector)

            if not cont:
                return

        while True:
            git_context = get_git_context(self.repository)

            if not self.feature.has_task():
                initiate_new_task(
                    self.ai, self.feature, git_context, self.file_selector
                )

            cont = check_for_unstaged_changes(self.repository)

            if not cont:
                return

            generate_code_for_task(
                self.project_path,
                self.feature,
                git_context,
                self.ai,
                self.file_selector,
            )

            review_changes(
                self.project_path,
                self.feature,
                self.repository,
                self.ai,
                self.file_selector,
            )
