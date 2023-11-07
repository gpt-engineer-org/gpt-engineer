from typing import TypeVar, Dict

class Code(dict):

    def __setitem__(self, key, value):
        if not isinstance(key, str):
            raise TypeError("Keys must be strings")
        if not isinstance(value, str):
            raise TypeError("Values must be integers")
        super().__setitem__(key, value)

    def to_string(self):
        return "\n".join([key + "\n" + val + "\n" for key, val in self.items()])