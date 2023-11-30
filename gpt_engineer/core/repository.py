from pathlib import Path
from typing import TypeVar, MutableMapping
from abc import ABC

Repository = MutableMapping[str | Path, str]
