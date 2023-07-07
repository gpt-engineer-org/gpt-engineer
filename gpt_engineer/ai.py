from __future__ import annotations

import json
import logging
import re

from pathlib import Path

import openai

from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.llms.loading import load_llm
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    messages_from_dict,
    messages_to_dict,
)

logger = logging.getLogger(__name__)


class AI:
    def __init__(self, modelid="gpt-4", temperature=0.1):
        self.temperature = temperature
        # __file__ is "<package_dir>/gpt-engineer/ai.py"
        # therefore .parent.parent/models is "<package_dir>/models"
        self.modeldir = Path(__file__).resolve().parent.parent / "models"
        self.modelid = fallback_model(modelid)
        self.llm = None

        try:
            llm_filename = self.modeldir / f"{modelid}.yaml"
            logging.info(f"LLM file name: {llm_filename}")
            self.llm = load_llm(llm_filename)
        except Exception as e:
            raise RuntimeError(f"Unable to load LLM {modelid} from file", e)

    def start(self, system, user):
        messages = [
            SystemMessage(content=system),
            HumanMessage(content=user),
        ]

        return self.next(messages)

    def fsystem(self, msg):
        return SystemMessage(content=msg)

    def fuser(self, msg):
        return HumanMessage(content=msg)

    def fassistant(self, msg):
        return AIMessage(content=msg)

    def combine_messages(self, messages: list[dict[str, str]]):
        msg_dict = messages_to_dict(messages)
        logging.debug(msg_dict)
        prompt = "\n".join(
            "%s: %s" % (md["type"], md["data"]["content"]) for md in msg_dict
        )
        logging.debug("Prompt: " + prompt)
        return prompt

    def next(self, messages: list[dict[str, str]], prompt=None):
        if prompt:
            messages += [self.fuser(prompt)]

        logger.debug(f"Creating a new chat completion: {messages}")

        msgs_as_prompt = self.combine_messages(messages)
        response = self.llm(msgs_as_prompt, callbacks=[StreamingStdOutCallbackHandler()])
        response = cleanup_reponse(response)

        messages += [self.fassistant(response)]

        logger.debug(f"Chat completion finished: {messages}")

        return messages

    def last_message_content(self, messages):
        m = messages[-1].content
        if m:
            m = m.strip()
        logging.info(m)
        print(m)
        return m

    def serialize_messages(messages):
        r = "[]"
        if messages and isinstance(messages, list) and len(messages) > 0:
            r = json.dumps(messages_to_dict(messages))
        return r

    def deserialize_messages(jsondictstr):
        r = messages_from_dict(json.loads(jsondictstr))
        return r


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


def serialize_messages(messages):
    return AI.serialize_messages(messages)


def cleanup_reponse(response):
    response = re.sub(
        "\\n", "\n", response
    )  # for some reason models sometimes return \n instead of newline?
    return response
