from feature import Feature
from file_selection import FileSelection
from repository import Repository
from files import Files
from agent_steps import (
    initialize_new_feature,
    update_user_file_selection,
    check_for_unstaged_changes,
    confirm_task_and_context_with_user,
)
from generation_tools import build_context_string

from gpt_engineer.core.ai import AI
from gpt_engineer.core.base_agent import BaseAgent
from gpt_engineer.core.default.disk_memory import DiskMemory
from gpt_engineer.core.default.paths import PREPROMPTS_PATH, memory_path
from gpt_engineer.core.preprompts_holder import PrepromptsHolder
from gpt_engineer.core.prompt import Prompt


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
        self.memory = DiskMemory(memory_path(project_path))
        self.preprompts_holder = PrepromptsHolder(PREPROMPTS_PATH)

    def init(self):

        initialize_new_feature(self.feature)

        update_user_file_selection(self.file_selection)

        self.resume()

    def resume(self):

        check_for_unstaged_changes(self.repository)

        confirm_task_and_context_with_user(self.feature, self.file_selection)

        context_string = build_context_string(
            self.feature, self.repository.get_git_context()
        )

        files = Files(self.project_path, self.file_selection.get_from_yaml())

    def improve(self):
        self.resume()
