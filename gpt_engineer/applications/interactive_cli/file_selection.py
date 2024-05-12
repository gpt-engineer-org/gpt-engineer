import os
import subprocess
import yaml
import platform
import yaml
from typing import List, Tuple


class FileSelection:
    """
    Manages the active files in a project directory and creates a YAML file listing them.
    """
    def __init__(self, project_path: str, repository):
        self.repository = repository
        self.yaml_path = os.path.join(project_path, '.ticket', 'files.yml')
        self._initialize()

    def _create_nested_structure_from_file_paths(self, files_paths):
        files_paths.sort()
        file_structure = []
        for filepath in files_paths:
            parts = filepath.split('/')
            # Filter out the '.ticket' directory from paths
            if '.ticket' in parts or '.feature' in parts:
                continue
            node = file_structure
            for i, part in enumerate(parts[:-1]):
                # Append '/' to part if it's a directory
                directory = part if part.endswith('/') else part + '/'
                found = False
                for item in node:
                    if isinstance(item, dict) and directory in item:
                        node = item[directory]
                        found = True
                        break
                if not found:
                    new_node = []
                    # Insert directory at the correct position (before any file)
                    index = next((idx for idx, item in enumerate(node) if isinstance(item, str)), len(node))
                    node.insert(index, {directory: new_node})
                    node = new_node
            # Add the file to the last node, ensuring directories are listed first
            if not parts[-1].endswith('/'):
                node.append(parts[-1])

        return file_structure
    

    def _write_yaml_with_comments(self, yaml_content):
        with open(self.yaml_path, 'w') as file:
            file.write(f"""# Complete list of files shared with the AI
# Please comment out any files not needed as context for this change 
# This saves money and avoids overwhelming the AI
{yaml_content}""")

    def _initialize(self):
        """
        Generates a YAML file from the tracked files if one doesnt exist
        """

        if os.path.exists(self.yaml_path):
            return
        
        print("YAML file is missing or empty, generating YAML...")

        file_structure = self._create_nested_structure_from_file_paths(self.repository.get_tracked_files())
        
        self._write_yaml_with_comments(
            yaml.safe_dump(file_structure, default_flow_style=False, sort_keys=False, indent=2)
        )

            
    def _get_from_yaml(self) -> Tuple[List[str], List[str]]:
        with open(self.yaml_path, 'r') as file:
            original_content = file.readlines()[3:] # Skip the 3 instruction lines

        # Create a version of the content with all lines uncommented
        uncommented_content = ''.join(line.lstrip('# ') for line in original_content)

        # Load the original and uncommented content as YAML
        original_structure = yaml.safe_load(''.join(original_content))
        uncommented_structure = yaml.safe_load(uncommented_content)

        def recurse_items(items, path=""):
            paths = []
            if isinstance(items, dict):
                for key, value in items.items():
                    new_path = os.path.join(path, key)
                    paths.extend(recurse_items(value, new_path))
            elif isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        paths.extend(recurse_items(item, path))
                    else:
                        paths.append(os.path.join(path, item))
            else:
                paths.append(path)
            return paths

        original_paths = recurse_items(original_structure)
        uncommented_paths = recurse_items(uncommented_structure)

        # Determine excluded files by finding the difference
        excluded_files = list(set(uncommented_paths) - set(original_paths))

        return (original_paths, excluded_files)
    
    def _set_to_yaml(self, selected_files, excluded_files):

        # Dont worry about commenting lines if they are no excluded files
        if not excluded_files:
            file_structure = self._create_nested_structure_from_file_paths(selected_files)
        
            self._write_yaml_with_comments(
                yaml.safe_dump(file_structure, default_flow_style=False, sort_keys=False, indent=2)
            )

            return
        
        all_files = list(selected_files) + list(excluded_files)

        current_structure = self._create_nested_structure_from_file_paths(all_files)

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

        mark_excluded_files(current_structure)

        # Find all files marked for commenting - add comment and remove the mark.
        def comment_marked_files(yaml_content):
            lines = yaml_content.split('\n')

            updated_lines = []
            for line in lines:
                if '#' in line:
                    line = '#' + line.replace('#', '').strip()
                updated_lines.append(line)
            
            return '\n'.join(updated_lines)

        content = yaml.safe_dump(current_structure, default_flow_style=False, sort_keys=False, indent=2)

        updated_content = comment_marked_files(content)

        self._write_yaml_with_comments(updated_content)

        return
        

    def update_yaml_from_tracked_files(self):
        """
        Updates the YAML file with the current list of tracked files.
        """

        tracked_files = self.repository.get_tracked_files()

        selected_files, excluded_files = self._get_from_yaml()

        print(set(selected_files + excluded_files))
        print(set(tracked_files))

        # If there are no changes, do nothing
        if set(tracked_files) == set(selected_files + excluded_files):
            print('yep')
            return

        new_selected_files = list(set(tracked_files) - set(excluded_files))

        self._set_to_yaml(new_selected_files, excluded_files)

    def get_from_yaml(self):
        """
        Get selected file paths from yaml
        """

        selected_files, excluded_files = self._get_from_yaml()

        return selected_files


    def open_yaml_in_editor(self):
        """
        Opens the generated YAML file in the default system editor.
        If the YAML file is empty or doesn't exist, generate it first.
        """

        # Platform-specific methods to open the file
        if platform.system() == 'Windows':
            os.startfile(self.yaml_path)
        elif platform.system() == 'Darwin':
            subprocess.run(['open', self.yaml_path])
        else:  # Linux and other Unix-like systems
            subprocess.run(['xdg-open', self.yaml_path])
