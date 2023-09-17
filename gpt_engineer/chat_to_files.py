from gpt_engineer.constants import FILE_LIST_NAME


def get_code_strings(input: DB) -> dict[str, str]:
    """
    Read file_list.txt and return file names and their content.

    Parameters
    ----------
    input : dict
        A dictionary containing the file_list.txt.

    Returns
    -------
    dict[str, str]
        A dictionary mapping file names to their content.
    """
    files_paths = input[FILE_LIST_NAME].strip().split("\n")
    files_dict = {}
    for full_file_path in files_paths:
        with open(full_file_path, "r") as file:
            file_data = file.read()
        if file_data:
            file_name = os.path.relpath(full_file_path, input.path)
            files_dict[file_name] = file_data
    return files_dict
def to_files(chat: str, workspace: DB):
    """
    Parse the chat and add all extracted files to the workspace.

    Parameters
    ----------
    chat : str
        The chat to parse.
    workspace : DB
        The workspace to add the files to.
    """
    workspace["all_output.txt"] = chat  # TODO store this in memory db instead

    files = parse_chat(chat)
    for file_name, file_content in files:
        workspace[file_name] = file_content


def overwrite_files(chat, dbs):
    """
    Replace the AI files with the older local files.

    Parameters
    ----------
    chat : str
        The chat containing the AI files.
    dbs : DBs
        The database containing the workspace.
    """
    dbs.workspace["all_output.txt"] = chat  # TODO store this in memory db instead

    files = parse_chat(chat)
    for file_name, file_content in files:
        if file_name == "README.md":
            dbs.workspace[
                "LAST_MODIFICATION_README.md"
            ] = file_content  # TODO store this in memory db instead
        else:
            dbs.workspace[file_name] = file_content


def get_code_strings(input: DB) -> dict[str, str]:
    """
    Read file_list.txt and return file names and their content.

    Parameters
    ----------
    input : dict
        A dictionary containing the file_list.txt.

    Returns
    -------
    dict[str, str]
        A dictionary mapping file names to their content.
    """
    files_paths = input[FILE_LIST_NAME].strip().split("\n")
    files_dict = {}
    for full_file_path in files_paths:
        with open(full_file_path, "r") as file:
            file_data = file.read()
        if file_data:
            file_name = os.path.relpath(full_file_path, input.path)
            files_dict[file_name] = file_data
    return files_dict


def format_file_to_input(file_name: str, file_content: str) -> str:
    """
    Format a file string to use as input to the AI agent.

    Parameters
    ----------
    file_name : str
        The name of the file.
    file_content : str
        The content of the file.

    Returns
    -------
    str
        The formatted file string.
    """
    file_str = f"""
    {file_name}
    ```
    {file_content}
    ```
    """
    return file_str
