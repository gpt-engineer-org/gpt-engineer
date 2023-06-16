import logging
from typing import Any, Dict, List, Tuple, Optional


from gpt_engineer.models import Message, Role
from gpt_engineer.ai.ai import AI


class TestAI(AI):
    """A simple AI that tests the code's functionality.
    """

    def __init__(self, **kwargs: Dict[str, Any]) -> None:
        pass

    def start(self, initial_conversation: List[Tuple[Role, Message]]) -> List[Tuple[Role, Message]]:
        return [
            (Role.ASSISTANT, Message("hello world"))
        ]

    def next(self, messages: List[Tuple[Role, Message]], user_prompt: Optional[Message] = None) -> List[Tuple[Role, Message]]:
        return [
            (Role.ASSISTANT, Message("Unto the next world"))
        ]

