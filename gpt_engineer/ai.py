from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import logging
from typing import Any, Dict, List, Tuple, Union, Optional

import openai

from gpt_engineer.models import Message, Role


logging.basicConfig(level=logging.INFO)


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

class TestAI(AI):
    """A simple AI that tests the code's functionality.
    """

    def __init__(self, **kwargs: Dict[str, Any]) -> None:
        pass

    def start(self, initial_conversation: List[Tuple[Role, Message]]) -> List[Tuple[Role, Message]]:
        return [
            (Role.ASSISTANT, "hello world")
        ]

    def next(self, messages: List[Tuple[Role, Message]], prompt: Optional[Message] = None) -> List[Tuple[Role, Message]]:
        return [
            (Role.ASSISTANT, "Unto the next world")
        ]


class GPT(AI):
    def __init__(self, **kwargs: Dict[str, Any]) -> None:
        """
        Initialization for the AI model.

        Args:
            **kwargs: Variable length argument list for model configuration. **kwargs can/will 
                depend on AI subclass.
        """
        self.kwargs = kwargs
        self._model_check_and_fallback()

    def start(self, initial_conversation: List[Tuple[Role, Message]]) -> List[Tuple[Role, Message]]:
        """
        Initializes the conversation with specific system and user messages.

        Args:
            initial_conversation (List[Tuple[Role, Message]]): The initial system message.

        Returns:
            List[Dict[str, str]]: Returns the next set of conversation.
        """
        return self.next(initial_conversation)

    def next(self, messages: List[Tuple[Role, Message]], prompt: Optional[Message] = None) -> List[Tuple[Role, Message]]:
        """
        Appends the prompt if present to messages and performs chat completion.

        Args:
            messages (List[Dict[str, str]]): The list of messages to be used for chat completion.
            prompt (str, optional): Additional prompt to be added to messages. Defaults to None.

        Returns:
            List[Dict[str, str]]: Returns the chat completion response along with previous messages.
        """
        if prompt:
            messages.append(self._format_message(Role.USER, prompt))


        response = openai.ChatCompletion.create(
            messages=[self._format_message(r, m) for r, m in messages], stream=True, **self.kwargs
        )

        chat = []
        for chunk in response:
            delta = chunk["choices"][0]["delta"]
            msg = delta.get("content", "")
            logging.info(msg)
            chat.append(msg)

        messages.append((
            Role.ASSISTANT, Message(content="".join(chat))
        ))
        return messages

    def _format_message(self, role: Role, msg: Message) -> Dict[str, str]:
        """
        Formats the message as per role.

        Args:
            role (str): The role to be used for the message.
            msg (str): The message content.

        Returns:
            Dict[str, str]: A dictionary containing the role and content.
        """
        return {"role": str(role), "content": msg.content}

    def _model_check_and_fallback(self) -> None:
        """
        Checks if the desired model is available; if not, it falls back to a default model.
        """
        try:
            openai.Model.retrieve(self.kwargs.get('model', 'gpt-4'))
        except openai.error.InvalidRequestError:
            logging.info("Model gpt-4 not available for provided api key reverting "
                         "to gpt-3.5.turbo. Sign up for the gpt-4 wait list here: "
                         "https://openai.com/waitlist/gpt-4-api")
            self.kwargs['model'] = "gpt-3.5-turbo"
