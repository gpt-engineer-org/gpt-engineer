from typing import Dict
from pathlib import Path
from gpt_engineer.core.default.on_disk_repository import OnDiskRepository


class PrepromptHolder:
    def __init__(self, preprompts_path: Path):
        self.preprompts_path = preprompts_path

    def get_preprompts(self) -> Dict[str, str]:
        preprompts_repo = OnDiskRepository(self.preprompts_path)
        return {file_name: preprompts_repo[file_name] for file_name in preprompts_repo}
