# GPT Engineer

## Fork Information
This fork serves to replace OpenAI's ChatGPT with GPT4All to allow for offline use with open source model that can generate commercial content (Though make sure the model you choose allows this. Licensing is a tricky thing and it's completely up to you how you deal with it)

So far I still see the best results using OpenAI's ChatGPT-4, however it is imperative that we move away from commercial closed source models as quickly as possible to keep the playing field even. That is the motivation behind this fork

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


## Usage

**Setup**:
- `pip install -r requirements.txt`

**Run**:
- Create a new empty folder with a `main_prompt` file (or copy the example folder `cp -r example/ my-new-project`)
- Fill in the `main_prompt` in your new folder
- Run `python -m gpt_engineer.main my-new-project`

**Results**:
- Check the generated files in my-new-project/workspace

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
