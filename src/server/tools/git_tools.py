import asyncio
from pathlib import Path
from src.shared import ToolResult
from .base import BaseTool


class GitTool(BaseTool):
    
    name: str = "git"
    description: str = "Run git commands"
    
    def __init__(self, project_root: Path):
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