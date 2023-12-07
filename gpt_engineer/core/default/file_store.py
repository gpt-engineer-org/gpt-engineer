import tempfile
from pathlib import Path

from gpt_engineer.core.files_dict import FilesDict


class FileStore:
    def __init__(self, path: str | Path | None = None):
        if path is None:
            path = Path(tempfile.mkdtemp(prefix="gpt-engineer-"))

        self.working_dir = Path(path)
        self.working_dir.mkdir(parents=True, exist_ok=True)
        self.id = self.working_dir.name.split("-")[-1]

    def upload(self, files: FilesDict):
        for name, content in files.items():
            path = self.working_dir / name
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w") as f:
                f.write(content)
        return self

    def download(self) -> FilesDict:
        files = {}
        for path in self.working_dir.glob("**/*"):
            if path.is_file():
                with open(path, "r") as f:
                    try:
                        content = f.read()
                    except UnicodeDecodeError:
                        content = "binary file"
                    files[str(path.relative_to(self.working_dir))] = content
        return FilesDict(files)
