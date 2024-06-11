from dataclasses import dataclass
from typing import List


@dataclass
class FileSelection:
    included_files: List[str]
    excluded_files: List[str]


class Settings:
    def __init__(self, no_branch: bool = False):
        self.no_branch = no_branch
