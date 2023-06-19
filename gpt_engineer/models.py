from dataclasses import dataclass
from enum import Enum


class Step(Enum):
    CLARIFY = "clarify"
    RUN_CLARIFIED = "run_clarified"


@dataclass
class Message:
    content: str


class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"
