import base64
import io
import logging
import math

from dataclasses import dataclass
from typing import List, Union

import tiktoken

from langchain.schema import AIMessage, HumanMessage, SystemMessage
from PIL import Image

# workaround for function moved in:
# https://github.com/langchain-ai/langchain/blob/535db72607c4ae308566ede4af65295967bb33a8/libs/community/langchain_community/callbacks/openai_info.py
try:
    from langchain.callbacks.openai_info import (
        get_openai_token_cost_for_model,  # fmt: skip
    )
except ImportError:
    from langchain_community.callbacks.openai_info import (
        get_openai_token_cost_for_model,  # fmt: skip
    )


Message = Union[AIMessage, HumanMessage, SystemMessage]

logger = logging.getLogger(__name__)


@dataclass
class TokenUsage:
    """
    Dataclass representing token usage statistics for a conversation step.

    Attributes
    ----------
    step_name : str
        The name of the conversation step.
    in_step_prompt_tokens : int
        The number of prompt tokens used in the step.
    in_step_completion_tokens : int
        The number of completion tokens used in the step.
    in_step_total_tokens : int
        The total number of tokens used in the step.
    total_prompt_tokens : int
        The cumulative number of prompt tokens used up to this step.
    total_completion_tokens : int
        The cumulative number of completion tokens used up to this step.
    total_tokens : int
        The cumulative total number of tokens used up to this step.
    """

    """
    Represents token usage statistics for a conversation step.
    """

    step_name: str
    in_step_prompt_tokens: int
    in_step_completion_tokens: int
    in_step_total_tokens: int
    total_prompt_tokens: int
    total_completion_tokens: int
    total_tokens: int


class Tokenizer:
    """
    Tokenizer for counting tokens in text.
    """

    def __init__(self, model_name):
        self.model_name = model_name
        self._tiktoken_tokenizer = (
            tiktoken.encoding_for_model(model_name)
            if "gpt-4" in model_name or "gpt-3.5" in model_name
            else tiktoken.get_encoding("cl100k_base")
        )

    def num_tokens(self, txt: str) -> int:
        """
        Get the number of tokens in a text.

        Parameters
        ----------
        txt : str
            The text to count the tokens in.

        Returns
        -------
        int
            The number of tokens in the text.
        """
        return len(self._tiktoken_tokenizer.encode(txt))

    def num_tokens_for_base64_image(
        self, image_base64: str, detail: str = "high"
    ) -> int:
        """
        Calculate the token size for a base64 encoded image based on OpenAI's token calculation rules.

        Parameters:
        - image_base64 (str): The base64 encoded string of the image.
        - detail (str): The detail level of the image, 'low' or 'high'.

        Returns:
        - int: The token size of the image.
        """

        if detail == "low":
            return 85  # Fixed cost for low detail images

        # Decode image from base64
        image_data = base64.b64decode(image_base64)

        # Convert byte data to image for size extraction
        image = Image.open(io.BytesIO(image_data))

        # Calculate the initial scale to fit within 2048 square while maintaining aspect ratio
        max_dimension = max(image.size)
        scale_factor = min(2048 / max_dimension, 1)  # Ensure we don't scale up
        new_width = int(image.size[0] * scale_factor)
        new_height = int(image.size[1] * scale_factor)

        # Scale such that the shortest side is 768px
        shortest_side = min(new_width, new_height)
        if shortest_side > 768:
            resize_factor = 768 / shortest_side
            new_width = int(new_width * resize_factor)
            new_height = int(new_height * resize_factor)

        # Calculate the number of 512px tiles needed
        width_tiles = math.ceil(new_width / 512)
        height_tiles = math.ceil(new_height / 512)
        total_tiles = width_tiles * height_tiles

        # Each tile costs 170 tokens, plus a base cost of 85 tokens for high detail
        token_cost = total_tiles * 170 + 85

        return token_cost

    def num_tokens_from_messages(self, messages: List[Message]) -> int:
        """
        Get the total number of tokens used by a list of messages, accounting for text and base64 encoded images.

        Parameters
        ----------
        messages : List[Message]
            The list of messages to count the tokens in.

        Returns
        -------
        int
            The total number of tokens used by the messages.
        """
        n_tokens = 0
        for message in messages:
            n_tokens += 4  # Account for message framing tokens

            if isinstance(message.content, str):
                # Content is a simple string
                n_tokens += self.num_tokens(message.content)
            elif isinstance(message.content, list):
                # Content is a list, potentially mixed with text and images
                for item in message.content:
                    if item.get("type") == "text":
                        n_tokens += self.num_tokens(item["text"])
                    elif item.get("type") == "image_url":
                        image_detail = item["image_url"].get("detail", "high")
                        image_base64 = item["image_url"].get("url")
                        n_tokens += self.num_tokens_for_base64_image(
                            image_base64, detail=image_detail
                        )

            n_tokens += 2  # Account for assistant's reply framing tokens

        return n_tokens


class TokenUsageLog:
    """
    Represents a log of token usage statistics for a conversation.
    """

    def __init__(self, model_name):
        self.model_name = model_name
        self._cumulative_prompt_tokens = 0
        self._cumulative_completion_tokens = 0
        self._cumulative_total_tokens = 0
        self._log = []
        self._tokenizer = Tokenizer(model_name)

    def update_log(self, messages: List[Message], answer: str, step_name: str) -> None:
        """
        Update the token usage log with the number of tokens used in the current step.

        Parameters
        ----------
        messages : List[Message]
            The list of messages in the conversation.
        answer : str
            The answer from the AI.
        step_name : str
            The name of the step.
        """
        prompt_tokens = self._tokenizer.num_tokens_from_messages(messages)
        completion_tokens = self._tokenizer.num_tokens(answer)
        total_tokens = prompt_tokens + completion_tokens

        self._cumulative_prompt_tokens += prompt_tokens
        self._cumulative_completion_tokens += completion_tokens
        self._cumulative_total_tokens += total_tokens

        self._log.append(
            TokenUsage(
                step_name=step_name,
                in_step_prompt_tokens=prompt_tokens,
                in_step_completion_tokens=completion_tokens,
                in_step_total_tokens=total_tokens,
                total_prompt_tokens=self._cumulative_prompt_tokens,
                total_completion_tokens=self._cumulative_completion_tokens,
                total_tokens=self._cumulative_total_tokens,
            )
        )

    def log(self) -> List[TokenUsage]:
        """
        Get the token usage log.

        Returns
        -------
        List[TokenUsage]
            A log of token usage details per step in the conversation.
        """
        return self._log

    def format_log(self) -> str:
        """
        Format the token usage log as a CSV string.

        Returns
        -------
        str
            The token usage log formatted as a CSV string.
        """
        result = "step_name,prompt_tokens_in_step,completion_tokens_in_step,total_tokens_in_step,total_prompt_tokens,total_completion_tokens,total_tokens\n"
        for log in self._log:
            result += f"{log.step_name},{log.in_step_prompt_tokens},{log.in_step_completion_tokens},{log.in_step_total_tokens},{log.total_prompt_tokens},{log.total_completion_tokens},{log.total_tokens}\n"
        return result

    def is_openai_model(self) -> bool:
        """
        Check if the model is an OpenAI model.

        Returns
        -------
        bool
            True if the model is an OpenAI model, False otherwise.
        """
        return "gpt" in self.model_name.lower()

    def total_tokens(self) -> int:
        """
        Return the total number of tokens used in the conversation.

        Returns
        -------
        int
            The total number of tokens used in the conversation.
        """
        return self._cumulative_total_tokens

    def usage_cost(self) -> float | None:
        """
        Return the total cost in USD of the API usage.

        Returns
        -------
        float
            Cost in USD.
        """
        if not self.is_openai_model():
            return None

        try:
            result = 0
            for log in self.log():
                result += get_openai_token_cost_for_model(
                    self.model_name, log.total_prompt_tokens, is_completion=False
                )
                result += get_openai_token_cost_for_model(
                    self.model_name, log.total_completion_tokens, is_completion=True
                )
            return result
        except Exception as e:
            print(f"Error calculating usage cost: {e}")
            return None
