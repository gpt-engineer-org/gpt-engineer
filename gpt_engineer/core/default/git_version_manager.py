from gpt_engineer.core.base_version_manager import BaseVersionManager
from gpt_engineer.core.code import Code


class GitVersionManager(BaseVersionManager):
    def __init__(self, path: str):
        self.path = path

    def snapshot(self, code: Code) -> str:
        # Typically save to file and/or git and return a hash
        return ""
