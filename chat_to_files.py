import re

def parse_chat(chat):# -> List[Tuple[str, str]]:
    # Get all `<``>` blocks
    #using custom syntax so that common markdown syntax can be used in the code blocks
    regex = r"<#-(.*?)-#>"
    
    matches = re.finditer(regex, chat, re.DOTALL)

    files = []
    for match in matches:
        path = match.group(1).split("\n")[0]
        # Get the code
        code = match.group(1).split("\n")[1:]
        code = "\n".join(code)
        #remove the first and last line if they have ```
        if code.startswith("```"):
            code = "\n".join(code.split("\n")[1:])
        if code.endswith("```"):
            code = "\n".join(code.split("\n")[:-1])

        # Add the file to the list
        files.append((path, code))
    
    return files


def to_files(chat, workspace):
    workspace['all_output.txt'] = chat

    files = parse_chat(chat)
    for file_name, file_content in files:
        workspace[file_name] = file_content