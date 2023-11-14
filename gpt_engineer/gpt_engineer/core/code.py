from typing import MutableMapping
from pathlib import Path


# class Code(MutableMapping[str | Path, str]):
# ToDo: implement as mutable mapping, potentially holding a dict instead of being a dict.
class Code(dict):
    """
    A dictionary subclass that represents a collection of code files.

    This class extends the standard dictionary to enforce string keys and values,
    representing filenames and their respective code content. It provides a method
    to format the code into a chat-friendly string for AI interactions.
    """

    def __setitem__(self, key, value):
        if not isinstance(key, str | Path):
            raise TypeError("Keys must be strings or Path's")
        if not isinstance(value, str):
            raise TypeError("Values must be strings")
        super().__setitem__(key, value)

    def to_chat(self):
        def format_file_to_input(file_name: str, file_content: str) -> str:
            """
            Format a file string to use as input to the AI agent.

            Parameters
            ----------
            file_name : str
                The name of the file.
            file_content : str
                The content of the file.

            Returns
            -------
            str
                The formatted file string.
            """
            file_str = f"""
{file_name}
```
{file_content}
            ```
            """
            return file_str

        return "\n".join(
            [
                format_file_to_input(file_name, file_content) + "\n"
                for file_name, file_content in self.items()
            ]
        )
