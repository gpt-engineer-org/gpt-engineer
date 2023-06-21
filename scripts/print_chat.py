import json

import typer

from termcolor import colored

app = typer.Typer()


def pretty_print_conversation(messages):
    role_to_color = {
        "system": "red",
        "user": "green",
        "assistant": "blue",
        "function": "magenta",
    }
    formatted_messages = []
    for message in messages:
        if message["role"] == "function":
            formatted_messages.append(
                f"function ({message['name']}): {message['content']}\n"
            )
        else:
            assistant_content = (
                message["function_call"]
                if message.get("function_call")
                else message["content"]
            )
            role_to_message = {
                "system": f"system: {message['content']}\n",
                "user": f"user: {message['content']}\n",
                "assistant": f"assistant: {assistant_content}\n",
            }
            formatted_messages.append(role_to_message[message["role"]])

    for formatted_message in formatted_messages:
        print(
            colored(
                formatted_message,
                role_to_color[
                    messages[formatted_messages.index(formatted_message)]["role"]
                ],
            )
        )


@app.command()
def main(
    messages_path: str,
):
    with open(messages_path) as f:
        messages = json.load(f)

    pretty_print_conversation(messages)


if __name__ == "__main__":
    app()
