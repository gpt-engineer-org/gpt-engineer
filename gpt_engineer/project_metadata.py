# gpt_engineer/project_metadata.py

class DB:
    def __init__(self, path):
        self.path = path

class ProjectMetadataDB(DB):
    def __init__(self, path):
        super().__init__(path)
