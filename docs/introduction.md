# Introduction
``gpt-engineer`` is a project that uses LLMs (such as GPT-4) to automate the process of software engineering. It includes several Python scripts that interact with the LLM to generate code, clarify requirements, generate specifications, and more.

<br>

### Get started
[Here’s](/installation.html) how to install ``gpt-engineer``, set up your environment, and start building.

We recommend following our [Quickstart](/quickstart.html) guide to familiarize yourself with the framework by building your first application with ``gpt-engineer``.

## Core Components

(ai_class)=
### 1. AI Class (`gpt_engineer/core/ai.py`)
The `AI` class is the main interface to the LLM. It provides methods to start a conversation with the model, continue an existing conversation, and format system and user messages.

<br>

(agent_class)=
### 2. Agent Class (`gpt_engineer/applications/cli/cli_agent.py`)
The `Agent` class is responsible for managing the lifecycle of code generation and improvement. Its main functions are:

- `init(self, prompt)`: Generates a new piece of code using the AI based on the provided prompt. It also generates a entrypoint file based on the generated code.

- `improve(self, files_dict, prompt)`: Improves an existing piece of code using the AI class based on the provided prompt and files dictionary.

<br>

(files_dictionary_class)=
### 3. Files Dictionary Class (`gpt_engineer/core/files_dict.py`)
The `Files Dictionary` class extends the standard dictionary to enforce string keys and values, representing filenames and their corresponding code content. It provides a method to format its contents for chat-based interaction with the `AI` class.

<br>

### 4. Chat to Files (`gpt_engineer/core/chat_to_files.py`)
This module provides utilities to handle and process chat content, including parsing chat messages to retrieve code blocks, storing these blocks in the [`Files Dictionary`](files_dictionary_class), and overwriting the files based on new chat messages. The module contains four main functions:

- `chat_to_files_dict(chat)`: This function takes a chat conversation and extracts all the code blocks and preceding filenames. It returns an instance of [`Files Dictionary`](files_dictionary_class) representing filenames and their corresponding code content.

- `parse_edits(chat)`: This function parses edits from a chat and returns them as a list of `Edit` class objects.

- `apply_edits(edits, files_dict)`: This function takes a list of Edit objects and applies each edit to the code object. It handles the creation of new files and the modification of existing files when required.

- `overwrite_code_with_edits(chat, files_dict)`: This function takes a chat string, and employs the `parse_edits` function to parse it for edits, before applying the edits to the relevant code object via the `apply_edits` function.

<br>

(steps)=
### 5. Steps (`gpt_engineer/core/default/steps.py`)
This module defines a series of steps that can be run by the agent.
The main steps are:

- `gen_code(ai, prompt, memory, preprompts_holder)`: Generate new code based on the specification.

- `gen_entrypoint(ai, files_dict, memory, preprompts_holder)`: Generate an entrypoint file code based on the generated code.

- `execute_entrypoint(ai, execution_env, files_dict, preprompts_holder)`: Uses the entrypoint file to run the generated code inside the execution environment.

- `improve(ai, prompt, files_dict, memory, preprompts_holder)`: Improves an existing codebase based on the provided specifications.

<br>

### 6. Main Script (`gpt_engineer/applications/cli/main.py`)
The main script is the is the entry point of the application and uses the `Typer` library to create a command-line interface. It sets up instances of an [`AI`](ai_class), a [`Files Dictionary`](files_dictionary_class), a `BaseMemory`, a `BaseExecutionEnv` and an [`Agent`](agent_class) that runs a series of [steps](steps) based on the provided configuration.

<br>

## Example
You can find an example of the project in action [here](https://github.com/gpt-engineer-org/gpt-engineer/assets/4467025/6e362e45-4a94-4b0d-973d-393a31d92d9b).

<video width="100%" controls>
  <source src="https://github.com/gpt-engineer-org/gpt-engineer/assets/4467025/6e362e45-4a94-4b0d-973d-393a31d92d9b
" type="video/mp4">
  Your browser does not support the video tag.
</video>
