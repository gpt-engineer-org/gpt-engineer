

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







