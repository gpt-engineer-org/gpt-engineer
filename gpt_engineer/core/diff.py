import logging
from collections import Counter
from copy import deepcopy

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
        self.lines.insert(line, index)
        self.category_counts[RETAIN] += 1

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

    @staticmethod
    def future_line_match(line, lines_dict):
        return any([is_similar(line, file_line) for file_line in lines_dict.values()])

    def validate_and_correct(self, lines_dict: dict) -> bool:
        # rule out the case that its a new file
        if self.is_new_file:
            # this hunk cannot be falsified and is by definition true
            return True
        # check the location of the actual starting line:
        start_true = is_similar(self.lines[0][1], lines_dict[self.start_line_pre_edit])

        if not start_true:
            # now find the true starting line compare to all lines and see how many matches we get
            # ToDo handle the case where the start line is 0 or 1 characters separately
            # ToDo handle the case where the start line is an add (and shouldn't exist in the orig file)
            pot_start_lines = [
                is_similar(self.lines[0], line)
                for line in lines_dict[self.start_line_pre_edit].values()
            ]
            sum_of_matches = sum(pot_start_lines)
            if sum_of_matches == 0:
                # ToDo handle this case constructively
                raise ValueError(
                    f"The starting line of the diff {self.hunk_to_string()} does not exist in the code"
                )
            elif sum_of_matches == 1:
                start_ind = pot_start_lines.index(True)
            else:
                logging.warning("multiple candidates for starting index")
                # ToDo handle all the cases better again here. Smartest choice is that, for each candidate check match to the next line etc (recursively)
                start_ind = pot_start_lines.index(True)
            self.start_line_pre_edit = start_ind
            # This should now be fulfilled by default
            assert is_similar(self.lines[0], lines_dict[self.start_line_pre_edit])

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
                # check if we get a match further down the road
                if self.future_line_match(
                    self.lines[hunk_ind][1],
                    {key: val for key, val in lines_dict.items() if key > file_ind},
                ):
                    # now we assume that some lines were simply skipped and we should add them to the diff
                    self.add_retained_line(self.lines[hunk_ind][1], hunk_ind)
                    hunk_ind += 1
                    file_ind += 1
                # if we don't, we have a problem
                else:
                    raise ValueError(
                        f"The line {self.lines[hunk_ind][1]} in the diff cannot be found in the code"
                    )
            else:
                hunk_ind += 1
                file_ind += 1
        if file_ind < len(self.lines) - 1:
            remaining_lines = "\n".join(self.lines[file_ind + 1 :])
            raise ValueError(
                f"Hunk validation stopped before the lines {remaining_lines} were validated. The diff is incorrect"
            )


class Diff:
    def __init__(self, filename_pre, filename_post):
        self.filename_pre = filename_pre
        self.filename_post = filename_post
        self.hunks = []

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
            hunk.validate_and_correct(cut_lines_dict)
            if past_hunk is not None:
                cut_lines_dict = {
                    key: val
                    for key, val in cut_lines_dict.items()
                    if key
                    >= (past_hunk.start_line_pre_edit + past_hunk.hunk_len_pre_edit)
                }
            past_hunk = hunk


def is_similar(str1, str2):
    """
    Compares two strings for similarity, ignoring spaces and case.

    Parameters
    ----------
    str1, str2 : str
        The strings to compare.

    Returns
    -------
    bool
        True if the strings are similar, False otherwise.
    """
    str1, str2 = str1.replace(" ", "").lower(), str2.replace(" ", "").lower()

    counter1, counter2 = Counter(str1), Counter(str2)
    intersection = sum((counter1 & counter2).values())
    longer_length = max(len(str1), len(str2))

    return intersection >= 0.9 * longer_length
