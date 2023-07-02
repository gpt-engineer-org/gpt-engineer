from __future__ import annotations

import json
import logging

import openai

from langchain.chat_models import ChatOpenAI
from langchain.schema import (  # serialization
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
        self.modelid = modelid
        # llm = load_llm("llm.yaml")  # load llm from file
        try:
            self.chat = ChatOpenAI(model=self.modelid, temperature=temperature)
        except Exception as e:
            # ? try a different model
            logging.warning(e)

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

    def next(self, messages: list[dict[str, str]], prompt=None):
        if prompt:
            messages += [self.fuser(prompt)]

        logger.debug(f"Creating a new chat completion: {messages}")

        r = self.chat(messages)
        messages += [r]  # AI Message

        logger.debug(f"Chat completion finished: {messages}")
        return messages

    def lastMessageContent(self, messages):
        m = messages[-1].content
        if m:
            m = m.strip()
        # logging.info(m)
        print(m)
        return m

    def serializeMessages(messages):
        # dicts = messages_to_dict(history.messages)
        r = "[]"
        try:
            if messages and isinstance(messages, list) and len(messages) > 0:
                r = json.dumps(messages_to_dict(messages))
        except Exception as e:
            logging.warn("Exception serializing messages, returning empty array", e)
        return r

    def deserializeMessages(jsondictstr):
        r = []
        try:
            r = messages_from_dict(json.loads(jsondictstr))
        except Exception as e:
            logging.warn("Exception deserializing messages, returning empty array", e)
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


def serializeMessages(messages):
    return AI.serializeMessages(messages)
