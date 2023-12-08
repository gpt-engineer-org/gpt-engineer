from typing import MutableMapping
from pathlib import Path


# class Code(MutableMapping[str | Path, str]):
# ToDo: implement as mutable mapping, potentially holding a dict instead of being a dict.
class FilesDict(dict):
    """
    A dictionary-based container for managing code files.

    This class extends the standard dictionary to enforce string keys and values,
    representing filenames and their corresponding code content. It provides a method
    to format its contents for chat-based interaction with an AI agent.

    Methods
    -------
    to_chat() -> str:
        Format the code files for chat-based interaction, returning a string suitable for AI input.
    """

    def __setitem__(self, key, value):
        """
        Set the code content for the given filename.

        This method overrides the dictionary's __setitem__ to enforce type checks on the key and value.
        The key must be a string or a Path object, and the value must be a string representing the code content.

        Parameters
        ----------
        key : str | Path
            The filename as a key for the code content.
        value : str
            The code content to associate with the filename.
        """
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
