import os
import shutil
import tempfile
import unittest

from gpt_engineer.applications.interactive_cli.file_selection import FileSelection


class MockRepository:
    def __init__(self, files):
        self.files = files

    def get_tracked_files(self):
        return self.files


class TestFileSelection(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for the test
        self.test_dir = tempfile.mkdtemp()
        self.project_path = self.test_dir
        os.makedirs(os.path.join(self.project_path, ".feature"), exist_ok=True)

        # Initial file structure for the mock repository
        self.initial_files = [
            "folder1/file1",
            "folder1/file2",
            "folder1/folder2/file3",
            "folder1/folder2/file4",
            "file5",
            "file6",
        ]
        self.repository = MockRepository(self.initial_files)

        # Initialize the FileSelection object
        self.file_selection = FileSelection(self.project_path, self.repository)

    def tearDown(self):
        # Remove the temporary directory after the test
        shutil.rmtree(self.test_dir)

    def test_lifecycle(self):
        # Step 1: Create YAML file from the mock repository
        self.file_selection._initialize()
        expected_yaml_initial = """# Complete list of files shared with the AI
# Please comment out any files not needed as context for this change
# This saves money and avoids overwhelming the AI
- folder1/:
  - folder2/:
    - file3
    - file4
  - file1
  - file2
- file5
- file6
"""
        with open(self.file_selection.yaml_path, "r") as file:
            initial_yaml_content = file.read()

        self.assertEqual(initial_yaml_content, expected_yaml_initial)

        # Step 2: Update the YAML file directly (simulating user comments)
        edited_yaml_content = """# Complete list of files shared with the AI
# Please comment out any files not needed as context for this change
# This saves money and avoids overwhelming the AI
- folder1/:
  - folder2/:
    # - file3
    # - file4
  # - file1
  - file2
# - file5
- file6
"""
        with open(self.file_selection.yaml_path, "w") as file:
            file.write(edited_yaml_content)

        # Step 3: Update tracked files in the repository and update the YAML file
        new_files = [
            "folder1/file1",
            "folder1/file2",
            "folder1/folder2/file3",
            "folder1/folder2/file4",
            "file5",
            "file6",
            "newfile7",
        ]
        self.repository.files = new_files
        self.file_selection.update_yaml_from_tracked_files()

        expected_yaml_updated = """# Complete list of files shared with the AI
# Please comment out any files not needed as context for this change
# This saves money and avoids overwhelming the AI
- folder1/:
  - folder2/:
    # - file3
    # - file4
  # - file1
  - file2
# - file5
- file6
- newfile7
"""
        with open(self.file_selection.yaml_path, "r") as file:
            updated_yaml_content = file.read()

        self.assertEqual(updated_yaml_content, expected_yaml_updated)

        # Step 4: Get files from YAML and verify
        selected_files = self.file_selection.get_from_yaml()
        expected_selected_files = ["folder1/file2", "file6", "newfile7"]

        self.assertEqual(selected_files, expected_selected_files)


if __name__ == "__main__":
    unittest.main()
