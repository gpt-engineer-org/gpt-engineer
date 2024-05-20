import os
import platform
import subprocess

from typing import List, Tuple
from collections import defaultdict

import yaml


class FileSelection:
    """
    Manages the active files in a project directory and creates a YAML file listing them.
    """

    def __init__(self, project_path: str, repository):
        self.repository = repository
        self.yaml_path = os.path.join(project_path, ".feature", "files.yml")
        self._initialize()

    def _paths_to_tree(self, paths):
        def nested_dict():
            return defaultdict(nested_dict)

        tree = nested_dict()

        files_marker = "(./)"

        for path in paths:
            parts = path.split(os.sep)
            file = parts.pop()
            d = tree
            for part in parts:
                d = d[part]
            if files_marker not in d:
                d[files_marker] = []
            d[files_marker].append(file)

        def default_to_regular(d):
            if isinstance(d, defaultdict):
                d = {k: default_to_regular(v) for k, v in d.items()}
            return d

        def ordered_dict(data):
            if isinstance(data, dict):
                keys = sorted(data.keys(), key=lambda x: (x == files_marker, x))
                return {k: ordered_dict(data[k]) for k in keys}
            return data

        ordered_tree = ordered_dict(default_to_regular(tree))

        return ordered_tree
        # return yaml.dump(tree, sort_keys=False)

    def _tree_to_paths(self, tree):

        files_marker = "(./)"

        def traverse_tree(tree, base_path=""):
            paths = []
            if tree:
                for key, value in tree.items():
                    if key == files_marker:
                        if value:
                            for file in value:
                                paths.append(os.path.join(base_path, file))
                    else:
                        subfolder_path = os.path.join(base_path, key)
                        paths.extend(traverse_tree(value, subfolder_path))
            return paths

        # tree = yaml.safe_load(yaml_content)
        return traverse_tree(tree)

    def _write_yaml_with_header(self, yaml_content):
        with open(self.yaml_path, "w") as file:
            file.write(
                f"""# Complete list of files shared with the AI
# Please comment out any files not needed as context for this change
# This saves money and avoids overwhelming the AI
{yaml_content}"""
            )

    def _initialize(self):
        """
        Generates a YAML file from the tracked files if one doesnt exist
        """

        if os.path.exists(self.yaml_path):
            return

        print("YAML file is missing or empty, generating YAML...")

        tree = self._paths_to_tree(self.repository.get_tracked_files())

        self._write_yaml_with_header(yaml.dump(tree, sort_keys=False))

    def _get_from_yaml(self) -> Tuple[List[str], List[str]]:
        with open(self.yaml_path, "r") as file:
            original_content_lines = file.readlines()[
                3:
            ]  # Skip the 3 instruction lines

        # Create a version of the content with all lines uncommented
        commented_content = "".join(original_content_lines)
        uncommented_content = "".join(
            line.replace("# ", "").replace("#", "") for line in original_content_lines
        )

        print(uncommented_content)

        included_files = self._tree_to_paths(yaml.safe_load(commented_content))
        all_files = self._tree_to_paths(yaml.safe_load(uncommented_content))

        # Determine excluded files by finding the difference
        excluded_files = list(set(all_files) - set(included_files))

        return (included_files, excluded_files)

    def _set_to_yaml(self, selected_files, excluded_files):
        # Dont worry about commenting lines if they are no excluded files
        if not excluded_files:
            tree = self._paths_to_tree(selected_files)

            self._write_yaml_with_header(yaml.dump(tree, sort_keys=False))

            return

        all_files = list(selected_files) + list(excluded_files)

        current_tree = self._paths_to_tree(all_files)

        # Add a # in front of files which are excluded. This is a marker for us to go back and properly comment them out
        def mark_excluded_files(structure, prefix=""):
            for i, item in enumerate(structure):
                if isinstance(item, dict):
                    for key, value in item.items():
                        mark_excluded_files(value, prefix + key)
                else:
                    full_path = prefix + item
                    if full_path in excluded_files:
                        structure[i] = f"#{item}"

        mark_excluded_files(current_tree)

        # Find all files marked for commenting - add comment and remove the mark.
        def comment_marked_files(yaml_content):
            lines = yaml_content.split("\n")

            updated_lines = []
            for line in lines:
                if "#" in line:
                    line = "#" + line.replace("#", "")
                updated_lines.append(line)

            return "\n".join(updated_lines)

        content = yaml.dump(tree, sort_keys=False)

        updated_content = comment_marked_files(content)

        self._write_yaml_with_header(updated_content)

        return

    def update_yaml_from_tracked_files(self):
        """
        Updates the YAML file with the current list of tracked files.
        """

        tracked_files = self.repository.get_tracked_files()

        selected_files, excluded_files = self._get_from_yaml()

        print(excluded_files)

        # If there are no changes, do nothing
        if set(tracked_files) == set(selected_files + excluded_files):
            return

        new_selected_files = list(set(tracked_files) - set(excluded_files))

        self._set_to_yaml(new_selected_files, excluded_files)

    def get_from_yaml(self):
        """
        Get selected file paths from yaml
        """

        selected_files, excluded_files = self._get_from_yaml()

        return selected_files

    def get_pretty_from_yaml(self):
        """
        Retrieves selected file paths from the YAML file and prints them in an ASCII-style tree structure.
        """
        # Get selected files from YAML
        selected_files = self.get_from_yaml()

        # Helper function to insert a path into the tree dictionary
        def insert_path(tree, path_parts):
            # Recursively build nested dictionary from path parts
            if not path_parts:
                return
            if path_parts[0] not in tree:
                tree[path_parts[0]] = {}
            insert_path(tree[path_parts[0]], path_parts[1:])

        # Create a nested dictionary from the list of file paths
        file_tree = {}
        for filepath in selected_files:
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
