from __future__ import annotations

import logging
import os

import openai

logger = logging.getLogger(__name__)


class AI:
    def __init__(self, model="gpt-4", temperature=0.1, is_azure=False):
        self.temperature = temperature
        self.model = model
        self.is_azure = is_azure

        if self.is_azure:
            # set up azure openai
            if not os.getenv("AZURE_OPENAI_ENDPOINT"):
                raise ValueError("To use Azure OpenAI models please set a "
                                "AZURE_OPENAI_ENDPOINT enviroment variable.") 
            if not os.getenv("AZURE_OPENAI_KEY"):
                raise ValueError("To use Azure OpenAI models please set a "
                                "AZURE_OPENAI_KEY enviroment variable.") 
    
            if api_version := os.getenv("AZURE_API_VERSION") is None:
                openai.api_version = "2023-05-15"
            else:
                openai.api_version = api_version
            openai.api_type = "azure"
            openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT") 
            openai.api_key = os.getenv("AZURE_OPENAI_KEY")


    def start(self, system, user):
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]

        return self.next(messages)

    def fsystem(self, msg):
        return {"role": "system", "content": msg}

    def fuser(self, msg):
        return {"role": "user", "content": msg}

    def fassistant(self, msg):
        return {"role": "assistant", "content": msg}

    def next(self, messages: list[dict[str, str]], prompt=None):
        if prompt:
            messages += [{"role": "user", "content": prompt}]

        logger.debug(f"Creating a new chat completion: {messages}")

        shared_params = {
            "messages": messages,
            "stream": True,
            "temperature": self.temperature,
        }
        if not self.is_azure:
            # use OpenAI's models directly
            response = openai.ChatCompletion.create(model=self.model, **shared_params)
        else:
            # use Azure OpenAI
            response = openai.ChatCompletion.create(engine=self.model, **shared_params)

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
