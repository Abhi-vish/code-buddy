import subprocess
import asyncio
from pathlib import Path
from src.shared import ToolResult
from .base import BaseTool


class RunCommandTool(BaseTool):
    
    name: str = "run_command"
    description: str = "Run a shell command in the project directory"
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
    
    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Command to run"
                },
                "timeout": {
                    "type": "integer",
                    "description": "Timeout in seconds (default: 60)"
                }
            },
            "required": ["command"]
        }
    
    async def execute(self, command: str, timeout: int = 60) -> ToolResult:
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                cwd=self.project_root,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                return self.error(f"Command timed out after {timeout}s")
            
            output_parts = []
            
            if stdout:
                output_parts.append(f"STDOUT:\n{stdout.decode()}")
            
            if stderr:
                output_parts.append(f"STDERR:\n{stderr.decode()}")
            
            exit_code = process.returncode
            status = "Success" if exit_code == 0 else f"Failed (exit code: {exit_code})"
            
            output = "\n\n".join(output_parts) if output_parts else "(no output)"
            
            return self.success(f"{status}\n\n{output}")
        except Exception as e:
            return self.error(str(e))