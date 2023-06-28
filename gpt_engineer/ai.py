from __future__ import annotations

import logging

import tiktoken
import openai

logger = logging.getLogger(__name__)


class AI:
    def __init__(self, model="gpt-4", temperature=0.1):
        self.temperature = temperature
        self.model = model

        # initialize token usage log
        self.cumulative_prompt_tokens = 0
        self.cumulative_completion_tokens = 0
        self.cumulative_total_tokens = 0
        self.token_usage_log = []

        try:
            self.tokenizer = tiktoken.encoding_for_model(model)
        except KeyError:
            logger.debug(f"Tiktoken encoder for model {model} not found. Using "
                        "cl100k_base encoder instead. The results may therefore be "
                        "inaccurate and should only be used as estimate.")
            self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def start(self, system, user, step_name):
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]

        return self.next(messages, step_name=step_name)

    def fsystem(self, msg):
        return {"role": "system", "content": msg}

    def fuser(self, msg):
        return {"role": "user", "content": msg}

    def fassistant(self, msg):
        return {"role": "assistant", "content": msg}

    def next(self, messages: list[dict[str, str]], prompt=None, *, step_name=None):
        if prompt:
            messages += [{"role": "user", "content": prompt}]

        logger.debug(f"Creating a new chat completion: {messages}")
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

        self.update_token_usage_log(messages=messages, answer="".join(chat),
                                    step_name=step_name)

        return messages

    def update_token_usage_log(self, messages, answer, step_name):
        prompt_tokens = self.num_tokens_from_messages(messages)
        completion_tokens = self.num_tokens(answer)
        total_tokens = prompt_tokens + completion_tokens

        self.cumulative_prompt_tokens += prompt_tokens
        self.cumulative_completion_tokens += completion_tokens
        self.cumulative_total_tokens += total_tokens

        self.token_usage_log.append({
            "step_name": step_name,
            "in_step": {
                "prompt": prompt_tokens,
                "completion": completion_tokens,
                "total": total_tokens
            },
            "total": {
                "prompt": self.cumulative_prompt_tokens,
                "completion": self.cumulative_completion_tokens,
                "total": self.cumulative_total_tokens,
            }
        })

    def format_token_usage_log(self):
        result = "step_name,"
        result += "prompt_tokens_in_step,completion_tokens_in_step,total_tokens_in_step"
        result += ",total_prompt_tokens,total_completion_tokens,total_tokens\n"
        for l in self.token_usage_log:
            result += l["step_name"] + ","
            result += str(l["in_step"]["prompt"]) + ","
            result += str(l["in_step"]["completion"]) + ","
            result += str(l["in_step"]["total"]) + ","
            result += str(l["total"]["prompt"]) + ","
            result += str(l["total"]["completion"]) + ","
            result += str(l["total"]["total"]) + "\n"
        return result

    def num_tokens(self, txt):
        return len(self.tokenizer.encode(txt))

    def num_tokens_from_messages(self, messages):
        """Returns the number of tokens used by a list of messages."""
        n_tokens = 0
        for message in messages:
            n_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
            for key, value in message.items():
                n_tokens += self.num_tokens(value)
                if key == "name":  # if there's a name, the role is omitted
                    n_tokens += -1  # role is always required and always 1 token
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
