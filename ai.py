
import openai

class AI:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def start(self, system, user):
        messages = [
            {"role": "system", "content": system},  # System message
            {"role": "user", "content": user},      # User message
        ]

        return self.next(messages)

    def fsystem(self, msg):
        return {"role": "system", "content": msg}  # Construct system message object
    
    def fuser(self, msg):
        return {"role": "user", "content": msg}    # Construct user message object

    def next(self, messages: list[dict[str, str]], prompt=None):
        if prompt:
            messages = messages + [{"role": "user", "content": prompt}]  # Add prompt as user message

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
        return messages + [{"role": "assistant", "content": "".join(chat)}]  # Add assistant's message to chat history

# Create an instance of the AI class
ai = AI()

# Example usage:
# Start a conversation with a system message and a user message
ai.start("Hello, how can I assist you?", "Can you provide information about your products?")
