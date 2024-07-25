import os
import yaml
from collections import defaultdict


def paths_to_yaml(paths):
    def nested_dict():
        return defaultdict(nested_dict)

    tree = nested_dict()

    for path in paths:
        parts = path.split(os.sep)
        file = parts.pop()
        d = tree
        for part in parts:
            d = d[part]
        if "/" not in d:
            d["/"] = []
        d["/"].append(file)

    def default_to_regular(d):
        if isinstance(d, defaultdict):
            d = {k: default_to_regular(v) for k, v in d.items()}
        return d

    tree = default_to_regular(tree)

    return yaml.dump(tree, sort_keys=False)


def yaml_to_paths(yaml_content):
    def traverse_tree(tree, base_path=""):
        paths = []
        for key, value in tree.items():
            if key == "./":
                for file in value:
                    paths.append(os.path.join(base_path, file))
            else:
                subfolder_path = os.path.join(base_path, key)
                paths.extend(traverse_tree(value, subfolder_path))
        return paths

    tree = yaml.safe_load(yaml_content)
    return traverse_tree(tree)


# Example usage
yaml_content = """
folder:
  ./:
  # - file1.txt
  - file2.txt
  subfolder:
    ./:
    - file3.txt
"""

paths = yaml_to_paths(yaml_content)
print(paths)


# paths = ["folder/file1.txt", "folder/file2.txt", "folder/subfolder/file3.txt"]

# yaml_output = paths_to_yaml(paths)
# print(yaml_output)
