from dataclasses import dataclass
from enum import Enum
from typing import List

from dataclasses_json import dataclass_json


class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"


@dataclass_json
@dataclass
class Message:
    content: str
    role: Role


@dataclass_json
@dataclass
class Messages:
    messages: List[Message]

    def last_message_content(self) -> str:
        return self.messages[-1].content
