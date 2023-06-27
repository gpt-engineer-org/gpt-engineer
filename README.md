# GPT Engineer

[![Discord Follow](https://dcbadge.vercel.app/api/server/8tcDQ89Ej2?style=flat)](https://discord.gg/8tcDQ89Ej2)
[![GitHub Repo stars](https://img.shields.io/github/stars/AntonOsika/gpt-engineer?style=social)](https://github.com/AntonOsika/gpt-engineer)
[![Twitter Follow](https://img.shields.io/twitter/follow/antonosika?style=social)](https://twitter.com/AntonOsika)

GPT Engineer is an AI-powered tool designed to simplify code generation and help you build your codebase based on a prompt.

[Demo](https://twitter.com/antonosika/status/1667641038104674306)

## Project Philosophy

- Easy to use and get value from
- Flexible and extensible, allowing you to customize and teach the AI how you want your code to look
- Iterative improvement towards a user experience that includes high-level prompting and the ability to provide feedback to the AI for better learning
- Smooth collaboration between AI and human developers
- Simplicity with all computation being resumable and persisted to the filesystem

## Usage

Choose between the **stable** or **development** release.

For the **stable** release:

- `pip install gpt-engineer`

For the **development** release:
- `git clone https://github.com/AntonOsika/gpt-engineer.git`
- `cd gpt-engineer`
- `pip install -e .`
  - (Alternatively, use `make install && source venv/bin/activate` for a virtual environment)

**Setup**

Before running GPT Engineer, ensure you have an API key with GPT4 access:

- `export OPENAI_API_KEY=[your api key]`

**Running GPT Engineer**:

- Create an empty folder. If you're inside the repository, you can run:
  - `cp -r projects/example/ projects/my-new-project`
- Fill in the `prompt` file in your new folder
- Run `gpt-engineer projects/my-new-project`
  - (Note: Use `gpt-engineer --help` to see all available options. For example, `--steps use_feedback` allows you to improve or fix code in a project)

By running GPT Engineer, you agree to our [Terms of Service](https://github.com/AntonOsika/gpt-engineer/blob/main/TERMS_OF_USE.md).

**Results**
- Check the generated files in `projects/my-new-project/workspace`

## Features

You can specify the "identity" of the AI agent by editing the files in the `preprompts` folder.

Editing the `preprompts` and evolving how you write the project prompt is currently the way to make the agent remember things between projects.

Each step in `steps.py` will have its communication history with GPT4 stored in the logs folder and can be rerun with `scripts/rerun_edited_message_logs.py`.

## Contributing
The GPT Engineer community is building an open platform for developers to experiment and build their personal code-generation toolbox.

If you're interested in contributing, we would love to have you on board!

You can find good first issues [here](https://github.com/AntonOsika/gpt-engineer/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22).
Check out the contributing guidelines [here](.github/CONTRIBUTING.md).

We are currently looking for more maintainers and community organizers. If you're interested in an official role, please email anton.osika@gmail.com.

To learn more about our broader ambitions, take a look at the [roadmap](https://github.com/AntonOsika/gpt-engineer/blob/main/ROADMAP.md), and join our [Discord](https://discord.gg/8tcDQ89Ej2) community to get involved and contribute.

## Example

https://github.com/AntonOsika/gpt-engineer/assets/4467025/6e362e45-4a94-4b0d-973d-393a31d92d9b

