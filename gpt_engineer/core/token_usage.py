import tiktoken
import logging

from dataclasses import dataclass
from typing import List, Union

from langchain.callbacks.openai_info import get_openai_token_cost_for_model
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

Message = Union[AIMessage, HumanMessage, SystemMessage]

logger = logging.getLogger(__name__)

@dataclass
class TokenUsage:
    step_name: str
    in_step_prompt_tokens: int
    in_step_completion_tokens: int
    in_step_total_tokens: int
    total_prompt_tokens: int
    total_completion_tokens: int
    total_tokens: int

class Tokenizer:
    def __init__(self, model_name):
        self.model_name = model_name

        if "gpt-4" in model_name or "gpt-3.5" in model_name:
            self._tiktoken_tokenizer =  tiktoken.encoding_for_model(model_name)
        else: 
            logger.debug(
                f"No encoder implemented for model {model_name}."
                "Defaulting to tiktoken cl100k_base encoder."
                "Use results only as estimates."
            )

            self._tiktoken_tokenizer = tiktoken.get_encoding("cl100k_base")


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
    
    def num_tokens_from_messages(self, messages: List[Message]) -> int:
        """
        Get the total number of tokens used by a list of messages.

        Parameters
        ----------
        messages : List[Message]
            The list of messages to count the tokens in.

        Returns
        -------
        int
            The total number of tokens used by the messages.
        """
        """Returns the number of tokens used by a list of messages."""
        n_tokens = 0
        for message in messages:
            n_tokens += (
                4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
            )
            n_tokens += self.num_tokens(message.content)
        n_tokens += 2  # every reply is primed with <im_start>assistant
        return n_tokens
    

class TokenUsageLog:
    """
    cumulative_prompt_tokens : int
        The running count of prompt tokens used.
    cumulative_completion_tokens : int
        The running count of completion tokens used.
    cumulative_total_tokens : int
        The running total of tokens used.
    token_usage_log : List[TokenUsage]
        A log of token usage details per step in the conversation.

    """
    def __init__(self, model_name):
        self.model_name = model_name
        self._cumulative_prompt_tokens = 0
        self._cumulative_completion_tokens = 0
        self._cumulative_total_tokens = 0
        self._log = []
        self._tokenizer = Tokenizer(model_name)
        
    def update_log(
        self, messages: List[Message], answer: str, step_name: str
    ) -> None:
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
        return self._log

    def format_log(self) -> str:
        """
        Format the token usage log as a CSV string.

        Returns
        -------
        str
            The token usage log formatted as a CSV string.
        """
        result = "step_name,"
        result += "prompt_tokens_in_step,completion_tokens_in_step,total_tokens_in_step"
        result += ",total_prompt_tokens,total_completion_tokens,total_tokens\n"
        for log in self._log:
            result += log.step_name + ","
            result += str(log.in_step_prompt_tokens) + ","
            result += str(log.in_step_completion_tokens) + ","
            result += str(log.in_step_total_tokens) + ","
            result += str(log.total_prompt_tokens) + ","
            result += str(log.total_completion_tokens) + ","
            result += str(log.total_tokens) + "\n"
        return result

    def usage_cost(self) -> float:
        """
        Return the total cost in USD of the api usage.

        Returns
        -------
        float
            Cost in USD.
        """
        result = 0
        for log in self.log():
            result += get_openai_token_cost_for_model(self.model_name, log.total_prompt_tokens, is_completion=False)
            result +=  get_openai_token_cost_for_model(self.model_name, log.total_completion_tokens, is_completion=True)
        return result
