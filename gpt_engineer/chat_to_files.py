import os
import re

from typing import List, Tuple

from gpt_engineer.db import DB
from gpt_engineer.file_selector import FILE_LIST_NAME


def parse_chat(chat) -> List[Tuple[str, str]]:
    """
    Extracts all code blocks from a chat and returns them
    as a list of (filename, codeblock) tuples.

    Parameters
    ----------
    chat : str
        The chat to extract code blocks from.

    Returns
    -------
    List[Tuple[str, str]]
        A list of tuples, where each tuple contains a filename and a code block.
    """
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


def overwrite_files_with_edits(chat, dbs):
    edits = parse_edits(chat)

    # # # # DEBUG
    print('\nEDITS:\n\n')
    for e in edits:
        print('filename:', e[0])
        print('original:',e[1])
        print('edit:',e[2])
        print('----\n')
    # # # # 

    apply_edits(edits, dbs)


def parse_edits(llm_response):
    # strongly based on https://github.com/paul-gauthier/aider/blob/main/aider/coders/editblock_coder.py
    # shout out to Paul Gauthier!

    HEAD = "<<<<<<< HEAD"
    DIVIDER = "======="
    UPDATED = ">>>>>>> updated"

    separators = "|".join([HEAD, DIVIDER, UPDATED])

    split_re = re.compile(r"^((?:" + separators + r")[ ]*\n)", re.MULTILINE | re.DOTALL)

    def find_original_update_blocks(content):
        # make sure we end with a newline, otherwise the regex will miss <<UPD on the last line
        if not content.endswith("\n"):
            content = content + "\n"

        pieces = re.split(split_re, content)

        pieces.reverse()
        processed = []

        # Keep using the same filename in cases where GPT produces an edit block
        # without a filename.
        current_filename = None
        try:
            while pieces:
                cur = pieces.pop()

                if cur in (DIVIDER, UPDATED):
                    processed.append(cur)
                    raise ValueError(f"Unexpected {cur}")

                if cur.strip() != HEAD:
                    processed.append(cur)
                    continue

                processed.append(cur)  # original_marker

                filename = processed[-2].splitlines()[-1].strip()
                try:
                    if not len(filename) or "`" in filename:
                        filename = processed[-2].splitlines()[-2].strip()
                    if not len(filename) or "`" in filename:
                        if current_filename:
                            filename = current_filename
                        else:
                            raise ValueError(
                                f"Bad/missing filename. It should go right above the {HEAD}"
                            )
                except IndexError:
                    if current_filename:
                        filename = current_filename
                    else:
                        raise ValueError(f"Bad/missing filename. It should go right above the {HEAD}")

                current_filename = filename

                original_text = pieces.pop()
                processed.append(original_text)

                divider_marker = pieces.pop()
                processed.append(divider_marker)
                if divider_marker.strip() != DIVIDER:
                    raise ValueError(f"Expected `{DIVIDER}` not {divider_marker.strip()}")

                updated_text = pieces.pop()
                processed.append(updated_text)

                updated_marker = pieces.pop()
                processed.append(updated_marker)
                if updated_marker.strip() != UPDATED:
                    raise ValueError(f"Expected `{UPDATED}` not `{updated_marker.strip()}")

                yield filename, original_text, updated_text
        except ValueError as e:
            processed = "".join(processed)
            err = e.args[0]
            raise ValueError(f"{processed}\n^^^ {err}")
        except IndexError:
            processed = "".join(processed)
            raise ValueError(f"{processed}\n^^^ Incomplete HEAD/updated block.")
        except Exception:
            processed = "".join(processed)
            raise ValueError(f"{processed}\n^^^ Error parsing HEAD/updated block.")


    # might raise ValueError for malformed ORIG/UPD blocks # todo <- understand comment + resolve
    return list(find_original_update_blocks(llm_response))

def apply_edits(edits, dbs):

    print('NOTE UMER: applying edits isnt implemented yet')
    pass

    def prep(content):
        if content and not content.endswith("\n"):
            content += "\n"
        lines = content.splitlines(keepends=True)
        return content, lines


    def perfect_or_whitespace(whole_lines, part_lines, replace_lines):
        # Try for a perfect match
        res = perfect_replace(whole_lines, part_lines, replace_lines)
        if res:
            return res

        # Try being flexible about leading whitespace
        res = replace_part_with_missing_leading_whitespace(whole_lines, part_lines, replace_lines)
        if res:
            return res


    def perfect_replace(whole_lines, part_lines, replace_lines):
        part_tup = tuple(part_lines)
        part_len = len(part_lines)

        for i in range(len(whole_lines) - part_len + 1):
            whole_tup = tuple(whole_lines[i : i + part_len])
            if part_tup == whole_tup:
                res = whole_lines[:i] + replace_lines + whole_lines[i + part_len :]
                return "".join(res)


    def replace_most_similar_chunk(whole, part, replace):
        """Best efforts to find the `part` lines in `whole` and replace them with `replace`"""

        whole, whole_lines = prep(whole)
        part, part_lines = prep(part)
        replace, replace_lines = prep(replace)

        res = perfect_or_whitespace(whole_lines, part_lines, replace_lines)
        if res:
            return res

        # drop leading empty line, GPT sometimes adds them spuriously (issue #25)
        if len(part_lines) > 2 and not part_lines[0].strip():
            skip_blank_line_part_lines = part_lines[1:]
            res = perfect_or_whitespace(whole_lines, skip_blank_line_part_lines, replace_lines)
            if res:
                return res

        # Try to handle when it elides code with ...
        try:
            res = try_dotdotdots(whole, part, replace)
            if res:
                return res
        except ValueError:
            pass

        return


    def try_dotdotdots(whole, part, replace):
        """
        See if the edit block has ... lines.
        If not, return none.

        If yes, try and do a perfect edit with the ... chunks.
        If there's a mismatch or otherwise imperfect edit, raise ValueError.

        If perfect edit succeeds, return the updated whole.
        """

        dots_re = re.compile(r"(^\s*\.\.\.\n)", re.MULTILINE | re.DOTALL)

        part_pieces = re.split(dots_re, part)
        replace_pieces = re.split(dots_re, replace)

        if len(part_pieces) != len(replace_pieces):
            raise ValueError("Unpaired ... in edit block")

        if len(part_pieces) == 1:
            # no dots in this edit block, just return None
            return

        # Compare odd strings in part_pieces and replace_pieces
        all_dots_match = all(part_pieces[i] == replace_pieces[i] for i in range(1, len(part_pieces), 2))

        if not all_dots_match:
            raise ValueError("Unmatched ... in edit block")

        part_pieces = [part_pieces[i] for i in range(0, len(part_pieces), 2)]
        replace_pieces = [replace_pieces[i] for i in range(0, len(replace_pieces), 2)]

        pairs = zip(part_pieces, replace_pieces)
        for part, replace in pairs:
            if not part and not replace:
                continue

            if not part and replace:
                if not whole.endswith("\n"):
                    whole += "\n"
                whole += replace
                continue

            if whole.count(part) != 1:
                raise ValueError(
                    "No perfect matching chunk in edit block with ... or part appears more than once"
                )

            whole = whole.replace(part, replace, 1)

        return whole


    def replace_part_with_missing_leading_whitespace(whole_lines, part_lines, replace_lines):
        # GPT often messes up leading whitespace.
        # It usually does it uniformly across the ORIG and UPD blocks.
        # Either omitting all leading whitespace, or including only some of it.

        # Outdent everything in part_lines and replace_lines by the max fixed amount possible
        leading = [len(p) - len(p.lstrip()) for p in part_lines if p.strip()] + [
            len(p) - len(p.lstrip()) for p in replace_lines if p.strip()
        ]

        if leading and min(leading):
            num_leading = min(leading)
            part_lines = [p[num_leading:] if p.strip() else p for p in part_lines]
            replace_lines = [p[num_leading:] if p.strip() else p for p in replace_lines]

        # can we find an exact match not including the leading whitespace
        num_part_lines = len(part_lines)

        for i in range(len(whole_lines) - num_part_lines + 1):
            add_leading = match_but_for_leading_whitespace(
                whole_lines[i : i + num_part_lines], part_lines
            )

            if add_leading is None:
                continue

            replace_lines = [add_leading + rline if rline.strip() else rline for rline in replace_lines]
            whole_lines = whole_lines[:i] + replace_lines + whole_lines[i + num_part_lines :]
            return "".join(whole_lines)

        return None


    def match_but_for_leading_whitespace(whole_lines, part_lines):
        num = len(whole_lines)

        # does the non-whitespace all agree?
        if not all(whole_lines[i].lstrip() == part_lines[i].lstrip() for i in range(num)):
            return

        # are they all offset the same?
        add = set(
            whole_lines[i][: len(whole_lines[i]) - len(part_lines[i])]
            for i in range(num)
            if whole_lines[i].strip()
        )

        if len(add) != 1:
            return

        return add.pop()


    def strip_quoted_wrapping(res, fname=None, fence=None):
        """
        Given an input string which may have extra "wrapping" around it, remove the wrapping.
        For example:

        filename.ext
        ```
        We just want this content
        Not the filename and triple quotes
        ```
        """
        if not res:
            return res

        if not fence:
            fence = ("```", "```")

        res = res.splitlines()

        if fname and res[0].strip().endswith(Path(fname).name):
            res = res[1:]

        if res[0].startswith(fence[0]) and res[-1].startswith(fence[1]):
            res = res[1:-1]

        res = "\n".join(res)
        if res and res[-1] != "\n":
            res += "\n"

        return res


    def do_replace(fname, content, before_text, after_text, fence=None):
        before_text = strip_quoted_wrapping(before_text, fname, fence)
        after_text = strip_quoted_wrapping(after_text, fname, fence)
        fname = Path(fname)

        # does it want to make a new file?
        if not fname.exists() and not before_text.strip():
            fname.touch()
            content = ""

        if content is None:
            return

        if not before_text.strip():
            # append to existing file, or start a new file
            new_content = content + after_text
        else:
            new_content = replace_most_similar_chunk(content, before_text, after_text)

        return new_content


