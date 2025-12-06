from pathlib import Path
from src.shared import ToolResult
from src.server.utils import PathValidator, get_directory_tree, should_include_file
from .base import BaseTool


class CreateDirectoryTool(BaseTool):

    name: str = "create_directory"
    description: str = "Creates a directory at the specified path (can be absolute or relative to project)."

    def __init__(self, project_root: Path, allow_external: bool = True):
        self.path_validator = PathValidator(project_root, allow_external=allow_external)

    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "dirpath": {
                    "type": "string",
                    "description": "The path to the directory to create, relative to the project root."
                }
            },
            "required": ["dirpath"]
        }

    async def execute(self, dirpath: str) -> ToolResult:
        try:
            full_path = self.path_validator.validate(dirpath)
            full_path.mkdir(parents=True, exist_ok=True)
            return self.success(f"Directory created at: {full_path}")
        except Exception as e:
            return self.error(str(e))
        

class ListDirectoryTool(BaseTool):
    
    name: str = "list_directory"
    description: str = "Lists files and directories at the specified path within the project."

    def __init__(self, project_root: Path, allow_external: bool = True):
        self.path_validator = PathValidator(project_root, allow_external=allow_external)

    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "dirpath": {
                    "type": "string",
                    "description": "The path to the directory to list (can be absolute or relative to project root)."
                },
                "recursive":{
                    "type": "boolean",
                    "description": "Whether to list files recursively."
                }
            }
        }

    async def execute(self, dirpath: str, recursive: bool = False) -> ToolResult:
        try:
            if dirpath:
                full_path = self.path_validator.validate(dirpath)
            else:
                full_path = self.project_root
            
            if not full_path.is_dir():
                return self.error(f"Path '{dirpath}' is not a directory.")
            
            if recursive:
                entries = get_directory_tree(full_path)
                lines = []
                for entry, depth in entries:
                    prefix = " " * depth
                    rel = entry.relative_to(full_path)
                    marker = "/" if entry.is_dir() else ""
                    lines.append(f"{prefix}{rel}{marker}")
                content = "\n".join(lines)
            else:
                entries = sorted(full_path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
                lines = []
                for entry in entries:
                    marker = "/" if entry.is_dir() else ""
                    lines.append(f"{entry.name}{marker}")
                content = "\n".join(lines)

            if not content:
                content = "(empty directory)"
            
            return self.success(content)
        except Exception as e:
            return self.error(str(e))
        
class DeleteDirectoryTool(BaseTool):

    name: str = "delete_directory"
    description: str = "Deletes a directory at the specified path within the project."

    def __init__(self, project_root: Path, allow_external: bool = True):
        self.path_validator = PathValidator(project_root, allow_external=allow_external)

    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "dirpath": {
                    "type": "string",
                    "description": "The path to the directory to delete (can be absolute or relative to project root)."
                }
            },
            "required": ["dirpath"]
        }

    async def execute(self, dirpath: str, force: bool = False) -> ToolResult:
        try:
            import shutil
            full_path = self.path_validator.validate(dirpath)

            if not full_path.exists():
                return self.error(f"Directory '{dirpath}' does not exist.")
            if not full_path.is_dir():
                return self.error(f"Path '{dirpath}' is not a directory.")
            if force:
                shutil.rmtree(full_path)
            else:
                full_path.rmdir()

            return self.success(f"Directory deleted at: {full_path}")
        
        except Exception as e:
            return self.error(str(e))
        

class GetTreeTool(BaseTool):

    name: str = "get_directory_tree"
    description: str = "Gets the directory tree structure starting from the specified path within the project."

    def __init__(self, project_root: Path, allow_external: bool = True):
        self.path_validator = PathValidator(project_root, allow_external=allow_external)

    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "dirpath": {
                    "type": "string",
                    "description": "The path to the directory to get the tree from (can be absolute or relative to project root)."
                },
                "max_depth": {
                    "type": "integer",
                    "description": "The maximum depth to traverse."
                }
            }
        }

    async def execute(self, dirpath: str = "", max_depth: int = 4) -> ToolResult:
        try:
            if dirpath:
                full_path = self.path_validator.validate(dirpath)
            else:
                full_path = self.project_root

            if not full_path.is_dir():
                return self.error(f"Path '{dirpath}' is not a directory.")

            entries = get_directory_tree(full_path, max_depth=max_depth)
            lines = []
            for entry, depth in entries:
                prefix = " " * depth
                rel = entry.relative_to(full_path)
                marker = "/" if entry.is_dir() else ""
                lines.append(f"{prefix}{rel}{marker}")
            content = "\n".join(lines)

            if not content:
                content = "(empty directory)"

            return self.success(content)
        except Exception as e:
            return self.error(str(e))