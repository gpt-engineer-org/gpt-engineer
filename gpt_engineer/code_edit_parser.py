# strongly based on https://github.com/paul-gauthier/aider/blob/main/aider/coders/editblock_coder.py
# shout out to Paul Gauthier (https://github.com/paul-gauthier)!

import math
import re
from difflib import SequenceMatcher
from pathlib import Path


def get_edits(llm_response):
    # might raise ValueError for malformed ORIG/UPD blocks # todo <- understand comment + resolve
    return list(find_original_update_blocks(llm_response))


def apply_edits(self, edits):
    for path, original, updated in edits:
        full_path = self.abs_root_path(path)
        content = self.io.read_text(full_path)
        content = do_replace(full_path, content, original, updated)
        if content:
            self.io.write_text(full_path, content)
            continue
        raise ValueError(f"""InvalidEditBlock: edit failed!
                         
{path} does not contain the *exact sequence* of HEAD lines you specified.
Try again.
DO NOT skip blank lines, comments, docstrings, etc!
The HEAD block needs to be EXACTLY the same as the lines in {path} with nothing missing!

{path} does not contain these {len(original.splitlines())} exact lines in a row:
```
{original}```
""")


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
