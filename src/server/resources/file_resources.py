from pathlib import Path
from src.server.utils import *
from .base import BaseResource


class FileResources(BaseResource):
    
    def __init__(self, project_root: Path, filepath: Path):
        self.project_root = project_root
        self.filepath = filepath
        self.validator = PathValidator(project_root)
        self._full_path = self.validator.validate(filepath)
        self.name = str(filepath)
        self.description = f"File: {filepath}"
        self.mime_type = get_mime_type(self._full_path)

    def get_uri(self) -> str:
        return f"file://{self.filepath}"
    
    async def read(self) -> str:
        return read_file(self._full_path)
    

class FileResourceProvider:

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.validator = PathValidator(project_root)

    def list_all(self) -> list[FileResources]:
        files = collect_project_files(self.project_root)
        resources = []
        for filepath in files:
            relative_path = self.validator.get_relative(filepath)
            resources.append(FileResources(self.project_root, Path(relative_path)))
        return resources
    
    def get_resource(self, uri: str | Path) -> FileResources | None:
        if not uri.startswith("file://"):
            raise ValueError("URI must start with 'file://'")
    
        filepath = uri[len("file://") :]
        return FileResources(self.project_root, filepath)
    
    def get_by_pattern(self, pattern: str) -> list[FileResources]:
        import fnmatch

        all_resources = self.list_all()

        matched = []
        for resource in all_resources:
            if fnmatch.fnmatch(str(resource.name), pattern):
                matched.append(resource)

        return matched