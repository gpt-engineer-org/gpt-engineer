from typing import Callable, List, TypeVar

from gpt_engineer.core.ai import AI
from gpt_engineer.core.db import DBs

Step = TypeVar("Step", bound=Callable[[AI, DBs], List[dict]])
