from pathlib import Path
from typing import TypeVar, MutableMapping
from abc import ABC

BaseMemory = MutableMapping[str | Path, str]
