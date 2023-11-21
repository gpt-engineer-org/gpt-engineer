from typing import MutableMapping, Union
from pathlib import Path
from gpt_engineer.core.default.on_disk_repository import OnDiskRepository


class PrepromptHolder:
    @staticmethod
    def get_preprompts(
        preprompts_path: Union[str, Path]
    ) -> MutableMapping[Union[str, Path], str]:
        return OnDiskRepository(preprompts_path)
