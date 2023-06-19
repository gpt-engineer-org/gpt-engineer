import logging
from typing import Any, Dict, List, Tuple, Optional

import openai

from gpt_engineer.models import Message, Role
from gpt_engineer.ai.ai import AI

logging.basicConfig(level=logging.INFO)


class GPT(AI):
    def __init__(self, **kwargs: Dict[str, Any]) -> None:
        self.kwargs = kwargs
        self._model_check_and_fallback()

    def start(self, initial_conversation: List[Tuple[Role, Message]]) -> List[Tuple[Role, Message]]:
        return self.next(initial_conversation)

    def next(self, messages: List[Tuple[Role, Message]], user_prompt: Optional[Message] = None) -> List[Tuple[Role, Message]]:
        if user_prompt:
            messages.append((Role.USER, user_prompt))


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
        return {"role": role.value, "content": msg.content}

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
