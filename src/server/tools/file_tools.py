from pathlib import Path
from src.shared import ToolResult
from src.server.utils import PathValidator, read_file, write_file
from .base import BaseTool


class ReadFileTool(BaseTool):

    name: str = "read_file"
    description: str = "Reads the content of a text file at the specified path"

    def __init__(self, project_root: Path):
        self.path_validator = PathValidator(project_root)

    def get_input_schema(self)-> dict:
        return {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "The path to the file to read, relative to the project root."
                }
            },
            "required": ["filepath"]
        }
    
    async def execute(self, filepath: str) -> ToolResult:
        try:
            full_path = self.path_validator.validate(filepath)
            content = read_file(full_path)
            return self.success(content)
        except Exception as e:
            return self.error(str(e))
        

class WriteFileTool(BaseTool):
    
    name: str = "write_file"
    description: str = "Writes content to a text file at the specified path"
    
    def __init__(self, project_root: Path):
        self.path_validator = PathValidator(project_root)

    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "The path to the file to write, relative to the project root."
                },
                "content": {
                    "type": "string",
                    "description": "The content to write to the file."
                }
            },
            "required": ["filepath", "content"]
        }
    
    async def execute(self, filepath: str, content: str) -> ToolResult:
        try:
            full_path = self.path_validator.validate(filepath)
            write_file(full_path, content)
            return self.success(f"Successfully wrote to file '{filepath}'.")
        except Exception as e:
            return self.error(str(e))
        

class EditFileTool(BaseTool):

    name: str = "edit_file"
    description: str = "Edit a file by replacing specific content"

    def __init__(self, project_root: Path):
        self.validator = PathValidator(project_root)

    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "Path to the file"
                },
                "old_content": {
                    "type": "string",
                    "description": "The content to be replaced in the file."
                },
                "new_content": {
                    "type": "string",
                    "description": "New content to insert"
                }
            },
            "required": ["filepath", "old_content", "new_content"]
        }
    
    async def execute(self, filepath: str, old_content: str, new_content: str = None, **kwargs) -> ToolResult:
        try:
            # Handle alternative parameter names that might be sent
            if new_content is None and 'new_str' in kwargs:
                new_content = kwargs['new_str']
            
            if not new_content:
                return self.error("The 'new_content' parameter is required.")
            
            full_path = self.validator.validate(filepath)
            file_text = read_file(full_path)

            if old_content not in file_text:
                return self.error(f"Content to replace not found in file '{filepath}'.")

            updated_text = file_text.replace(old_content, new_content)
            write_file(full_path, updated_text)

            return self.success(f"File '{filepath}' edited successfully.")
        except Exception as e:
            return self.error(str(e))
        

class DeleteFileTool(BaseTool):

    name: str = "delete_file"
    description: str = "Deletes a file at the specified path"

    def __init__(self, project_root: Path):
        self.validator = PathValidator(project_root)

    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "Path to the file to delete"
                }
            },
            "required": ["filepath"]
        }
    
    async def execute(self, filepath: str) -> ToolResult:
        try:
            full_path = self.validator.validate(filepath)
            if not full_path.exists():
                return self.error(f"File '{filepath}' does not exist.")
            if not full_path.is_file():
                return self.error(f"Path '{filepath}' is not a file.")
            
            full_path.unlink()
            return self.success(f"File '{filepath}' deleted successfully.")
        except Exception as e:
            return self.error(str(e))
        

class MoveFileTool(BaseTool):

    name: str = "move_file"
    description: str = "Moves a file from one path to another"

    def __init__(self, project_root: Path):
        self.validator = PathValidator(project_root)

    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "source_path": {
                    "type": "string",
                    "description": "The current path of the file to move"
                },
                "destination_path": {
                    "type": "string",
                    "description": "The new path for the file"
                }
            },
            "required": ["source_path", "destination_path"]
        }
    
    async def execute(self, source_path: str, destination_path: str) -> ToolResult:
        try:
            src_full_path = self.validator.validate(source_path)
            dest_full_path = self.validator.validate(destination_path)

            if not src_full_path.exists():
                return self.error(f"Source file '{source_path}' does not exist.")
            if not src_full_path.is_file():
                return self.error(f"Source path '{source_path}' is not a file.")

            dest_full_path.parent.mkdir(parents=True, exist_ok=True)
            src_full_path.rename(dest_full_path)

            return self.success(f"File moved from '{source_path}' to '{destination_path}' successfully.")
        except Exception as e:
            return self.error(str(e))
        

class CopyFileTool(BaseTool):

    name: str = "copy_file"
    description: str = "Copies a file from one path to another"

    def __init__(self, project_root: Path):
        self.validator = PathValidator(project_root)

    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "source_path": {
                    "type": "string",
                    "description": "The current path of the file to copy"
                },
                "destination_path": {
                    "type": "string",
                    "description": "The new path for the copied file"
                }
            },
            "required": ["source_path", "destination_path"]
        }
    
    async def execute(self, source_path: str, destination_path: str) -> ToolResult:
        try:
            src_full_path = self.validator.validate(source_path)
            dest_full_path = self.validator.validate(destination_path)

            if not src_full_path.exists():
                return self.error(f"Source file '{source_path}' does not exist.")
            if not src_full_path.is_file():
                return self.error(f"Source path '{source_path}' is not a file.")

            dest_full_path.parent.mkdir(parents=True, exist_ok=True)
            content = read_file(src_full_path)
            write_file(dest_full_path, content)

            return self.success(f"File copied from '{source_path}' to '{destination_path}' successfully.")
        except Exception as e:
            return self.error(str(e))