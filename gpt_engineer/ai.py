import logging

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import openai

from gpt_engineer.models import Message, Messages, Role


class AI(ABC):
    """Abstract class for AI models. Any LLM model for use in gpt-engineer must satisfy
    the following interface.
    """

    @abstractmethod
    def __init__(self, **kwargs: Dict[str, Any]) -> None:
        """
        Initialization for the AI model.

        Args:
            **kwargs: Variable length argument list for model configuration. **kwargs
                can/will depend on AI subclass.
        """
        pass

    @abstractmethod
    def start(self, initial_conversation: Messages) -> Messages:
        """
        Initializes the conversation with specific system and user messages.

        Args:
            initial_conversation (List[Tuple[Role, Message]]): The initial messages
                given to the
            AI. Generally these are prompt to the system about their task, qa and/or
                philosophy.

        Returns:
            List[Dict[str, str]]: Returns the next set of conversation.
        """
        pass

    @abstractmethod
    def next(self, messages: Messages, user_prompt: Optional[Message] = None) -> Messages:
        """
        Asks the AI model to respond to the user prompt after ingesting some initial
            messages.

        Args:
            messages (List[Dict[str, str]]): The list of messages to be used for
                chat completion.
            user_prompt (str, optional): Additional prompt to be added to messages.
                Defaults to None.

        Returns:
            List[Dict[str, str]]: Returns the chat completion response along with
              previous messages.
        """
        pass


class GPT(AI):
    def __init__(self, **kwargs: Dict[str, Any]) -> None:
        self.kwargs = kwargs
        self._model_check_and_fallback()

    def start(self, initial_conversation: Messages) -> Messages:
        return self.next(initial_conversation)

    def next(self, messages: Messages, user_prompt: Optional[str] = None) -> Messages:
        if user_prompt:
            messages.messages.append(Message(user_prompt, Role.USER))

        response = openai.ChatCompletion.create(
            messages=[self._format_message(m) for m in messages.messages],
            stream=True,
            **self.kwargs,
        )

        chat = []
        for chunk in response:
            delta = chunk["choices"][0]["delta"]
            msg = delta.get("content", "")
            print(msg, end="")
            chat.append(msg)

        messages.messages.append(Message("".join(chat), Role.ASSISTANT))
        return messages

    def _format_message(self, msg: Message) -> Dict[str, str]:
        """
        Formats the message as per role.

        Args:
            role (str): The role to be used for the message.
            msg (str): The message content.

        Returns:
            Dict[str, str]: A dictionary containing the role and content.
        """
        return {"role": msg.role, "content": msg.content}

    def _model_check_and_fallback(self) -> None:
        """
        Checks if the desired model is available; if not, it falls back to a default
         model.
        """
        try:
            openai.Model.retrieve(self.kwargs.get("model", "gpt-4"))
        except openai.error.InvalidRequestError:
            logging.info(
                "Model gpt-4 not available for provided api key reverting "
                "to gpt-3.5.turbo. Sign up for the gpt-4 wait list here: "
                "https://openai.com/waitlist/gpt-4-api"
            )
            self.kwargs["model"] = "gpt-3.5-turbo"
