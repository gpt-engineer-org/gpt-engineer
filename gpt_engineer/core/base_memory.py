"""
Base Memory Module

This module provides a type alias for a mutable mapping that represents the base memory structure
used in the GPT Engineer project. The base memory is a mapping from file names (as strings or Path objects)
to their corresponding code content (as strings).

Type Aliases:
    BaseMemory: A mutable mapping from file names to code content.
"""

from pathlib import Path
from typing import MutableMapping, Union

BaseMemory = MutableMapping[Union[str, Path], str]
