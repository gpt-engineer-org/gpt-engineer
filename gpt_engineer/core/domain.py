"""
This module provides annotations related to the steps workflow in GPT Engineer.

Imports:
    - `Callable`, `List`, and `TypeVar` from `typing` module, which are used for type hinting.
    - `AI` class from the `gpt_engineer.core.ai` module.
    - `DBs` class from the `gpt_engineer.core.db` module.

Variables:
    - `Step`: This is a generic type variable that represents a Callable or function type. The function
      is expected to accept two parameters: an instance of `AI` and an instance of `DBs`. The function
      is expected to return a list of dictionaries.
"""
# ToDo: This file and everything that depends on it should be eliminated

from typing import TypeVar, Callable, List
from gpt_engineer.core.ai import AI
from gpt_engineer.core.default.on_disk_repository import FileRepositories
from gpt_engineer.tools.code_vector_repository import CodeVectorRepository

Step = TypeVar(
    "Step", bound=Callable[[AI, FileRepositories, CodeVectorRepository], List[dict]]
)
