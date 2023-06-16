from enum import Enum
from typing import Any, Callable, Dict

from .gpt import GPT
from .test import TestAI
from .ai import AI

class ModelName(str, Enum):
    GPT4 = "gpt-4"
    GPT35_TURBO = "gpt-3.5-turbo"
    TEST = "test"


models: Dict[ModelName, Callable[[Any,], AI]] = {
    ModelName.GPT4: GPT,
    ModelName.GPT35_TURBO: GPT,
    ModelName.TEST: TestAI
}
default_model_name: ModelName = ModelName.GPT4