import logging

from collections import Counter
from typing import Optional, Tuple

RETAIN = "retain"
ADD = "add"
REMOVE = "remove"


class Hunk:
    def __init__(
        self,
        start_line_pre_edit,
        hunk_len_pre_edit,
        start_line_post_edit,
        hunk_len_post_edit,
        lines,
    ):
        self.start_line_pre_edit = start_line_pre_edit
        self.hunk_len_pre_edit = hunk_len_pre_edit
        self.start_line_post_edit = start_line_post_edit
        self.hunk_len_post_edit = hunk_len_post_edit
        self.category_counts = {RETAIN: 0, ADD: 0, REMOVE: 0}
        self.lines = list()
        self.add_lines(lines)
        # Note that this assumption should not be done on hunk level, however, if the below is true, no validation is possible anyway.
        if self.category_counts[RETAIN] == 0 and self.category_counts[REMOVE] == 0:
            self.is_new_file = True
        else:
            self.is_new_file = False

    def add_retained_line(self, line, index):
        self.lines.insert(index, (RETAIN, line))
        self.category_counts[RETAIN] += 1

    def relabel_line(self, index, new_label):
        old_label = self.lines[index][0]
        self.lines[index] = (new_label, self.lines[index][1])
        self.category_counts[old_label] -= 1
        self.category_counts[new_label] += 1

    def pop_line(self, line, index):
        self.lines.pop(index)
        assert self.category_counts[line[0]] > 0
        self.category_counts[line[0]] -= 1

    def add_lines(self, new_lines):
        for line in new_lines:
            self.lines.append(line)
            self.category_counts[line[0]] += 1

    def hunk_to_string(self):
        string = f"@@ -{self.start_line_pre_edit},{self.hunk_len_pre_edit} +{self.start_line_post_edit},{self.hunk_len_post_edit} @@\n"
        for line_type, line_content in self.lines:
            line_prefix = (
                " " if line_type == RETAIN else "+" if line_type == ADD else "-"
            )
            string += f"{line_prefix}{line_content}\n"
        return string

    # @staticmethod
    # def future_line_match(line, lines_dict):
    #     return any([is_similar(line, file_line) for file_line in lines_dict.values()])

    def make_forward_block(self, hunk_ind: int, forward_block_len) -> str:
        forward_lines = [
            line[1] for line in self.lines[hunk_ind:] if not line[0] == ADD
        ]
        forward_block = "\n".join(forward_lines[0:forward_block_len])
        return forward_block

    def validate_and_correct(
        self, lines_dict: dict, forward_block_len: int = 10
    ) -> Tuple[bool, Optional[str]]:
        # salvaging correct hunks
        error_message: Optional[str] = None
        # rule out the case that its a new file
        if self.is_new_file:
            # this hunk cannot be falsified and is by definition true
            return True, error_message
        # check the location of the actual starting line:
        start_true = is_similar(self.lines[0][1], lines_dict[self.start_line_pre_edit])

        if not start_true:
            # now find the true starting line compare to all lines and see how many matches we get
            # ToDo handle the case where the start line is 0 or 1 characters separately
            # handle the case where the start line is an add
            if self.lines[0][0] == ADD:
                start_line = None
                # find the first line that is not an add
                for index, line in enumerate(self.lines):
                    if line[0] != ADD:
                        for line_number, line_content in lines_dict.items():
                            # if the line is similar to a non-blank line in line_dict, we can pick the line prior to it
                            if is_similar(line[1], line_content) and line[1] != "":
                                start_line = line_number - 1
                                break
                        # if the start line is not found, this should be a comment from LLM
                        if start_line is None:
                            self.relabel_line(index, ADD)
                            continue
                        else:
                            # the line prior to the start line is found now we insert it to the first place as the start line
                            self.start_line_pre_edit = start_line
                            self.add_retained_line(lines_dict[start_line], 0)
                            return self.validate_and_correct(
                                lines_dict, forward_block_len
                            )

            pot_start_lines = {
                key: is_similar(self.lines[0][1], line)
                for key, line in lines_dict.items()
            }
            sum_of_matches = sum(pot_start_lines.values())
            if sum_of_matches == 0:
                # before we go any further, we should check if it's a comment from LLM
                if self.lines[0][1].count("#") > 0:
                    # if it is, we can mark it as an ADD lines
                    self.relabel_line(0, ADD)
                    # and restart the validation at the next line
                    return self.validate_and_correct(lines_dict, forward_block_len)

                else:
                    return (
                        False,
                        f"In {self.hunk_to_string()}:The starting line of the diff {self.hunk_to_string()} does not exist in the code",
                    )
            elif sum_of_matches == 1:
                start_ind = list(pot_start_lines.keys())[
                    list(pot_start_lines.values()).index(True)
                ]  # lines are one indexed
            else:
                logging.warning("multiple candidates for starting index")
                # ToDo handle all the cases better again here. Smartest choice is that, for each candidate check match to the next line etc (recursively)
                start_ind = list(pot_start_lines.keys())[
                    list(pot_start_lines.values()).index(True)
                ]
            self.start_line_pre_edit = start_ind
            # This should now be fulfilled by default
            assert is_similar(self.lines[0][1], lines_dict[self.start_line_pre_edit])

        # Now we should be able to validate the hunk line by line and add missing line
        hunk_ind = 0
        file_ind = self.start_line_pre_edit
        # make an orig hunk lines for logging
        # orig_hunk_lines = deepcopy(self.lines)
        while hunk_ind < len(self.lines) and file_ind <= max(lines_dict):
            if self.lines[hunk_ind][0] == ADD:
                # this cannot be validated, jump one index
                hunk_ind += 1
            elif not is_similar(self.lines[hunk_ind][1], lines_dict[file_ind]):
                # before we go any further, we should relabel the comment from LLM
                if self.lines[hunk_ind][1].count("#") > 0:
                    self.relabel_line(hunk_ind, ADD)
                    continue

                # make a forward block from the code for comparisons
                forward_code = "\n".join(
                    [
                        lines_dict[ind]
                        for ind in range(
                            file_ind,
                            min(file_ind + forward_block_len, max(lines_dict.keys())),
                        )
                    ]
                )
                # make the original forward block for quantitative comparison
                forward_block = self.make_forward_block(hunk_ind, forward_block_len)
                orig_count_ratio = count_ratio(forward_block, forward_code)
                # Here we have 2 cases
                # 1) some lines were simply skipped in the diff and we should add them to the diff
                # If this is the case, adding the line to the diff, should give an improved forward diff
                forward_block_missing_line = self.make_forward_block(
                    hunk_ind, forward_block_len - 1
                )
                # insert the missing line in front of the block
                forward_block_missing_line = "\n".join(
                    [lines_dict[file_ind], forward_block_missing_line]
                )
                missing_line_count_ratio = count_ratio(
                    forward_block_missing_line, forward_code
                )
                # 2) Additional lines, not belonging to the code were added to the diff
                forward_block_false_line = self.make_forward_block(
                    hunk_ind + 1, forward_block_len
                )
                false_line_count_ratio = count_ratio(
                    forward_block_false_line, forward_code
                )
                if (
                    orig_count_ratio >= missing_line_count_ratio
                    and orig_count_ratio >= false_line_count_ratio
                ):
                    return (
                        False,
                        f"In {self.hunk_to_string()}:The trail of the diff, {forward_block}, does not match the code {forward_code}.",
                    )
                elif missing_line_count_ratio > false_line_count_ratio:
                    self.add_retained_line(lines_dict[file_ind], hunk_ind)
                    hunk_ind += 1
                    file_ind += 1
                    # NOTE: IF THE LLM SKIPS SOME LINES AND HAS ADDs ADJACENT TO THE SKIPPED BLOCK,
                    # WE CANNOT KNOW WHETHER THE ADDs SHOULD BE BEFORE OR AFTER THE BLOCK. WE OPT FOR PUTTING IT BEFORE.
                    # IF IT MATTERED, WE ASSUME THE LLM WOULD NOT SKIP THE BLOCK
                else:
                    self.pop_line(self.lines[hunk_ind], hunk_ind)

            else:
                hunk_ind += 1
                file_ind += 1
        # if we have not validated all lines, we have a problem
        if hunk_ind < len(self.lines) - 1:
            remaining_lines = "\n".join(
                f"{line_type}: {line_content}"
                for line_type, line_content in self.lines[file_ind + 1 :]
            )

            return (
                False,
                f"In {self.hunk_to_string()}:Hunk validation stopped before the lines {remaining_lines} were validated. The diff is incorrect",
            )


class Diff:
    def __init__(self, filename_pre, filename_post):
        self.filename_pre = filename_pre
        self.filename_post = filename_post
        self.hunks = []

    def is_new_file(self):
        return any([hunk.is_new_file for hunk in self.hunks])

    def diff_to_string(self):
        string = f"--- {self.filename_pre}\n"
        string += f"+++ {self.filename_post}\n"
        for hunk in self.hunks:
            string += hunk.hunk_to_string()
        return string.strip()

    def validate_and_correct(self, lines_dict: dict):
        past_hunk = None
        cut_lines_dict = lines_dict.copy()
        for hunk in self.hunks:
            if past_hunk is not None:
                # make sure to not cut so much that the start_line gets out of range
                cut_ind = min(
                    past_hunk.start_line_pre_edit + past_hunk.hunk_len_pre_edit,
                    hunk.start_line_pre_edit,
                )
                cut_lines_dict = {
                    key: val for key, val in cut_lines_dict.items() if key >= (cut_ind)
                }
            hunk.validate_and_correct(cut_lines_dict)
            # now correct the numbers, assuming the start line pre-edit has been fixed
            hunk.hunk_len_pre_edit = (
                hunk.category_counts[RETAIN] + hunk.category_counts[REMOVE]
            )
            hunk.hunk_len_post_edit = (
                hunk.category_counts[RETAIN] + hunk.category_counts[ADD]
            )
            if past_hunk is not None:
                hunk.start_line_post_edit = (
                    hunk.start_line_pre_edit
                    + past_hunk.hunk_len_post_edit
                    - past_hunk.hunk_len_pre_edit
                    + past_hunk.start_line_post_edit
                    - past_hunk.start_line_pre_edit
                )
            else:
                hunk.start_line_post_edit = hunk.start_line_pre_edit
            past_hunk = hunk


def is_similar(str1, str2, similarity_threshold=0.9):
    """
    Compares two strings for similarity, ignoring spaces and case.

    Parameters
    ----------
    str1, str2 : str
        The strings to compare.
    similarity_threshold: float
        How similar must the strings be

    Returns
    -------
    bool
        True if the strings are similar, False otherwise.
    """

    return count_ratio(str1, str2) >= similarity_threshold


def count_ratio(str1, str2):
    str1, str2 = str1.replace(" ", "").lower(), str2.replace(" ", "").lower()

    counter1, counter2 = Counter(str1), Counter(str2)
    intersection = sum((counter1 & counter2).values())
    longer_length = max(len(str1), len(str2))
    if longer_length == 0:
        return 1
    else:
        return intersection / longer_length
