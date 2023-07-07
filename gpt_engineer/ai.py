from __future__ import annotations

import json
import logging
import re

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence

import openai
import tiktoken

from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.llms.loading import load_llm
from langchain.schema import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    messages_from_dict,
    messages_to_dict,
)

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
    def __init__(self, model_dir=None, model_name="gpt-4", temperature=0.1):
        self.temperature = temperature
        if model_dir:
            self.model_dir = Path(model_dir)
        else:
            # __file__ is "<package_dir>/gpt-engineer/ai.py"
            # therefore .parent.parent/models is "<package_dir>/models"
            self.model_dir = Path(__file__).resolve().parent.parent / "models"
        self.model_name = fallback_model(model_name)
        self.llm = None

        llm_filename = self.model_dir / f"{model_name}.yaml"
        try:
            logging.info(f"LLM file name: {llm_filename}")
            self.llm = load_llm(llm_filename)
        except Exception as e:
            raise RuntimeError(
                f"Unable to load LLM {model_name} from file {llm_filename}", e
            )

        # initialize token usage log
        self.cumulative_prompt_tokens = 0
        self.cumulative_completion_tokens = 0
        self.cumulative_total_tokens = 0
        self.token_usage_log = []

        # ToDo: Adapt to arbitrary model, currently assumes model using tiktoken
        try:
            self.tokenizer = tiktoken.encoding_for_model(model_name)
        except KeyError:
            logger.debug(
                f"Tiktoken encoder for model {model_name} not found. Using "
                "cl100k_base encoder instead. The results may therefore be "
                "inaccurate and should only be used as estimate."
            )
            self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def start(self, system: str, user: str, step_name: str) -> Sequence[BaseMessage]:
        messages = [
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

    def combine_messages(self, messages: Sequence[BaseMessage]) -> str:
        msg_dict = messages_to_dict(messages)
        logging.debug(msg_dict)
        prompt = "\n".join(
            "%s: %s" % (md["type"], md["data"]["content"]) for md in msg_dict
        )
        logging.debug("Prompt: " + prompt)
        return prompt

    def next(
        self,
        messages: Sequence[BaseMessage],
        prompt: Optional[str] = None,
        *,
        step_name: str,
    ) -> Sequence[BaseMessage]:
        if prompt:
            # need to make message a mutable list before we can change it
            messages = list(messages) + [self.fuser(prompt)]

        logger.debug(f"Creating a new chat completion: {messages}")

        msgs_as_prompt = self.combine_messages(messages)
        response = self.llm(msgs_as_prompt, callbacks=[StreamingStdOutCallbackHandler()])
        response = cleanup_reponse(response)

        # need to make message a mutable list before we can change it
        messages = list(messages) + [self.fassistant(response)]

        logger.debug(f"Chat completion finished: {messages}")

        self.update_token_usage_log(
            messages=messages, answer=response, step_name=step_name
        )

        return messages

    def last_message_content(self, messages: Sequence[BaseMessage]) -> str:
        m = messages[-1].content.strip()
        logging.info(m)
        return m

    @staticmethod
    def serialize_messages(messages: Sequence[BaseMessage]) -> str:
        return json.dumps(messages_to_dict(messages))

    @staticmethod
    def deserialize_messages(jsondictstr: str) -> Sequence[BaseMessage]:
        return messages_from_dict(json.loads(jsondictstr))

    def update_token_usage_log(
        self, messages: Sequence[BaseMessage], answer: str, step_name: str
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

    def num_tokens_from_messages(self, messages: Sequence[BaseMessage]) -> int:
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
        return "gpt-3.5-turbo-16k"


def serialize_messages(messages: Sequence[BaseMessage]) -> str:
    return AI.serialize_messages(messages)


def cleanup_reponse(response: str) -> str:
    response = re.sub(
        "\\n", "\n", response
    )  # for some reason models sometimes return \n instead of newline?
    return response
