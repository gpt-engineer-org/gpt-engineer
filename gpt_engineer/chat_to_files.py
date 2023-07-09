import os
import re
import tkinter as tk
import tkinter.filedialog as fd


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


def overwrite_files(chat, dbs, replace_files):
    """
    Replace the AI files to the older local files.
    """
    dbs.workspace["all_output.txt"] = chat

    files = parse_chat(chat)
    for file_name, file_content in files:
        # Verify if the file created by the AI agent was in the input list
        if file_name in replace_files:
            # If the AI created a file from our input list, we replace it.
            with open(replace_files[file_name], "w") as text_file:
                text_file.write(file_content)
        else:
            # If the AI create a new file I don't know where to put it yet
            # maybe we can think in a smarter solution for this in the future
            # like asking the AI where to put it.
            #
            # by now, just add this to the workspace inside .gpteng folder
            print(
                f"Could not find file path for '{file_name}', creating file in workspace"
            )
            dbs.workspace[file_name] = file_content


def get_code_strings(input) -> dict[str, str]:
    """
    Read file_list.txt and return file names and its content.
    """
    filesPaths = input["file_list.txt"].strip().split("\n")
    filesDict = {}
    for filePath in filesPaths:
        fileData = ""
        with open(filePath, "r") as file:
            fileData = file.read()
        if fileData:
            fileName = os.path.basename(filePath).split("/")[-1]
            filesDict[fileName] = fileData
    return filesDict


def format_file_to_input(fileName: str, fileContent: str) -> str:
    """
    Format a file string to use as input to AI agent
    """
    filestr = f"""
    {fileName}
    ```
    {fileContent}
    ```
    """
    return filestr


def ask_for_files(input) -> dict[str, str]:
    """
    Display a tkinter file selection window to select context files.
    Return a dictionary of file_name as key and file_path as value
    """
    root = tk.Tk()
    root.withdraw()
    root.call("wm", "attributes", ".", "-topmost", True)
    file_list = list(
        fd.askopenfilenames(
            parent=root,
            initialdir=os.getcwd(),
            title="Select relevant files for your change:",
        )
    )
    file_list_string = ""
    file_path_info = {}
    for file_path in file_list:
        file_list_string += file_path + "\n"
        # Return a dict with key=file_name and value=file_path
        file_path_info[os.path.basename(file_path).split("/")[-1]] = file_path
    # Write in file_list so the user can edit and remember what was done
    input["file_list.txt"] = file_list_string
    return file_path_info
