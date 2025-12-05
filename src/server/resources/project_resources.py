import json
from pathlib import Path
from src.shared import ProjectSummary
from src.server.utils import (
    collect_project_files,
    get_directory_tree,
    read_file,
    should_exclude_file,
)
from .base import BaseResource


class ProjectStructureResource(BaseResource):
    
    name = "Project Structure"
    description = "Tree view of the project directory structure"
    mime_type = "text/plain"
    
    def __init__(self, project_root: Path, max_depth: int = 4):
        self.project_root = project_root
        self.max_depth = max_depth
    
    def get_uri(self) -> str:
        return "project://structure"
    
    async def read(self) -> str:
        lines = [f"{self.project_root.name}/"]
        entries = get_directory_tree(self.project_root, self.max_depth)
        
        for entry, depth in entries:
            indent = "  " * (depth + 1)
            marker = "/" if entry.is_dir() else ""
            lines.append(f"{indent}{entry.name}{marker}")
        
        return "\n".join(lines)


class ProjectSummaryResource(BaseResource):
    
    name = "Project Summary"
    description = "Summary statistics of the project"
    mime_type = "application/json"
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
    
    def get_uri(self) -> str:
        return "project://summary"
    
    async def read(self) -> str:
        files = collect_project_files(self.project_root)
        
        total_lines = 0
        files_by_extension = {}
        
        for filepath in files:
            ext = filepath.suffix.lower() or "(no extension)"
            files_by_extension[ext] = files_by_extension.get(ext, 0) + 1
            
            try:
                content = read_file(filepath)
                total_lines += len(content.splitlines())
            except Exception:
                continue
        
        directories = [
            d.name for d in self.project_root.iterdir()
            if d.is_dir() and not should_exclude_file(d)
        ]
        
        summary = ProjectSummary(
            root_path=str(self.project_root),
            total_files=len(files),
            total_directories=len(directories),
            total_lines=total_lines,
            files_by_extension=files_by_extension,
            main_directories=sorted(directories)
        )
        
        return json.dumps({
            "root_path": summary.root_path,
            "total_files": summary.total_files,
            "total_directories": summary.total_directories,
            "total_lines": summary.total_lines,
            "files_by_extension": summary.files_by_extension,
            "main_directories": summary.main_directories
        }, indent=2)


class ProjectFilesListResource(BaseResource):
    
    name = "Project Files List"
    description = "List of all project files"
    mime_type = "application/json"
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
    
    def get_uri(self) -> str:
        return "project://files"
    
    async def read(self) -> str:
        files = collect_project_files(self.project_root)
        
        file_list = []
        for filepath in files:
            try:
                rel_path = str(filepath.relative_to(self.project_root))
                file_list.append({
                    "path": rel_path,
                    "name": filepath.name,
                    "extension": filepath.suffix,
                    "size": filepath.stat().st_size
                })
            except Exception:
                continue
        
        return json.dumps(file_list, indent=2)


class DirectoryContentsResource(BaseResource):
    
    mime_type = "application/json"
    
    def __init__(self, project_root: Path, directory: str = ""):
        self.project_root = project_root
        self.directory = directory
        self.name = f"Directory: {directory or 'root'}"
        self.description = f"Contents of {directory or 'project root'}"
    
    def get_uri(self) -> str:
        if self.directory:
            return f"project://dir/{self.directory}"
        return "project://dir"
    
    async def read(self) -> str:
        if self.directory:
            target_dir = self.project_root / self.directory
        else:
            target_dir = self.project_root
        
        if not target_dir.exists() or not target_dir.is_dir():
            return json.dumps({"error": "Directory not found"})
        
        contents = {
            "directories": [],
            "files": []
        }
        
        for entry in sorted(target_dir.iterdir(), key=lambda x: x.name.lower()):
            if entry.name.startswith("."):
                continue
            
            if entry.is_dir():
                if not should_exclude_file(entry):
                    contents["directories"].append(entry.name)
            else:
                contents["files"].append({
                    "name": entry.name,
                    "size": entry.stat().st_size
                })
        
        return json.dumps(contents, indent=2)