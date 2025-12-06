import asyncio
from pathlib import Path
from src.shared import ToolResult
from .base import BaseTool


class GitTool(BaseTool):
    
    name: str = "git"
    description: str = "Run git commands"
    
    def __init__(self, project_root: Path, allow_external: bool = True):
        self.project_root = project_root
    
    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Git command (without 'git' prefix)"
                }
            },
            "required": ["command"]
        }
    
    async def execute(self, command: str) -> ToolResult:
        try:
            process = await asyncio.create_subprocess_shell(
                f"git {command}",
                cwd=self.project_root,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            output_parts = []
            if stdout:
                output_parts.append(stdout.decode())
            if stderr:
                output_parts.append(stderr.decode())
            
            output = "\n".join(output_parts) if output_parts else "(no output)"
            
            if process.returncode == 0:
                return self.success(output)
            else:
                return self.error(output)
        except Exception as e:
            return self.error(str(e))
        
        
class GitStatusTool(BaseTool):
    
    name: str = "git_status"
    description: str = "Get git status of the project"
    
    def __init__(self, project_root: Path, allow_external: bool = True):
        self.project_root = project_root
    
    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {}
        }
    
    async def execute(self) -> ToolResult:
        try:
            process = await asyncio.create_subprocess_exec(
                "git", "status", "--porcelain",
                cwd=self.project_root,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                return self.error(stderr.decode() if stderr else "Git command failed")
            
            output = stdout.decode().strip()
            if not output:
                return self.success("Working directory clean")
            
            return self.success(output)
        except Exception as e:
            return self.error(str(e))


class GitDiffTool(BaseTool):
    
    name: str = "git_diff"
    description: str = "Show git diff"
    
    def __init__(self, project_root: Path, allow_external: bool = True):
        self.project_root = project_root
    
    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "Specific file to diff (optional)"
                },
                "staged": {
                    "type": "boolean",
                    "description": "Show staged changes"
                }
            }
        }
    
    async def execute(self, filepath: str = None, staged: bool = False) -> ToolResult:
        try:
            cmd = ["git", "diff"]
            
            if staged:
                cmd.append("--staged")
            
            if filepath:
                cmd.append("--")
                cmd.append(filepath)
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=self.project_root,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                return self.error(stderr.decode() if stderr else "Git diff failed")
            
            output = stdout.decode().strip()
            if not output:
                return self.success("No changes")
            
            return self.success(output)
        except Exception as e:
            return self.error(str(e))


class GitLogTool(BaseTool):
    
    name: str = "git_log"
    description: str = "Show git commit history"
    
    def __init__(self, project_root: Path, allow_external: bool = True):
        self.project_root = project_root
    
    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "count": {
                    "type": "integer",
                    "description": "Number of commits to show"
                },
                "oneline": {
                    "type": "boolean",
                    "description": "One line per commit"
                }
            }
        }
    
    async def execute(self, count: int = 10, oneline: bool = True) -> ToolResult:
        try:
            cmd = ["git", "log", f"-{count}"]
            
            if oneline:
                cmd.append("--oneline")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=self.project_root,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                return self.error(stderr.decode() if stderr else "Git log failed")
            
            return self.success(stdout.decode())
        except Exception as e:
            return self.error(str(e))
