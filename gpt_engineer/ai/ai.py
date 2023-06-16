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
        """
        Initialization for the AI model.

        Args:
            **kwargs: Variable length argument list for model configuration. **kwargs can/will 
                depend on AI subclass.
        """
        pass

    @abstractmethod
    def start(self, initial_conversation: List[Tuple[Role, Message]]) -> List[Tuple[Role, Message]]:
        """
        Initializes the conversation with specific system and user messages.

        Args:
            initial_conversation (List[Tuple[Role, Message]]): The initial messages given to the 
            AI. Generally these are prompt to the system about their task, qa and/or philosophy.

        Returns:
            List[Dict[str, str]]: Returns the next set of conversation.
        """
        pass

    @abstractmethod
    def next(self, messages: List[Tuple[Role, Message]], user_prompt: Optional[Message] = None) -> List[Tuple[Role, Message]]:
        """
        Asks the AI model to respond to the user prompt after ingesting some initial messages.

        Args:
            messages (List[Dict[str, str]]): The list of messages to be used for chat completion.
            user_prompt (str, optional): Additional prompt to be added to messages. Defaults to None.

        Returns:
            List[Dict[str, str]]: Returns the chat completion response along with previous messages.
        """
        pass
