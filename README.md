# GPT Engineer

[![Discord Follow](https://dcbadge.vercel.app/api/server/8tcDQ89Ej2?style=flat)](https://discord.gg/8tcDQ89Ej2)
[![GitHub Repo stars](https://img.shields.io/github/stars/AntonOsika/gpt-engineer?style=social)](https://github.com/AntonOsika/gpt-engineer)
[![Twitter Follow](https://img.shields.io/twitter/follow/antonosika?style=social)](https://twitter.com/AntonOsika)

**Specify what you want it to build, the AI asks for clarification, and then builds it.**

GPT Engineer is made to be easy to adapt, extend, and make your agent learn how you want your code to look. It generates an entire codebase based on a prompt.

- [Demo](https://twitter.com/antonosika/status/1667641038104674306)

## Project philosophy

- Simple to get value
- Incrementally build towards a user experience of:
  1. high level prompting
  2. giving feedback to the AI that it will remember over time
- Fast handovers, back and forth, between AI and human
- Simplicity, all computation is "resumable" and persisted to the filesystem

## Setup

This project supports Python 3.8 - 3.11.

Choose either **stable** or **development**.

For **stable** release:

- `python -m pip install gpt-engineer`

For **development**:
- `git clone https://github.com/AntonOsika/gpt-engineer.git`
- `cd gpt-engineer`
- `poetry install`
- `poetry shell` to activate the virtual environment

We have experimental support for [llama-index](https://github.com/run-llama/llama_index), [rank_bm25](https://github.com/dorianbrown/rank_bm25), and [tree_sitter_languages](https://github.com/grantjenks/py-tree-sitter-languages).
- `poetry install --extras experimental`

**API Key**

Choose **one** of:
- Export env variable (you can add this to .bashrc so that you don't have to do it each time you start the terminal)
    - `export OPENAI_API_KEY=[your api key]`
- .env file:
    - Create a copy of `.env.template` named `.env`
    - Add your OPENAI_API_KEY in .env
- Custom model:
    - See [docs](https://gpt-engineer.readthedocs.io/en/latest/open_models.html), supports local model, azure, etc.

Check the [Windows README](./WINDOWS_README.md) for windows usage.

**Other ways to run:**
- Use Docker ([instructions](docker/README.md))
- Do everything in your browser:
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/AntonOsika/gpt-engineer/codespaces)

## Usage

There are two ways to work with GPT-engineer: new code mode (the default), and improve existing code mode (the `-i` option).

### Creating new code
- Create an empty folder for your project anywhere on your computer
- Create a file called `prompt` (no extension) inside your new folder and fill it with instructions
- Run `gpte <project_dir>` with a relative path to your folder
  - For example: `gpte projects/my-new-project` from the gpt-engineer directory root with your new folder in `projects/`

### Improving Existing Code
- Locate a folder with code which you want to improve anywhere on your computer
- Create a file called `prompt` (no extension) inside your new folder and fill it with instructions for how you want to improve the code
- Run `gpte <project_dir> -i` with a relative path to your folder
  - For example: `gpte projects/my-old-project` from the gpt-engineer directory root with your folder in `projects/`

By running gpt-engineer you agree to our [terms](https://github.com/AntonOsika/gpt-engineer/blob/main/TERMS_OF_USE.md).

### Note

- To run this tool, the new command `gpte` is recommended for better user experience. However, the earlier default commands `gpt-engineer` and `ge` are also supported.


## Features

You can specify the "identity" of the AI agent by editing the files in the `preprompts` folder.

Editing the `preprompts`, and evolving how you write the project prompt, is how you make the agent remember things between projects.

You can also automatically copy all `preprompts` files into your project folder using the cli parameter `--use-custom-prepompts`. This way you can have custom preprompts for all of your projects without the need to edit the main files.

Each step in `steps.py` will have its communication history with GPT4 stored in the logs folder, and can be rerun with `scripts/rerun_edited_message_logs.py`.

You can also run with open source models, like WizardCoder. See the [documentation](https://gpt-engineer.readthedocs.io/en/latest/open_models.html) for example instructions.

## Vision

The gpt-engineer community is building the **open platform for devs to tinker with and build their personal code-generation toolbox**.

If you are interested in contributing to this, we would be interested in having you.

If you want to see our broader ambitions, check out the [roadmap](https://github.com/AntonOsika/gpt-engineer/blob/main/ROADMAP.md), and join
[discord](https://discord.gg/8tcDQ89Ej2)
to get input on how you can [contribute](.github/CONTRIBUTING.md) to it.

We are currently looking for more maintainers and community organizers. Email anton.osika@gmail.com if you are interested in an official role.


## Example



https://github.com/AntonOsika/gpt-engineer/assets/4467025/40d0a9a8-82d0-4432-9376-136df0d57c99
