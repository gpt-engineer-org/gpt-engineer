import os
import re


def parse_chat(chat):  # -> List[Tuple[str, str]]:
    # Get all ``` blocks and preceding filenames
    regex = r"(\S+)\n\s*```[^\n]*\n(.+?)```"
    matches = re.finditer(regex, chat, re.DOTALL)

    files = []
    for match in matches:
        # Strip the filename of any non-allowed characters and convert / to \
        path = re.sub(r'[\:<>"|?*]', "", match.group(1))

        # Remove leading and trailing brackets
        path = re.sub(r"^\[(.*)\]$", r"\1", path)

        # Remove leading and trailing backticks
        path = re.sub(r"^`(.*)`$", r"\1", path)

        # Remove trailing ]
        path = re.sub(r"[\]\:]$", "", path)

        # Get the code
        code = match.group(2)

        # Add the file to the list
        files.append((path, code))

    # Get all the text before the first ``` block
    readme = chat.split("```")[0]
    files.append(("README.md", readme))

    # Return the files
    return files


def to_files(chat, workspace):
    workspace["all_output.txt"] = chat

    files = parse_chat(chat)
    for file_name, file_content in files:
        workspace[file_name] = file_content


def overwrite_files(chat, dbs, replace_files):
    """
    Replace the AI files to the older local files.
    """
    dbs.workspace["all_output.txt"] = chat

    files = parse_chat(chat)
    for file_name, file_content in files:
        dbs.workspace[file_name] = file_content


def get_code_strings(input) -> dict[str, str]:
    """
    Read file_list.txt and return file names and its content.
    """
    files_paths = input["file_list.txt"].strip().split("\n")
    files_dict = {}
    for file_path in files_paths:
        with open(file_path, "r") as file:
            file_data = file.read()
        if file_data:
            file_name = os.path.basename(file_path).split("/")[-1]
            files_dict[file_name] = file_data
    return files_dict


def format_file_to_input(file_name: str, file_content: str) -> str:
    """
    Format a file string to use as input to AI agent
    """
    file_str = f"""
    {file_name}
    ```
    {file_content}
    ```
    """
    return file_str
