import json
from pathlib import Path
from src.shared import ToolResult
from src.server.utils import PathValidator, read_file
from .base import BaseTool


class AnalyzeCodeTool(BaseTool):
    
    name: str = "analyze_code"
    description: str = "Analyze code file and provide statistics"
    
    def __init__(self, project_root: Path):
        self.validator = PathValidator(project_root)
    
    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "Path to the file to analyze"
                }
            },
            "required": ["filepath"]
        }
    
    async def execute(self, filepath: str) -> ToolResult:
        try:
            full_path = self.validator.validate(filepath)
            content = read_file(full_path)
            lines = content.splitlines()
            
            total_lines = len(lines)
            blank_lines = sum(1 for line in lines if not line.strip())
            code_lines = total_lines - blank_lines
            
            analysis = {
                "filepath": filepath,
                "total_lines": total_lines,
                "code_lines": code_lines,
                "blank_lines": blank_lines,
                "characters": len(content),
                "extension": full_path.suffix
            }
            
            return self.success(json.dumps(analysis, indent=2))
        except Exception as e:
            return self.error(str(e))


class GetFunctionsTool(BaseTool):
    
    name: str = "get_functions"
    description: str = "Extract function and class definitions from a Python file"
    
    def __init__(self, project_root: Path):
        self.validator = PathValidator(project_root)
    
    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "Path to the Python file"
                }
            },
            "required": ["filepath"]
        }
    
    async def execute(self, filepath: str) -> ToolResult:
        try:
            import ast
            
            full_path = self.validator.validate(filepath)
            content = read_file(full_path)
            
            tree = ast.parse(content)
            
            functions = []
            classes = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    args = [arg.arg for arg in node.args.args]
                    functions.append({
                        "name": node.name,
                        "line": node.lineno,
                        "args": args
                    })
                elif isinstance(node, ast.ClassDef):
                    methods = []
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            methods.append(item.name)
                    classes.append({
                        "name": node.name,
                        "line": node.lineno,
                        "methods": methods
                    })
            
            result = {
                "filepath": filepath,
                "functions": functions,
                "classes": classes
            }
            
            return self.success(json.dumps(result, indent=2))
        except SyntaxError as e:
            return self.error(f"Syntax error: {e}")
        except Exception as e:
            return self.error(str(e))


class FormatCodeTool(BaseTool):
    
    name: str = "format_code"
    description: str = "Format a Python file using black"
    
    def __init__(self, project_root: Path):
        self.validator = PathValidator(project_root)
    
    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "Path to the file to format"
                }
            },
            "required": ["filepath"]
        }
    
    async def execute(self, filepath: str) -> ToolResult:
        try:
            import subprocess
            
            full_path = self.validator.validate(filepath)
            
            result = subprocess.run(
                ["black", str(full_path)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return self.success(f"Formatted: {filepath}")
            else:
                return self.error(result.stderr)
        except FileNotFoundError:
            return self.error("black is not installed. Run: pip install black")
        except Exception as e:
            return self.error(str(e))


class LintCodeTool(BaseTool):
    
    name: str = "lint_code"
    description: str = "Lint a Python file using ruff or flake8"
    
    def __init__(self, project_root: Path):
        self.validator = PathValidator(project_root)
    
    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "Path to the file to lint"
                }
            },
            "required": ["filepath"]
        }
    
    async def execute(self, filepath: str) -> ToolResult:
        try:
            import subprocess
            
            full_path = self.validator.validate(filepath)
            
            try:
                result = subprocess.run(
                    ["ruff", "check", str(full_path)],
                    capture_output=True,
                    text=True
                )
                linter = "ruff"
            except FileNotFoundError:
                result = subprocess.run(
                    ["flake8", str(full_path)],
                    capture_output=True,
                    text=True
                )
                linter = "flake8"
            
            output = result.stdout or result.stderr
            
            if result.returncode == 0:
                return self.success(f"No issues found ({linter})")
            else:
                return self.success(f"Issues found ({linter}):\n\n{output}")
        except FileNotFoundError:
            return self.error("No linter found. Install ruff or flake8")
        except Exception as e:
            return self.error(str(e))