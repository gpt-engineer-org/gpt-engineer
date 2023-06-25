from typing import Callable, List, TypeVar

from gpt_engineer.ai import AI
from gpt_engineer.db import DBs

Step = TypeVar("Step", bound=Callable[[AI, DBs], List[dict]])
