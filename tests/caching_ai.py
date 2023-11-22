import os.path

from gpt_engineer.core.ai import AI
from pathlib import Path
import json
from typing import List, Optional, Union

from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage,
)

# Type hint for a chat message
Message = Union[AIMessage, HumanMessage, SystemMessage]

class CachingAI(AI):

    def __init__(self):
        super().__init__(streaming=False)
        self.cache_file = Path(__file__).parent / "ai_cache.json"

    def next(
        self,
        messages: List[Message],
        prompt: Optional[str] = None,
        *,
        step_name: str,
    ) -> List[Message]:
        """
        Advances the conversation by sending message history
        to LLM and updating with the response.

        Parameters
        ----------
        messages : List[Message]
            The list of messages in the conversation.
        prompt : Optional[str], optional
            The prompt to use, by default None.
        step_name : str
            The name of the step.

        Returns
        -------
        List[Message]
            The updated list of messages in the conversation.
        """
        """
        Advances the conversation by sending message history
        to LLM and updating with the response.
        """
        if prompt:
            messages.append(HumanMessage(content=prompt))

        # read cache file if it exists
        if os.path.isfile(self.cache_file):
            with open(self.cache_file, "r") as cache_file:
                cache = json.load(cache_file)
        else:
            cache = dict()

        messages_key = self.serialize_messages(messages)
        if messages_key not in cache:
            callbacks = []
            response = self.backoff_inference(messages, callbacks)
            messages.append(response)
            cache[messages_key] = self.serialize_messages(messages)
            with open(self.cache_file, "w") as cache_file:
                json.dump(cache, cache_file)

        return self.deserialize_messages(cache[messages_key])
