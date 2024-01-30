"""
FilesDict Module

This module provides a FilesDict class which is a dictionary-based container for managing code files.
It extends the standard dictionary to enforce string keys and values, representing filenames and their
corresponding code content. It also provides methods to format its contents for chat-based interaction
with an AI agent and to enforce type checks on keys and values.

Classes:
    FilesDict: A dictionary-based container for managing code files.
"""
from pathlib import Path
from typing import Union


# class Code(MutableMapping[str | Path, str]):
# ToDo: implement as mutable mapping, potentially holding a dict instead of being a dict.
class FilesDict(dict):
    """
    A dictionary-based container for managing code files.

    This class extends the standard dictionary to enforce string keys and values,
    representing filenames and their corresponding code content. It provides methods
    to format its contents for chat-based interaction with an AI agent and to enforce
    type checks on keys and values.

    Methods
    -------
    __setitem__(self, key, value)
        Set the code content for the given filename, enforcing type checks on the key and value.
    to_chat(self)
        Format the code files for chat-based interaction, returning a string suitable for AI input.
    """

    def __setitem__(self, key: Union[str, Path], value: str):
        """
        Set the code content for the given filename, enforcing type checks on the key and value.

        Overrides the dictionary's __setitem__ to enforce type checks on the key and value.
        The key must be a string or a Path object, and the value must be a string representing
        the code content.

        Parameters
        ----------
        key : Union[str, Path]
            The filename as a key for the code content.
        value : str
            The code content to associate with the filename.

        Raises
        ------
        TypeError
            If the key is not a string or Path, or if the value is not a string.
        """
        if not isinstance(key, (str, Path)):
            raise TypeError("Keys must be strings or Path's")
        if not isinstance(value, str):
            raise TypeError("Values must be strings")
        super().__setitem__(key, value)

    def to_chat(self):
        def format_file_to_input(file_name: str, file_content: str) -> str:
            """
            Format a file string to use as input to the AI agent.

            Takes the name and content of a file and formats it into a string that is suitable
            for input to an AI agent, enclosed within markdown code block fences.

            Parameters
            ----------
            file_name : str
                The name of the file to format.
            file_content : str
                The content of the file to format.

            Returns
            -------
            str
                The formatted file string, ready for AI input.
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
