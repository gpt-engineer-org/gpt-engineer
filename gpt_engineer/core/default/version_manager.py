from gpt_engineer.core.version_manager_interface import VersionManagerInterface
from gpt_engineer.core.code import Code

class VersionManager(VersionManagerInterface):

    def snapshot(self, code: Code) -> str:
        # Typically save to file and/or git
        return ""
