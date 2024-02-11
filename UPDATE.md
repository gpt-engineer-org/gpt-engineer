# Update - Interactive CLI Mode

## New Features

- **Interactive Mode**: Users can now enter an interactive mode by using the `--interactive` flag. This mode allows users to chat with the codebase for live adjustments without the need to create a prompt file.

- **Direct Prompt Input**: The CLI has been updated to allow users to input the prompt directly in the terminal when creating a new codebase or improving an existing one. This eliminates the need for a prompt file in the project directory.

- **Improved User Experience**: The CLI now prompts users to choose between creating a new codebase or improving an existing one. It then asks for the directory path and the prompt accordingly, streamlining the process.

## Usage

To start the interactive mode, use the following command:

```bash
gpt-engineer --interactive
```

To create a new codebase or improve an existing one with direct prompt input, use the following commands:

```bash
gpt-engineer --create-new
# or
gpt-engineer --improve-existing
```

The user will be prompted to enter the directory path for the codebase and the prompt for the code generation or improvement.

These updates aim to enhance the flexibility and usability of the GPT-Engineer CLI tool, making it more intuitive and efficient for developers.