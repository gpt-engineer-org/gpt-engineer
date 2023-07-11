from __future__ import annotations

import json
import logging

from dataclasses import dataclass
from typing import List, Optional, Sequence, Union

import openai
import tiktoken

from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.chat_models.base import BaseChatModel
from langchain.schema import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    messages_from_dict,
    messages_to_dict,
)

Message = Union[AIMessage, HumanMessage, SystemMessage]

logger = logging.getLogger(__name__)


@dataclass
class TokenUsage:
    step_name: str
    in_step_prompt_tokens: int
    in_step_completion_tokens: int
    in_step_total_tokens: int
    total_prompt_tokens: int
    total_completion_tokens: int
    total_tokens: int


class AI:
    def __init__(self, model_name="gpt-4", temperature=0.1):
        self.temperature = temperature
        self.model_name = fallback_model(model_name)
        self.llm = create_chat_model(self.model_name, temperature)
        self.tokenizer = get_tokenizer(self.model_name)

        # initialize token usage log
        self.cumulative_prompt_tokens = 0
        self.cumulative_completion_tokens = 0
        self.cumulative_total_tokens = 0
        self.token_usage_log = []

    def start(self, system: str, user: str, step_name: str) -> List[Message]:
        messages: List[Message] = [
            SystemMessage(content=system),
            HumanMessage(content=user),
        ]
        return self.next(messages, step_name=step_name)

    def fsystem(self, msg: str) -> SystemMessage:
        return SystemMessage(content=msg)

    def fuser(self, msg: str) -> HumanMessage:
        return HumanMessage(content=msg)

    def fassistant(self, msg: str) -> AIMessage:
        return AIMessage(content=msg)

    def next(
        self,
        messages: List[Message],
        prompt: Optional[str] = None,
        *,
        step_name: str,
    ) -> List[Message]:
        if prompt:
            messages.append(self.fuser(prompt))

        logger.debug(f"Creating a new chat completion: {messages}")

        response = self.llm(messages, callbacks=[StreamingStdOutCallbackHandler()])
        messages.append(response)

        logger.debug(f"Chat completion finished: {messages}")

        self.update_token_usage_log(
            messages=messages, answer=response.content, step_name=step_name
        )

        return messages

    def last_message_content(self, messages: List[Message]) -> str:
        m = messages[-1].content.strip()
        return m

    @staticmethod
    def serialize_messages(messages: List[Message]) -> str:
        return json.dumps(messages_to_dict(messages))

    @staticmethod
    def deserialize_messages(jsondictstr: str) -> List[Message]:
        return AI.parse_langchain_basemessages(
            messages_from_dict(json.loads(jsondictstr))
        )

    @staticmethod
    def parse_langchain_basemessages(messages: Sequence[BaseMessage]) -> List[Message]:
        """LangChain saves message history as Sequence[BaseMessage], which is immutable.
        To make our code cleaner, we parse it to List[Message], which is mutable."""
        parsed_messages = []

        msg_type_to_cls = {
            msg_cls(content="").type: msg_cls
            for msg_cls in [AIMessage, HumanMessage, SystemMessage]
        }

        for m in messages:
            parsed_messages.append(msg_type_to_cls[m.type](content=m.content))

        return parsed_messages

    def update_token_usage_log(
        self, messages: List[Message], answer: str, step_name: str
    ) -> None:
        prompt_tokens = self.num_tokens_from_messages(messages)
        completion_tokens = self.num_tokens(answer)
        total_tokens = prompt_tokens + completion_tokens

        self.cumulative_prompt_tokens += prompt_tokens
        self.cumulative_completion_tokens += completion_tokens
        self.cumulative_total_tokens += total_tokens

        self.token_usage_log.append(
            TokenUsage(
                step_name=step_name,
                in_step_prompt_tokens=prompt_tokens,
                in_step_completion_tokens=completion_tokens,
                in_step_total_tokens=total_tokens,
                total_prompt_tokens=self.cumulative_prompt_tokens,
                total_completion_tokens=self.cumulative_completion_tokens,
                total_tokens=self.cumulative_total_tokens,
            )
        )

    def format_token_usage_log(self) -> str:
        result = "step_name,"
        result += "prompt_tokens_in_step,completion_tokens_in_step,total_tokens_in_step"
        result += ",total_prompt_tokens,total_completion_tokens,total_tokens\n"
        for log in self.token_usage_log:
            result += log.step_name + ","
            result += str(log.in_step_prompt_tokens) + ","
            result += str(log.in_step_completion_tokens) + ","
            result += str(log.in_step_total_tokens) + ","
            result += str(log.total_prompt_tokens) + ","
            result += str(log.total_completion_tokens) + ","
            result += str(log.total_tokens) + "\n"
        return result

    def num_tokens(self, txt: str) -> int:
        return len(self.tokenizer.encode(txt))

    def num_tokens_from_messages(self, messages: List[Message]) -> int:
        """Returns the number of tokens used by a list of messages."""
        n_tokens = 0
        for message in messages:
            n_tokens += (
                4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
            )
            n_tokens += self.num_tokens(message.content)
        n_tokens += 2  # every reply is primed with <im_start>assistant
        return n_tokens


def fallback_model(model: str) -> str:
    try:
        openai.Model.retrieve(model)
        return model
    except openai.InvalidRequestError:
        print(
            f"Model {model} not available for provided API key. Reverting "
            "to gpt-3.5-turbo. Sign up for the GPT-4 wait list here: "
            "https://openai.com/waitlist/gpt-4-api\n"
        )
        return "gpt-3.5-turbo"


def create_chat_model(model: str, temperature) -> BaseChatModel:
    if model == "gpt-4":
        return ChatOpenAI(
            model="gpt-4",
            temperature=temperature,
            streaming=True,
            client=openai.ChatCompletion,
        )
    elif model == "gpt-3.5-turbo":
        return ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=temperature,
            streaming=True,
            client=openai.ChatCompletion,
        )
    else:
        raise ValueError(f"Model {model} is not supported.")


def get_tokenizer(model: str):
    if "gpt-4" in model or "gpt-3.5" in model:
        return tiktoken.encoding_for_model(model)

    logger.debug(
        f"No encoder implemented for model {model}."
        "Defaulting to tiktoken cl100k_base encoder."
        "Use results only as estimates."
    )
    return tiktoken.get_encoding("cl100k_base")


def serialize_messages(messages: List[Message]) -> str:
    return AI.serialize_messages(messages)
