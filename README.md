# GPT Engineer
Specify what you want it to build, the AI asks for clarification, and then builds it.

Even if it is complex.

## Philosophy
The philosophy of this project is that it should be be
- Simple to get value
- Flexible and simple to add new own "AI steps" (see `steps.py`)
- Incrementally build towards a user experience of:
  - high level prompting
  - giving feedback to the AI that it will remember over time
- Fast handovers back and forth between AI and human
- No databases, all computation is "resumable" and persisted to filesystems


## Usage

**Install**:

- `pip install -r requirements.txt`

**Run**:
- Create a new empty folder with a `main_prompt` file (or copy the example folder `cp example -r my-new-project`)
- Fill in the `main_prompt` in your new folder
- run `python main.py my-new-project`

**Results**:
- Check the generated files in my-new-project/workspace_clarified

## Features
Allows you to specify the "identity" of the AI agent by editing the files in the `identity` folder.

This, and reusing snippets in the main_prompt, is currently how you make the agent remember things between sessions.

Each step in steps.py will 