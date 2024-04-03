"""
This module provides functionality to print a conversation with messages
colored according to the role of the speaker.
"""

import json
import os
from typing import List

import typer
from termcolor import colored

app = typer.Typer()

# Dictionary to map roles to colors
role_to_color = {
    "system": "red",
    "user": "green",
    "assistant": "blue",
    "function": "magenta",
}


def load_messages(messages_path: str) -> List[dict]:
    """
    Load messages from a JSON file.

    Parameters
    ----------
    messages_path : str
        The file path to the JSON file containing the messages.

    Returns
    -------
    list
        A list of message dictionaries, each containing 'role', 'name', and 'content' keys.

    Raises
    ------
    FileNotFoundError
        If the specified file does not exist.
    ValueError
        If the file is not a JSON file or if the JSON file is not properly formatted.
    """
    if not os.path.exists(messages_path):
        raise FileNotFoundError(f"The file '{messages_path}' does not exist.")

    if not messages_path.endswith('.json'):
        raise ValueError("The file provided is not a JSON file.")

    try:
        with open(messages_path) as f:
            messages = json.load(f)
    except json.JSONDecodeError:
        raise ValueError("The JSON file is not properly formatted.")

    return messages


def format_message(message: dict) -> str:
    """
    Format a single message based on its role.

    Parameters
    ----------
    message : dict
        A dictionary representing a single message with 'role', 'name', and 'content' keys.

    Returns
    -------
    str
        The formatted message.
    """
    if message["role"] == "function":
        return f"function ({message['name']}): {message['content']}\n"
    else:
        assistant_content = message["function_call"] if message.get("function_call") else message["content"]
        return f"{message['role']}: {assistant_content}\n"


def pretty_print_conversation(messages: List[dict]):
    """
    Prints a conversation with messages formatted and colored by role.

    Parameters
    ----------
    messages : list
        A list of message dictionaries, each containing 'role', 'name', and 'content' keys.
    """
    formatted_messages = [format_message(message) for message in messages]
    for idx, formatted_message in enumerate(formatted_messages):
        role = messages[idx]["role"]
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
    messages = load_messages(messages_path)
    pretty_print_conversation(messages)


if __name__ == "__main__":
    app()
