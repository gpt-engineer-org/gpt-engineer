# GPT Engineer
**Specify what you want it to build, the AI asks for clarification, and then builds it.**

GPT Engineer is made to be easy to adapt, extend, and make your agent learn how you want your code to look. It generates an entire codebase based on a prompt.

[Demo](https://twitter.com/antonosika/status/1667641038104674306) 👶🤖

## Project philosophy
- Simple to get value
- Flexible and easy to add new own "AI steps". See `steps.py`.
- Incrementally build towards a user experience of:
  1. high level prompting
  2. giving feedback to the AI that it will remember over time
- Fast handovers back and forth between AI and human
- Simplicity, all computation is "resumable" and persisted to the filesystem


## Installation

**Users**:

We recommend installing from PyPi:
```bash
pip install gpt-engineer
```
This will make sure you are running the latest stable version.


**Contributors/Developers**:

If you plan on becoming a [contributor](.github/CONTRIBUTING.md) or if you just want to test/develop something on top of things,
you can install from GitHub the bleeding version, aka the `main` branch:

_(be aware this is a very active project and might be unstable at times)_

```bash
# use make (run make --help to see all commands available)
make install

# or

make dev-install  # if you plan to contribute
```

If you know your way around Python project you can also install manually (make sure you are in a virtual environment):
```
pip install -r requirements.txt
```


## Usage

**Setup**:

- setup your OpenAI API Key (with a key that has GPT4 access)
```
export OPENAI_API_KEY=[your api key]
```

**Run**:
- Create a new empty folder with a `main_prompt` file in the `projects` folder or copy the example folder:
```
cp -r projects/example/ projects/my-new-project
```

- Fill in the `main_prompt` in your new folder

- Run `make run my-new-project` or `python -m gpt_engineer.main my-new-project`
  - Optionally pass in `true` to delete the working files before running

**Results**:
- Check the generated files in `projects/my-new-project/workspace`

### Limitations
Implementing additional chain of thought prompting, e.g. [Reflexion](https://github.com/noahshinn024/reflexion), should be able to make it more reliable and not miss requested functionality in the main prompt.

Contributors welcome! If you are unsure what to add, check out the ideas listed in the Projects tab in the GitHub repo.


## Features
You can specify the "identity" of the AI agent by editing the files in the `identity` folder.

Editing the identity, and evolving the `main_prompt`, is currently how you make the agent remember things between projects.

Each step in `steps.py` will have its communication history with GPT4 stored in the logs folder, and can be rerun with `scripts/rerun_edited_message_logs.py`.

## Contributing
If you want to contribute, please check out the [projects](https://github.com/AntonOsika/gpt-engineer/projects?query=is%3Aopen) or [issues tab](https://github.com/AntonOsika/gpt-engineer/issues) in the GitHub repo and please read the [contributing document](.github/CONTRIBUTING.md) on how to contribute.


## High resolution example

https://github.com/AntonOsika/gpt-engineer/assets/4467025/6e362e45-4a94-4b0d-973d-393a31d92d9b
