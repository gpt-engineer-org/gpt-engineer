# GPT Engineer

[![Discord Follow](https://dcbadge.vercel.app/api/server/8tcDQ89Ej2?style=flat)](https://discord.gg/8tcDQ89Ej2)
[![GitHub Repo stars](https://img.shields.io/github/stars/AntonOsika/gpt-engineer?style=social)](https://github.com/AntonOsika/gpt-engineer)
[![Twitter Follow](https://img.shields.io/twitter/follow/antonosika?style=social)](https://twitter.com/AntonOsika)


**Specify what you want it to build, the AI asks for clarification, and then builds it.**

GPT Engineer is made to be easy to adapt, extend, and make your agent learn how you want your code to look. It generates an entire codebase based on a prompt.

[Demo](https://twitter.com/antonosika/status/1667641038104674306)

## Project philosophy

- Simple to get value
- Flexible and easy to add new own "AI steps". See `steps.py`.
- Incrementally build towards a user experience of:
  1. high level prompting
  2. giving feedback to the AI that it will remember over time
- Fast handovers back and forth between AI and human
- Simplicity, all computation is "resumable" and persisted to the filesystem

## Workflow

**Step 1: Installation**
- Before you can begin using GPT-Engineer, you need to ensure that it's installed on your system. You can install it using the following command:
```
pip install gpt-engineer
```
**Step 2: Initial Code Generation**
- To start the code generation process, you provide a prompt to GPT-Engineer. This prompt outlines the task you want the generated code to accomplish. For example:
```
gpt-engineer --prompt "Generate a Python function that calculates the factorial of a number."
```
- GPT-Engineer will then generate a preliminary code snippet based on the provided prompt.

**Step 3: Inspecting and Refining the Initial Code**
- After generating the initial code, it's time to inspect and refine it according to your preferences. You might need to make adjustments to the generated code to better suit your requirements or coding style. You can do this manually by editing the generated code.

**Step 4: User Feedback**
- The feedback step is a crucial part. It involves providing feedback to GPT-Engineer on the generated code. This feedback helps the model understand your preferences and allows it to improve subsequent code generations.
```
gpt-engineer --steps feedback
```
- When prompted, you can provide feedback on the generated code. For example, you might point out specific improvements, request changes, or explain why certain parts of the code need adjustment.

**Step 5: Iterative Refinement**
- Based on the feedback you provide, GPT-Engineer learns to generate code that aligns better with your requirements. The model adapts its output to incorporate your suggestions, leading to more accurate and relevant code generations in the future.


## Usage

Choose either **stable** or **development**.

For **stable** release:

- `python -m pip install gpt-engineer`

For **development**:
- `git clone https://github.com/AntonOsika/gpt-engineer.git`
- `cd gpt-engineer`
- `python -m pip install -e .`
  - (or: `make install && source venv/bin/activate` for a venv)

**API Key**
Either just:
- `export OPENAI_API_KEY=[your api key]`

Or:
- Create a copy of `.env.template` named `.env`
- Add your OPENAI_API_KEY in .env

Check the [Windows README](./WINDOWS_README.md) for windows usage.

**Running**

- Create an empty folder. If inside the repo, you can run:
  - `cp -r projects/example/ projects/my-new-project`
- Fill in the `prompt` file in your new folder
- `gpt-engineer projects/my-new-project`
  - (Note, `gpt-engineer --help` lets you see all available options. For example `--steps use_feedback` lets you improve/fix code in a project)

By running gpt-engineer you agree to our [terms](https://github.com/AntonOsika/gpt-engineer/blob/main/TERMS_OF_USE.md).

**Results**

Check the generated files in `projects/my-new-project/workspace`

**Alternatives**

You can check [Docker instructions](docker/README.md) to use Docker, or simply
do everything in your browser:

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/AntonOsika/gpt-engineer/codespaces)

## Features

You can specify the "identity" of the AI agent by editing the files in the `preprompts` folder.

Editing the `preprompts`, and evolving how you write the project prompt, is how you make the agent remember things between projects.

Each step in `steps.py` will have its communication history with GPT4 stored in the logs folder, and can be rerun with `scripts/rerun_edited_message_logs.py`.

## Vision
The gpt-engineer community is building the **open platform for devs to tinker with and build their personal code-generation toolbox**.

If you are interested in contributing to this, we would be interested in having you.

If you want to see our broader ambitions, check out the [roadmap](https://github.com/AntonOsika/gpt-engineer/blob/main/ROADMAP.md), and join
[discord](https://discord.gg/8tcDQ89Ej2)
to get input on how you can [contribute](.github/CONTRIBUTING.md) to it.

We are currently looking for more maintainers and community organizers. Email anton.osika@gmail.com if you are interested in an official role.


## Example

https://github.com/AntonOsika/gpt-engineer/assets/4467025/6e362e45-4a94-4b0d-973d-393a31d92d9b
