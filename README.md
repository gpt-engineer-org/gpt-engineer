# gpt-engineer

[![GitHub Repo stars](https://img.shields.io/github/stars/gpt-engineer-org/gpt-engineer?style=social)](https://github.com/gpt-engineer-org/gpt-engineer)
[![Discord Follow](https://dcbadge.vercel.app/api/server/8tcDQ89Ej2?style=flat)](https://discord.gg/8tcDQ89Ej2)
[![License](https://img.shields.io/github/license/gpt-engineer-org/gpt-engineer)](https://github.com/gpt-engineer-org/gpt-engineer/blob/main/LICENSE)
[![GitHub Issues or Pull Requests](https://img.shields.io/github/issues/gpt-engineer-org/gpt-engineer)](https://github.com/gpt-engineer-org/gpt-engineer/issues)
![GitHub Release](https://img.shields.io/github/v/release/gpt-engineer-org/gpt-engineer)
[![Twitter Follow](https://img.shields.io/twitter/follow/antonosika?style=social)](https://twitter.com/antonosika)

The OG code genereation experimentation platform!

If you are looking for the evolution that is an opinionated, managed service – check out gptengineer.app.

If you are looking for a well maintained hackable CLI for – check out aider.
 # gpt-engineer

GitHub Repo stars · Discord Follow · License · GitHub Issues or Pull Requests · GitHub Release · Twitter Follow

The OG code generation experimentation platform!

If you are looking for the evolution that is an opinionated, managed service – check out gptengineer.app.

If you are looking for a well maintained hackable CLI – check out aider.


gpt-engineer lets you:

- Specify software in natural language
- Sit back and watch as an AI writes and executes the code
- Ask the AI to implement improvements


## Getting Started

### Install gpt-engineer

For stable release:

```bash
python -m pip install gpt-engineer
```

For development:

```bash
git clone https://github.com/gpt-engineer-org/gpt-engineer.git
cd gpt-engineer
poetry install
poetry shell  # activate the virtual environment
```

We actively support Python 3.10 - 3.12. The last version to support Python 3.8 - 3.9 was 0.2.6.

### Setup API key

Choose one of:

- Export an environment variable (add it to your shell profile so you don't need to set it every time):

```bash
export OPENAI_API_KEY=[your api key]
```

- Use a `.env` file:
  - Create a copy of `.env.template` named `.env`
  - Add your `OPENAI_API_KEY` in `.env`

- Custom model: See the docs for instructions (supports local models, Azure, etc.).

Check the `WINDOWS_README.md` file for Windows-specific instructions.

Other ways to run:

- Use Docker (see `docker/README.md`)
- Open in GitHub Codespaces


## Usage

### Create new code (default usage)

1. Create an empty folder for your project.
2. Inside that folder create a file named `prompt` (no extension) and fill it with your instructions.
3. From the gpt-engineer repo root run:

```bash
gpte <project_dir>
# example: gpte projects/my-new-project
```


### Improve existing code

1. Locate the folder containing the code you want to improve.
2. Create a `prompt` file inside it with instructions for the improvement.
3. Run:

```bash
gpte <project_dir> -i
# example: gpte projects/my-old-project -i
```


### Benchmarking

The `gpt-engineer` package installs a `bench` binary for benchmarking agent implementations. See the `gpte-bench-template` repo for a starter template.

Supported datasets include APPS and MBPP.


### Research

See the `docs` and community resources for research notes and briefs.


## Notes

- Limiting context window: see `docs/context_window.md` for strategies to control token usage and avoid truncation.
- By running gpt-engineer you agree to the terms in `TERMS_OF_USE.md`.


## Links & Community

- Roadmap: `ROADMAP.md`
- Governance: `GOVERNANCE.md`
- Contributing: `.github/CONTRIBUTING.md`
- Discord: https://discord.gg/8tcDQ89Ej2


---

_This README was updated locally._

The gptengineer.app team is actively supporting the open source community.


## Features

### Pre Prompts
You can specify the "identity" of the AI agent by overriding the `preprompts` folder with your own version of the `preprompts`. You can do so via the `--use-custom-preprompts` argument.

Editing the `preprompts` is how you make the agent remember things between projects.

### Vision

By default, gpt-engineer expects text input via a `prompt` file. It can also accept image inputs for vision-capable models. This can be useful for adding UX or architecture diagrams as additional context for GPT Engineer. You can do this by specifying an image directory with the `—-image_directory` flag and setting a vision-capable model in the second CLI argument.

E.g. `gpte projects/example-vision gpt-4-vision-preview --prompt_file prompt/text --image_directory prompt/images -i`

### Open source, local and alternative models

By default, gpt-engineer supports OpenAI Models via the OpenAI API or Azure OpenAI API, as well as Anthropic models.

With a little extra setup, you can also run with open source models like WizardCoder. See the [documentation](https://gpt-engineer.readthedocs.io/en/latest/open_models.html) for example instructions.

## Mission

The gpt-engineer community mission is to **maintain tools that coding agent builders can use and facilitate collaboration in the open source community**.

If you are interested in contributing to this, we are interested in having you.

If you want to see our broader ambitions, check out the [roadmap](https://github.com/gpt-engineer-org/gpt-engineer/blob/main/ROADMAP.md), and join
[discord](https://discord.gg/8tcDQ89Ej2)
to learn how you can [contribute](.github/CONTRIBUTING.md) to it.

gpt-engineer is [governed](https://github.com/gpt-engineer-org/gpt-engineer/blob/main/GOVERNANCE.md) by a board of long-term contributors. If you contribute routinely and have an interest in shaping the future of gpt-engineer, you will be considered for the board.

## Significant contributors
<ul style="list-style-type: none; padding: 0; display: flex; flex-wrap: wrap;"> <li style="margin-right: 10px; margin-bottom: 10px;"> <a href="https://github.com/ATheorell"> <img src="https://avatars.githubusercontent.com/u/143704446?s=64&v=4" alt="@ATheorell" width="32" height="32" style="border-radius: 50%;"> @ATheorell </a> </li> <li style="margin-right: 10px; margin-bottom: 10px;"> <a href="https://github.com/similato87"> <img src="https://avatars.githubusercontent.com/u/71301573?s=64&v=4" alt="@similato87" width="32" height="32" style="border-radius: 50%;"> @similato87 </a> </li> <li style="margin-right: 10px; margin-bottom: 10px;"> <a href="https://github.com/TheoMcCabe"> <img src="https://avatars.githubusercontent.com/u/9841960?s=64&v=4" alt="@TheoMcCabe" width="32" height="32" style="border-radius: 50%;"> @TheoMcCabe </a> </li> <li style="margin-right: 10px; margin-bottom: 10px;"> <a href="https://github.com/captivus"> <img src="https://avatars.githubusercontent.com/u/366332?s=64&v=4" alt="@captivus" width="32" height="32" style="border-radius: 50%;"> @captivus </a> </li> </ul>


## Example



https://github.com/gpt-engineer-org/gpt-engineer/assets/4467025/40d0a9a8-82d0-4432-9376-136df0d57c99
