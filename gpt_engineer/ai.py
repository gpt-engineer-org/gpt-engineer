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
    def __init__(self, model="gpt-4", temperature=0.1):
        self.temperature = temperature
        self.model = model
        # llm = load_llm("llm.yaml")  # load llm from file
        try:
            self.chat = ChatOpenAI(model=self.model, temperature=temperature)
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

    """
    def messagesToLangChainHistory(messages):
        # convert messages array to LangChain History Object if necessary
        # from langchain.memory import ChatMessageHistory
        ChatMessageHistory()
        pass
    """

    def serializeMessages(messages):
        # dicts = messages_to_dict(history.messages)
        r = "[]"
        try:
            if messages and isinstance(messages, list) and len(messages) > 0:
                r = json.dumps(messages_to_dict(messages))
                logging.info("Serializing Message History:\n" + messages[0].content)
        except Exception as e:
            logging.warn("Exception serializing messages, returning empty array", e)
            # r = "[]"
        return r

    def deserializeMessages(jsondictstr):
        r = []
        try:
            r = messages_from_dict(json.loads(jsondictstr))
        except Exception as e:
            logging.warn("Exception deserializing messages, returning empty array", e)
        return r


"""
        response = openai.ChatCompletion.create(
            messages=messages,
            stream=True,
            model=self.model,
            temperature=self.temperature,
        )

        chat = []
        for chunk in response:
            delta = chunk["choices"][0]["delta"]
            msg = delta.get("content", "")
            print(msg, end="")
            chat.append(msg)
        print()
        messages += [{"role": "assistant", "content": "".join(chat)}]
        logger.debug(f"Chat completion finished: {messages}")
        return messages
"""

"""
# Custom JSON encoder
class MessageEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Message):
            # Convert Message object to a dictionary
            return {'role': obj.__class__, 'content': obj.content}
        # Let the base class encoder handle other types
        return super().default(obj)

# Custom JSON decoder
class MessageDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        # Override the object_hook parameter to use the custom object_hook method
        kwargs['object_hook'] = self.object_hook
        super().__init__(*args, **kwargs)

    def object_hook(self, dct):
        if 'role' in dct and 'content' in dct:
            # Convert dictionary to Message object
            role = Role(dct['role'])
            return Message(role, dct['content'])
        # Return the dictionary as is
        return dct
"""


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
