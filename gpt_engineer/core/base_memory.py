from pathlib import Path
from typing import MutableMapping, Union

BaseMemory = MutableMapping[Union[str, Path], str]
