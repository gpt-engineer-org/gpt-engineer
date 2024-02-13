"""
This module provides functionality to print a conversation with messages
colored according to the role of the speaker.
"""

import json

import typer

from termcolor import colored

app = typer.Typer()


def pretty_print_conversation(messages):
    """
    Prints a conversation with messages formatted and colored by role.

    Parameters
    ----------
    messages : list
        A list of message dictionaries, each containing 'role', 'name', and 'content' keys.

    """

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
        role = messages[formatted_messages.index(formatted_message)]["role"]
        color = role_to_color[role]
        print(colored(formatted_message, color))


@app.command()
def main(
    messages_path: str,
):
    """
    Main function that loads messages from a JSON file and prints them using pretty formatting.

    Parameters
    ----------
    messages_path : str
        The file path to the JSON file containing the messages.

    """
    with open(messages_path) as f:
        messages = json.load(f)

    pretty_print_conversation(messages)


if __name__ == "__main__":
    app()
