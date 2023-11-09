from typing import MutableMapping
from pathlib import Path


# class Code(MutableMapping[str | Path, str]):
# ToDo: implement as mutable mapping, potentially holding a dict instead of being a dict.
class Code(dict):
    def __setitem__(self, key, value):
        if not isinstance(key, str | Path):
            raise TypeError("Keys must be strings")
        if not isinstance(value, str):
            raise TypeError("Values must be strings")
        super()[key] = value

    def to_string(self):
        return "\n".join([key + "\n" + val + "\n" for key, val in self.items()])
