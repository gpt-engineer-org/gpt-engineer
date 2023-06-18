import json
import re

from typing import List, Tuple

import openai


def openai_func_call(
    model: str, messages: List, functions: List, function_call: dict
) -> dict:
    # TODO(junlin): reuse AI class
    # ref: https://platform.openai.com/docs/api-reference/chat/create
    response = openai.ChatCompletion.create(
        model=model, messages=messages, functions=functions, function_call=function_call
    )
    message = response["choices"][0]["message"]
    func_call = message["function_call"]
    func_call_args = json.loads(func_call["arguments"])
    return func_call_args


def parse_files_by_ai(chat, model="gpt-3.5-turbo-0613"):  # -> List[Tuple[str, str]]:
    func_call_args = openai_func_call(
        model=model,
        messages=[
            {
                "role": "user",
                "content": "you are an AI file writer, "
                "please write the following file to disk: " + chat,
            },
        ],
        functions=[
            {
                "name": "write_files",
                "description": "Write the file to the disk based on "
                "the given file filename and content.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "files": {
                            "type": "array",
                            "description": "an array of file which "
                            "contains filename and content",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "filename": {
                                        "type": "string",
                                        "description": "the relative path to the file",
                                    },
                                    "content": {
                                        "type": "string",
                                        "description": "the full content of the file",
                                    },
                                },
                                "required": ["filename", "content"],
                            },
                        }
                    },
                },
            }
        ],
        function_call={"name": "write_files"},
    )

    files = func_call_args["files"]
    return list(map(lambda f: (f["filename"], f["content"]), files))


def parse_chat(chat):  # -> List[Tuple[str, str]]:
    # Get all ``` blocks and preceding filenames
    regex = r"(\S+?)\n```\S+\n(.+?)```"
    matches = re.finditer(regex, chat, re.DOTALL)

    files = []
    for match in matches:
        # Strip the filename of any non-allowed characters and convert / to \
        path = re.sub(r'[<>"|?*]', "", match.group(1))

        # Get the code
        code = match.group(2)

        # Add the file to the list
        files.append((path, code))

    # Get all the text before the first ``` block
    readme = chat.split("```")[0]
    files.append(("README.md", readme))

    # Return the files
    return files


def parse_files(chat, try_ai: bool = True) -> List[Tuple[str, str]]:
    if try_ai:
        try:
            print("Try to parse files by ai")
            # TODO: Add a switch to change the model of parse_chat_by_ai,
            #  or use the same model as the main flow."
            parsed = parse_files_by_ai(chat)
            if parsed:
                return parsed
        except Exception as e:
            print(f"parse files by ai failed `{e}` , use legacy method instead")

    return parse_chat(chat)


def to_files(chat, workspace):
    workspace["all_output.txt"] = chat

    files = parse_files(chat)
    for file_name, file_content in files:
        print("saving ", file_name)
        workspace[file_name] = file_content
