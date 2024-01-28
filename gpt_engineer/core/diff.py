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
        self.category_counts = {"retain": 0, "add": 0, "remove": 0}
        self.lines = list()
        self.set_lines(lines)  # This will be a list of tuples (line_type, line_content)

    def set_lines(self, new_lines):
        for line in new_lines:
            self.lines.append(line)
            self.category_counts[line[0]] += 1

    def hunk_to_string(self):
        string = f"@@ -{self.start_line_pre_edit},{self.hunk_len_pre_edit} +{self.start_line_post_edit},{self.hunk_len_post_edit} @@\n"
        for line_type, line_content in self.lines:
            line_prefix = (
                " " if line_type == "retain" else "+" if line_type == "add" else "-"
            )
            string += f"{line_prefix}{line_content}\n"
        return string
