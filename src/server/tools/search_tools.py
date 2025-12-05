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
        
