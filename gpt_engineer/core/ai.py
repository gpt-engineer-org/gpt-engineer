from __future__ import annotations

import json
import logging
import os

from typing import List, Optional, Union

import backoff
import openai

from gpt_engineer.core.token_usage import TokenUsageLog

from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chat_models import AzureChatOpenAI, ChatOpenAI
from langchain.chat_models.base import BaseChatModel
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    messages_from_dict,
    messages_to_dict,
)

# Type hint for a chat message
Message = Union[AIMessage, HumanMessage, SystemMessage]

# Set up logging
logger = logging.getLogger(__name__)


class AI:
    def __init__(
        self,
        model_name="gpt-4-1106-preview",
        temperature=0.1,
        azure_endpoint="",
        streaming=True,
    ):
        """
        Initialize the AI class.

        Parameters
        ----------
        model_name : str, optional
            The name of the model to use, by default "gpt-4".
        temperature : float, optional
            The temperature to use for the model, by default 0.1.
        """
        self.temperature = temperature
        self.azure_endpoint = azure_endpoint
        self.model_name = model_name
        self.streaming = streaming
        self.llm = self._create_chat_model()
        self.token_usage_log = TokenUsageLog(model_name)

        logger.debug(f"Using model {self.model_name}")

    def start(self, system: str, user: str, step_name: str) -> List[Message]:
        """
        Start the conversation with a system message and a user message.

        Parameters
        ----------
        system : str
            The content of the system message.
        user : str
            The content of the user message.
        step_name : str
            The name of the step.

        Returns
        -------
        List[Message]
            The list of messages in the conversation.
        """

        messages: List[Message] = [
            SystemMessage(content=system),
            HumanMessage(content=user),
        ]
        return self.next(messages, step_name=step_name)

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

        logger.debug(f"Creating a new chat completion: {messages}")

        callbacks = [StreamingStdOutCallbackHandler()]
        response = self.backoff_inference(messages, callbacks)

        self.token_usage_log.update_log(
            messages=messages, answer=response.content, step_name=step_name
        )
        messages.append(response)
        logger.debug(f"Chat completion finished: {messages}")

        return messages

    @backoff.on_exception(
        backoff.expo, openai.error.RateLimitError, max_tries=7, max_time=45
    )
    def backoff_inference(self, messages, callbacks):
        """
        Perform inference using the language model while implementing an exponential backoff strategy.

        This function will retry the inference in case of a rate limit error from the OpenAI API.
        It uses an exponential backoff strategy, meaning the wait time between retries increases
        exponentially. The function will attempt to retry up to 7 times within a span of 45 seconds.

        Parameters
        ----------
        messages : List[Message]
            A list of chat messages which will be passed to the language model for processing.

        callbacks : List[Callable]
            A list of callback functions that are triggered after each inference. These functions
            can be used for logging, monitoring, or other auxiliary tasks.

        Returns
        -------
        Any
            The output from the language model after processing the provided messages.

        Raises
        ------
        openai.error.RateLimitError
            If the number of retries exceeds the maximum or if the rate limit persists beyond the
            allotted time, the function will ultimately raise a RateLimitError.

        Example
        -------
        >>> messages = [SystemMessage(content="Hello"), HumanMessage(content="How's the weather?")]
        >>> callbacks = [some_logging_callback]
        >>> response = backoff_inference(messages, callbacks)
        """
        return self.llm(messages, callbacks=callbacks)  # type: ignore

    @staticmethod
    def serialize_messages(messages: List[Message]) -> str:
        """
        Serialize a list of messages to a JSON string.

        Parameters
        ----------
        messages : List[Message]
            The list of messages to serialize.

        Returns
        -------
        str
            The serialized messages as a JSON string.
        """
        return json.dumps(messages_to_dict(messages))

    @staticmethod
    def deserialize_messages(jsondictstr: str) -> List[Message]:
        """
        Deserialize a JSON string to a list of messages.

        Parameters
        ----------
        jsondictstr : str
            The JSON string to deserialize.

        Returns
        -------
        List[Message]
            The deserialized list of messages.
        """
        data = json.loads(jsondictstr)
        # Modify implicit is_chunk property to ALWAYS false
        # since Langchain's Message schema is stricter
        prevalidated_data = [
            {**item, "tools": {**item.get("tools", {}), "is_chunk": False}}
            for item in data
        ]
        return list(messages_from_dict(prevalidated_data))  # type: ignore

    def _create_chat_model(self) -> BaseChatModel:
        """
        Create a chat model with the specified model name and temperature.

        Parameters
        ----------
        model : str
            The name of the model to create.
        temperature : float
            The temperature to use for the model.

        Returns
        -------
        BaseChatModel
            The created chat model.
        """
        if self.azure_endpoint:
            return AzureChatOpenAI(
                openai_api_base=self.azure_endpoint,
                openai_api_version=os.getenv("OPENAI_API_VERSION", "2023-05-15"),
                deployment_name=self.model_name,
                openai_api_type="azure",
                streaming=self.streaming,
            )

        return ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            streaming=self.streaming,
            client=openai.ChatCompletion,
        )


def serialize_messages(messages: List[Message]) -> str:
    return AI.serialize_messages(messages)
