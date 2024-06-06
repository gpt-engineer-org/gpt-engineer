from pathlib import Path

from gpt_engineer.core.files_dict import FilesDict


class Files(FilesDict):
    def __init__(self, project_path: str, selected_files: list):
        """
        Initialize the Files object by reading the content of the provided file paths.

        Parameters
        ----------
        project_path : str
            The base path of the project.
        selected_files : list
            List of file paths relative to the project path.
        """

        self.project_path = project_path
        # Convert the list of selected files and their relative directory into a dictionary of relative file paths
        content_dict = {}
        for file_path in selected_files:
            try:
                with open(
                    Path(project_path) / file_path, "r", encoding="utf-8"
                ) as content:
                    content_dict[str(file_path)] = content.read()
            except FileNotFoundError:
                print(f"Warning: File not found {file_path}")
            except UnicodeDecodeError:
                print(f"Warning: File not UTF-8 encoded {file_path}, skipping")
        super().__init__(content_dict)

    def write_to_disk(self, files: FilesDict):
        for name, content in files.items():
            path = Path(self.project_path) / name
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w") as f:
                f.write(content)
        return self
