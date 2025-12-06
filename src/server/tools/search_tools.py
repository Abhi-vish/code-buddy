import re
from pathlib import Path
from src.shared import ToolResult, SearchMatch
from src.server.utils import PathValidator, collect_project_files, read_file, matches_pattern
from .base import BaseTool


class SearchInFilesTool(BaseTool):
    
    name: str = "search_in_files"
    description: str = "Search for text or pattern across project files"
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.validator = PathValidator(project_root)
    
    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "Text or regex pattern to search"
                },
                "file_pattern": {
                    "type": "string",
                    "description": "File glob pattern (e.g., *.py)"
                },
                "case_sensitive": {
                    "type": "boolean",
                    "description": "Case sensitive search"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results"
                }
            },
            "required": ["pattern"]
        }
    
    async def execute(
        self,
        pattern: str,
        file_pattern: str = "*",
        case_sensitive: bool = False,
        max_results: int = 100
    ) -> ToolResult:
        try:
            flags = 0 if case_sensitive else re.IGNORECASE
            regex = re.compile(pattern, flags)
            
            files = collect_project_files(self.project_root)
            results = []
            
            for filepath in files:
                if not matches_pattern(filepath, file_pattern):
                    continue
                
                try:
                    content = read_file(filepath)
                except Exception:
                    continue
                
                lines = content.splitlines()
                for line_num, line in enumerate(lines, 1):
                    match = regex.search(line)
                    if match:
                        rel_path = self.validator.get_relative(filepath)
                        results.append(f"{rel_path}:{line_num}: {line.strip()}")
                        
                        if len(results) >= max_results:
                            break
                
                if len(results) >= max_results:
                    break
            
            if not results:
                return self.success("No matches found")
            
            header = f"Found {len(results)} matches:\n\n"
            return self.success(header + "\n".join(results))
        except re.error as e:
            return self.error(f"Invalid regex pattern: {e}")
        except Exception as e:
            return self.error(str(e))
        
class FindReplaceTool(BaseTool):
    
    name = "find_replace"
    description = "Find and replace text in a single file"
    
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
                "find": {
                    "type": "string",
                    "description": "Text to find"
                },
                "replace": {
                    "type": "string",
                    "description": "Text to replace with"
                },
                "all_occurrences": {
                    "type": "boolean",
                    "description": "Replace all occurrences"
                }
            },
            "required": ["filepath", "find", "replace"]
        }
    
    async def execute(
        self,
        filepath: str,
        find: str,
        replace: str,
        all_occurrences: bool = True
    ) -> ToolResult:
        try:
            full_path = self.validator.validate(filepath)
            content = read_file(full_path)
            
            count = content.count(find)
            if count == 0:
                return self.error("Text not found in file")
            
            if all_occurrences:
                new_content = content.replace(find, replace)
            else:
                new_content = content.replace(find, replace, 1)
                count = 1
            
            full_path.write_text(new_content)
            return self.success(f"Replaced {count} occurrence(s) in {filepath}")
        except Exception as e:
            return self.error(str(e))


class FindReplaceAllTool(BaseTool):
    
    name = "find_replace_all"
    description = "Find and replace text across multiple files"
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.validator = PathValidator(project_root)
    
    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "find": {
                    "type": "string",
                    "description": "Text to find"
                },
                "replace": {
                    "type": "string",
                    "description": "Text to replace with"
                },
                "file_pattern": {
                    "type": "string",
                    "description": "File glob pattern (e.g., *.py)"
                }
            },
            "required": ["find", "replace"]
        }
    
    async def execute(
        self,
        find: str,
        replace: str,
        file_pattern: str = "*"
    ) -> ToolResult:
        try:
            files = collect_project_files(self.project_root)
            files_modified = 0
            total_replacements = 0
            
            for filepath in files:
                if not matches_pattern(filepath, file_pattern):
                    continue
                
                try:
                    content = read_file(filepath)
                except Exception:
                    continue
                
                if find in content:
                    count = content.count(find)
                    new_content = content.replace(find, replace)
                    filepath.write_text(new_content)
                    files_modified += 1
                    total_replacements += count
            
            return self.success(
                f"Replaced {total_replacements} occurrence(s) in {files_modified} file(s)"
            )
        except Exception as e:
            return self.error(str(e))
