import os
import re


def parse_chat(chat):  # -> List[Tuple[str, str]]:
    # Get all ``` blocks and preceding filenames
    regex = r"(\S+)\n\s*```[^\n]*\n(.+?)```"
    matches = re.finditer(regex, chat, re.DOTALL)

    files = []
    for match in matches:
        # Strip the filename of any non-allowed characters and convert / to \
        path = re.sub(r'[<>"|?*]', "", match.group(1))

        # Remove leading and trailing brackets
        path = re.sub(r"^\[(.*)\]$", r"\1", path)

        # Remove leading and trailing backticks
        path = re.sub(r"^`(.*)`$", r"\1", path)

        # Remove trailing ]
        path = re.sub(r"\]$", "", path)

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


# Get code content from a code list
def get_code_strings(input):
    filesPaths = input["file_list.txt"].split("\n")
    filesDict = {}
    for filePath in filesPaths:
        with open(filePath, "r") as file:
            fileData = file.read()
            fileName = os.path.basename(filePath).split("/")[-1]
            filesDict[fileName] = fileData
    return filesDict


# Format file for inputing to chat prompt
def format_file_to_input(fileName, fileContent):
    filestr = f"""
    {fileName}
    ```
    {fileContent}
    ```
    """
    return filestr
