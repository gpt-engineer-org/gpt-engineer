
import openai

openai.api_key = "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"


class AI:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.testWorking()

        
    def testWorking(self):
        try: openai.ChatCompletion.create(
            messages=[{"role": "user", "content": "Testing"}],
            stream=True,
            max_tokens=1,
            **self.kwargs
        )
        except Exception as e:
            print(e)
            if str(e) != "The model: `gpt-4` does not exist": exit()
            self.kwargs['model'] = 'gpt-3.5-turbo'
            print('Switching over to model gpt-3.5-turbo')
            self.testWorking()

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
            messages=messages,
            stream=True,
            **self.kwargs
        )

        chat = []
        for chunk in response:
            delta = chunk['choices'][0]['delta']
            msg = delta.get('content', '')
            print(msg, end="")
            chat.append(msg)
        return messages + [{"role": "assistant", "content": "".join(chat)}]