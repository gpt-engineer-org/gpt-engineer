from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Tuple, Optional

from gpt_engineer.models import Message, Role, Step


class AI(ABC):
    """Abstract class for AI models. Any LLM model for use in gpt-engineer must satisfy the 
    following interface.
    """

    @abstractmethod
    def __init__(self, **kwargs: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def start(self, initial_conversation: List[Tuple[Role, Message]]) -> List[Tuple[Role, Message]]:
        pass

    @abstractmethod
    def next(self, messages: List[Tuple[Role, Message]], prompt: Optional[Message] = None) -> List[Tuple[Role, Message]]:
        pass
