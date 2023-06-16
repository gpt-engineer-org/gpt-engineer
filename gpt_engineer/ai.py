import openai
from typing import List, Dict, Union


class AI:
    def __init__(self, **kwargs: Union[str, int, bool]):
        self.kwargs = kwargs

        try:
            # Check if gpt-4 model is available
            openai.Model.retrieve("gpt-4")
        except openai.error.InvalidRequestError:
            # If gpt-4 is not available, fallback to gpt-3.5-turbo
            print("Model gpt-4 not available for the provided API key. Reverting to gpt-3.5-turbo.")
            print("Sign up for the gpt-4 waitlist here: https://openai.com/waitlist/gpt-4-api")
            self.kwargs['model'] = "gpt-3.5-turbo"

    def start(self, system: str, user: str) -> List[Dict[str, str]]:
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]

        return self.next(messages)

    def fsystem(self, msg: str) -> Dict[str, str]:
        return {"role": "system", "content": msg}

    def fuser(self, msg: str) -> Dict[str, str]:
        return {"role": "user", "content": msg}

    def next(self, messages: List[Dict[str, str]], prompt: str = None) -> List[Dict[str, str]]:
        if prompt:
            messages = messages + [{"role": "user", "content": prompt}]

        response = openai.ChatCompletion.create(
            messages=messages, stream=True, **self.kwargs
        )

        chat = []
        for chunk in response:
            delta = chunk['choices'][0]['delta']
            msg = delta.get('content', '')
            print(msg, end="")
            chat.append(msg)

        return messages + [{"role": "assistant", "content": "".join(chat)}]
