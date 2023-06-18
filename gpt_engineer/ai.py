from gpt4all import GPT4All
from typing import List, Dict

class AI:
    model: GPT4All = None

    def __init__(self, model, **kwargs):
        self.kwargs = kwargs

        try:
            if not AI.model:
                AI.model = GPT4All(model)
        except Exception:
            print("Unexpected error")

    def start(self, system, user):
        messages = [
            {"role": "system", "content": f"### Instruction: {system}"},
            {"role": "user", "content": user},
        ]

        return self.next(messages)

    def fsystem(self, msg):
        return {"role": "system", "content": msg}

    def fuser(self, msg):
        return {"role": "user", "content": msg
    
    def fassistant(self, msg):
        return {"role": "assistant", "content": msg}

    def next(self, messages: list[dict[str, str]], prompt=None):
        if "### System:" not in messages[0]["content"]:
            messages[0]["content"] = "### System: " + messages[0]["content"]
        if prompt:
            messages = messages + [{"role": "user", "content": f'### Prompt: \n{prompt}'}]

        response = AI.model.chat_completion(messages=messages, verbose=True, streaming=True, default_prompt_header=False, n_ctx=4096, n_predict=2048, **self.kwargs)

        return messages + [response['choices'][0]['message']]
