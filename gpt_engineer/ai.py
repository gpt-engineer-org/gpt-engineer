# Import necessary modules and functions
from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import Dict, List
import openai
import tiktoken

# Define logger for logging module
logger = logging.getLogger(__name__)

# A data class to encapsulate the data regarding token usage
@dataclass
class TokenUsage:
    step_name: str
    in_step_prompt_tokens: int
    in_step_completion_tokens: int
    in_step_total_tokens: int
    total_prompt_tokens: int
    total_completion_tokens: int
    total_tokens: int

# The main AI class 
class AI:
    # Initialize the AI object with model and temperature as parameters
    def __init__(self, model="gpt-4", temperature=0.1):
        self.temperature = temperature  # Control randomness in the AI's responses
        self.model = model  # Define the language model to be used

        # Initialize token usage logs
        self.cumulative_prompt_tokens = 0
        self.cumulative_completion_tokens = 0
        self.cumulative_total_tokens = 0
        self.token_usage_log = []

        # Try getting tokenizer for the given model
        try:
            self.tokenizer = tiktoken.encoding_for_model(model)
        except KeyError:  
            # If not found, log it and use a default tokenizer
            logger.debug(
                f"Tiktoken encoder for model {model} not found. Using "
                "cl100k_base encoder instead. The results may therefore be "
                "inaccurate and should only be used as estimate."
            )
            self.tokenizer = tiktoken.get_encoding("cl100k_base")

    # This function creates the initial system and user messages to start the chat
    def start(self, system, user, step_name):
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]

        # Call the next() function and return the responses
        return self.next(messages, step_name=step_name)

    # Helper function to format a system message
    def fsystem(self, msg):
        return {"role": "system", "content": msg}

    # Helper function to format a user message
    def fuser(self, msg):
        return {"role": "user", "content": msg}

    # Helper function to format an assistant message
    def fassistant(self, msg):
        return {"role": "assistant", "content": msg}

    # The function to generate the next AI response
    def next(self, messages: List[Dict[str, str]], prompt=None, *, step_name=None):
        if prompt:
            messages += [{"role": "user", "content": prompt}]

        # Log the creation of a new chat completion
        logger.debug(f"Creating a new chat completion: {messages}")
        response = openai.ChatCompletion.create(
            messages=messages,
            stream=True,
            model=self.model,
            temperature=self.temperature,
        )

        # Collect the assistant's responses
        chat = []
        for chunk in response:
            delta = chunk["choices"][0]["delta"]  # type: ignore
            msg = delta.get("content", "")
            print(msg, end="")
            chat.append(msg)
        print()

        # Add assistant's response to the message list
        messages += [{"role": "assistant", "content": "".join(chat)}]

        # Log the chat completion
        logger.debug(f"Chat completion finished: {messages}")

        # Update the token usage log
        self.update_token_usage_log(
            messages=messages, answer="".join(chat), step_name=step_name
        )

        # Return the updated list of messages
        return messages

    # The function to update token usage log
    def update_token_usage_log(self, messages, answer, step_name):
        prompt_tokens = self.num_tokens_from_messages(messages)
        completion_tokens = self.num_tokens(answer)
        total_tokens = prompt_tokens + completion_tokens

        # Update cumulative counts of tokens
        self.cumulative_prompt_tokens += prompt_tokens
        self.cumulative_completion_tokens += completion_tokens
        self.cumulative_total_tokens += total_tokens

        # Append the token usage of this step to the log
        self.token_usage_log.append(
            TokenUsage(
                step_name=step_name,
                in_step_prompt_tokens=prompt_tokens,
                in_step_completion_tokens=completion_tokens,
                in_step_total_tokens=total_tokens,
                total_prompt_tokens=self.cumulative_prompt_tokens,
                total_completion_tokens=self.cumulative_completion_tokens,
                total_tokens=self.cumulative_total_tokens,
            )
        )

    # The function to format token usage log for output
    def format_token_usage_log(self):
        # Prepare the header for CSV format
        result = "step_name,"
        result += "prompt_tokens_in_step,completion_tokens_in_step,total_tokens_in_step"
        result += ",total_prompt_tokens,total_completion_tokens,total_tokens\n"
        # Append each log in CSV format
        for log in self.token_usage_log:
            result += log.step_name + ","
            result += str(log.in_step_prompt_tokens) + ","
            result += str(log.in_step_completion_tokens) + ","
            result += str(log.in_step_total_tokens) + ","
            result += str(log.total_prompt_tokens) + ","
            result += str(log.total_completion_tokens) + ","
            result += str(log.total_tokens) + "\n"
        # Return the CSV string
        return result

    # Function to count the number of tokens in a given text
    def num_tokens(self, txt):
        return len(self.tokenizer.encode(txt))

    # Function to count the number of tokens used by a list of messages
    def num_tokens_from_messages(self, messages):
        n_tokens = 0
        for message in messages:
            n_tokens += (
                4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
            )
            for key, value in message.items():
                n_tokens += self.num_tokens(value)
                if key == "name":  # if there's a name, the role is omitted
                    n_tokens += -1  # role is always required and always 1 token
        n_tokens += 2  # every reply is primed with <im_start>assistant
        return n_tokens

# Function to fallback to a default model if the given model is not available
def fallback_model(model: str) -> str:
    try:
        # Try retrieving the model, if it exists then return it
        openai.Model.retrieve(model)
        return model
    except openai.InvalidRequestError:
        # If not available, print the warning and return the default model
        print(
            f"Model {model} not available for provided API key. Reverting "
            "to gpt-3.5-turbo. Sign up for the GPT-4 wait list here: "
            "https://openai.com/waitlist/gpt-4-api\n"
        )
        return "gpt-3.5-turbo-16k"
