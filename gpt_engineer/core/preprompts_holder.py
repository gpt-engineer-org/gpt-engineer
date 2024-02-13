from pathlib import Path
from typing import Dict

from gpt_engineer.core.default.disk_memory import DiskMemory


class PrepromptsHolder:
    """
    A holder for preprompt texts that are stored on disk.

    This class provides methods to retrieve preprompt texts from a specified directory.

    Attributes
    ----------
    preprompts_path : Path
        The file path to the directory containing preprompt texts.

    Methods
    -------
    get_preprompts() -> Dict[str, str]
        Retrieve all preprompt texts from the directory and return them as a dictionary.
    """

    def __init__(self, preprompts_path: Path):
        self.preprompts_path = preprompts_path

    def get_preprompts(self) -> Dict[str, str]:
        preprompts_repo = DiskMemory(self.preprompts_path)
        return {file_name: preprompts_repo[file_name] for file_name in preprompts_repo}
