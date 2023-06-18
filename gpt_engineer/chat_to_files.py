import re


def parse_chat(chat):  # -> List[Tuple[str, str]]:
    # Split the chat into sections by the "*CODEBLOCKSBELOW*" token
    split_chat = chat.split("*CODEBLOCKSBELOW*")

    # Check if the "*CODEBLOCKSBELOW*" token was found
    is_token_found = len(split_chat) > 1

    # If the "*CODEBLOCKSBELOW*" token is found, use the first part as README
    # and second part as code blocks. Otherwise, treat README as optional and
    # proceed with empty README and the entire chat as code blocks
    readme = split_chat[0].strip() if is_token_found else "No readme"
    code_blocks = split_chat[1] if is_token_found else chat

    # Get all ``` blocks and preceding filenames
    regex = r"(\S+?)\n```\S+\n(.+?)```"
    matches = re.finditer(regex, code_blocks, re.DOTALL)

    files = []
    for match in matches:
        # Strip the filename of any non-allowed characters and convert / to \
        path = re.sub(r'[<>"|?*]', "", match.group(1))

        # Get the code
        code = match.group(2)

        # Add the file to the list
        files.append((path, code))

    # Add README to the list
    files.append(("README.txt", readme))

    # Return the files
    return files


def to_files(chat, workspace):
    workspace["all_output.txt"] = chat

    files = parse_chat(chat)
    for file_name, file_content in files:
        workspace[file_name] = file_content
