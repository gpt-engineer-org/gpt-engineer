import openai


class AI:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

        try:
            openai.Model.retrieve("gpt-4")
        except openai.error.InvalidRequestError:
            print("Model gpt-4 not available for provided api key reverting "
                  "to gpt-3.5.turbo. Sign up for the gpt-4 wait list here: "
                  "https://openai.com/waitlist/gpt-4-api")
            self.kwargs['model'] = "gpt-3.5-turbo"

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

    def next(self, messages: list[dict[str, str]], prompt=None):
        if prompt:
            messages = messages + [{"role": "user", "content": prompt}]

        response = openai.ChatCompletion.create(
            messages=messages, stream=True, **self.kwargs
        )

        chat = []
        for chunk in response:
            delta = chunk["choices"][0]["delta"]
            msg = delta.get("content", "")
            print(msg, end="")
            chat.append(msg)
        return messages + [{"role": "assistant", "content": "".join(chat)}]
