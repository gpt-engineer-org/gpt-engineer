import os
import platform
import subprocess
import yaml
from pathlib import Path


from gpt_engineer.core.default.paths import memory_path
from gpt_engineer.core.ai import AI

from gpt_engineer.applications.feature_cli.repository import Repository
from gpt_engineer.applications.feature_cli.files import Files
from gpt_engineer.applications.feature_cli.generation_tools import (
    fuzzy_parse_file_selection,
)
from gpt_engineer.applications.feature_cli.domain import FileSelection


def paths_to_tree(paths):
    tree = {}
    files_marker = "(./)"

    for path in paths:
        parts = path.split("/")
        current_level = tree

        for part in parts[:-1]:
            if part not in current_level:
                current_level[part] = {}
            current_level = current_level[part]

        if isinstance(current_level, dict):
            if files_marker not in current_level:
                current_level[files_marker] = []
            current_level[files_marker].append(parts[-1])

    # Clean and sort the tree to match the required format
    def clean_tree(node):
        if not isinstance(node, dict):
            return node
        sorted_keys = sorted(node.keys(), key=lambda x: (x == files_marker, x))
        cleaned_node = {key: clean_tree(node[key]) for key in sorted_keys}
        if sorted_keys == [files_marker]:
            return cleaned_node[files_marker]
        return cleaned_node

    cleaned_tree = clean_tree(tree)
    return cleaned_tree


def tree_to_paths(tree):

    files_marker = "(./)"

    def traverse_tree(tree, base_path=""):
        paths = []
        if tree:
            for key, value in tree.items():
                if key == files_marker:
                    if value:
                        for file in value:
                            paths.append(os.path.join(base_path, file))
                elif isinstance(value, list):
                    for file in value:
                        paths.append(os.path.join(base_path, key, file))
                else:
                    subfolder_path = os.path.join(base_path, key)
                    paths.extend(traverse_tree(value, subfolder_path))
        return paths

    return traverse_tree(tree)


def commented_yaml_to_file_selection(commented_content) -> FileSelection:
    commented_content_lines = commented_content.split("\n")
    uncommented_content_1 = "\n".join(
        line.replace("# ", "").replace("#", "") for line in commented_content_lines
    )
    uncommented_content_2 = "\n".join(
        line.replace("#", "") for line in commented_content_lines
    )

    included_files = tree_to_paths(yaml.safe_load(commented_content))
    try:
        all_files = tree_to_paths(yaml.safe_load(uncommented_content_1))
    except:
        try:
            all_files = tree_to_paths(yaml.safe_load(uncommented_content_2))
        except:
            raise ValueError(
                "Could not convert the commented yaml to a file selection. Please check the format."
            )

    included_files_not_in_all_files = set(included_files) - set(all_files)

    if len(included_files_not_in_all_files) > 0:
        raise ValueError("Yaml file selection has not been read correctly.")

    excluded_files = list(set(all_files) - set(included_files))
    return FileSelection(included_files, excluded_files)


def file_selection_to_commented_yaml(selection: FileSelection) -> str:
    # Dont worry about commenting lines if they are no excluded files
    if not selection.excluded_files:
        tree = paths_to_tree(selection.included_files)

        return yaml.dump(tree, sort_keys=False)

    all_files = list(selection.included_files) + list(selection.excluded_files)

    current_tree = paths_to_tree(all_files)

    # Add a # in front of files which are excluded. This is a marker for us to go back and properly comment them out
    def mark_excluded_files(structure, prefix=""):
        if isinstance(structure, dict):
            for key, value in structure.items():
                if key == "(./)":
                    structure[key] = mark_excluded_files(value, prefix)
                else:
                    new_prefix = os.path.join(prefix, key)
                    structure[key] = mark_excluded_files(value, new_prefix)
        elif isinstance(structure, list):
            for i, item in enumerate(structure):
                full_path = os.path.join(prefix, item)

                if full_path in selection.excluded_files:
                    structure[i] = f"#{item}"

        return structure

    mark_excluded_files(current_tree)

    content = yaml.dump(current_tree, sort_keys=False)

    # Find all files marked for commenting - add comment and remove the mark.
    def comment_marked_files(yaml_content):
        lines = yaml_content.split("\n")

        updated_lines = []
        for line in lines:
            if "#" in line:
                line = line.replace("- '#", "#- ").replace("'", "")
            updated_lines.append(line)

        return "\n".join(updated_lines)

    commented_yaml = comment_marked_files(content)

    return commented_yaml


class FileSelector:
    """
    Manages the active files in a project directory and creates a YAML file listing them.
    """

    def __init__(self, project_path: str, repository: Repository):
        self.project_path = project_path
        self.ai = AI("gpt-4o", temperature=0)
        self.repository = repository
        self.yaml_path = Path(project_path) / ".feature" / "files.yml"

        if os.path.exists(self.yaml_path):
            return

        print("YAML file is missing or empty, generating YAML...")

        file_selection = FileSelection([], self.repository.get_tracked_files())

        self.set_to_yaml(file_selection)

    def _write_yaml_with_header(self, yaml_content):

        def add_indentation(content):
            lines = content.split("\n")
            new_lines = []
            last_key = None

            for line in lines:
                stripped_line = line.replace("#", "").strip()
                if stripped_line.endswith(":"):
                    last_key = stripped_line
                if stripped_line.startswith("- ") and (last_key != "(./):"):
                    # add 2 spaces at the begining of line or after any #

                    new_lines.append("  " + line)  # Add extra indentation
                else:
                    new_lines.append(line)
            return "\n".join(new_lines)

        indented_content = add_indentation(yaml_content)
        with open(self.yaml_path, "w") as file:
            file.write(
                f"""# Uncomment any files you would like to use for this feature
# Note that (./) is a special key which represents files at the root of the parent directory

{indented_content}"""
            )

    def _read_yaml_with_headers(self):
        with open(self.yaml_path, "r") as file:
            original_content_lines = file.readlines()[3:]

        return "".join(original_content_lines)

    def set_to_yaml(self, file_selection):

        commented_yaml = file_selection_to_commented_yaml(file_selection)

        self._write_yaml_with_header(commented_yaml)

        return

    def update_yaml_from_tracked_files(self):
        """
        Updates the YAML file with the current list of tracked files.
        """

        tracked_files = self.repository.get_tracked_files()

        file_selection = self.get_from_yaml()

        # If there are no changes, do nothing
        if set(tracked_files) == set(
            file_selection.included_files + file_selection.excluded_files
        ):
            return

        new_included_files = list(
            set(tracked_files) - set(file_selection.excluded_files)
        )

        self.set_to_yaml(
            FileSelection(new_included_files, file_selection.excluded_files)
        )

    def get_from_yaml(self) -> FileSelection:
        """
        Get selected file paths and excluded file paths from yaml
        """

        yaml_content = self._read_yaml_with_headers()

        try:
            file_selection = commented_yaml_to_file_selection(yaml_content)
        except:
            print(
                "Could not read the file selection from the YAML file. Attempting to fix with AI"
            )
            print(yaml_content)
            file_selection = fuzzy_parse_file_selection(self.ai, yaml_content)
            self.set_to_yaml(file_selection)

        return file_selection

    def get_pretty_selected_from_yaml(self) -> str:
        """
        Retrieves selected file paths from the YAML file and prints them in an ASCII-style tree structure.
        """
        # Get selected files from YAML
        file_selection = self.get_from_yaml()

        # Helper function to insert a path into the tree dictionary
        def insert_path(tree, path_parts):
            # Recursively build nested dictionary from path parts
            if not path_parts:
                return
            if path_parts[0] not in tree:
                tree[path_parts[0]] = {}
            insert_path(tree[path_parts[0]], path_parts[1:])

        file_tree = {}
        for filepath in file_selection.included_files:
            parts = filepath.split("/")
            insert_path(file_tree, parts)

        # Helper function to format the tree into a string with ASCII graphics
        def format_tree(tree, prefix=""):
            lines = []
            # Separate directories and files
            directories = {k: v for k, v in tree.items() if v}
            files = {k: v for k, v in tree.items() if not v}
            # Sort items to keep alphabetical order, directories first
            items = sorted(directories.items()) + sorted(files.items())
            for i, (key, sub_tree) in enumerate(items):
                if i == len(items) - 1:  # Last item uses └──
                    lines.append(prefix + "└── " + key)
                    extension = "    "
                else:
                    lines.append(prefix + "├── " + key)
                    extension = "│   "
                if sub_tree:
                    lines.extend(format_tree(sub_tree, prefix=prefix + extension))
            return lines

        # Generate formatted tree lines
        tree_lines = format_tree(file_tree)

        # Join lines and return as a string
        return "\n".join(tree_lines)

    def open_yaml_in_editor(self):
        """
        Opens the generated YAML file in the default system editor.
        If the YAML file is empty or doesn't exist, generate it first.
        """

        # Platform-specific methods to open the file
        if platform.system() == "Windows":
            os.startfile(self.yaml_path)
        elif platform.system() == "Darwin":
            subprocess.run(["open", self.yaml_path])
        else:  # Linux and other Unix-like systems
            subprocess.run(["xdg-open", self.yaml_path])

    def get_included_as_file_repository(self):
        file_selection = self.get_from_yaml()

        return Files(self.project_path, file_selection.included_files)
