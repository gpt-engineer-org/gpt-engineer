from gpt_engineer.core.files_dict import FilesDict
from pathlib import Path

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
        content_dict = {}
        for file_path in selected_files:
            try:
                with open(Path(project_path) / file_path, "r", encoding="utf-8") as content:
                    content_dict[str(file_path)] = content.read()
            except FileNotFoundError:
                print(f"Warning: File not found {file_path}")
            except UnicodeDecodeError:
                print(f"Warning: File not UTF-8 encoded {file_path}, skipping")
        super().__init__(content_dict)