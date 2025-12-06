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
                "cwd": {
                    "type": "string",
                    "description": "Working directory (optional, defaults to project root)"
                },
                "timeout": {
                    "type": "integer",
                    "description": "Timeout in seconds (default: 60)"
                }
            },
            "required": ["command"]
        }
    
    async def execute(self, command: str, cwd: str = None, timeout: int = 60) -> ToolResult:
        try:
            # Use specified working directory or default to project root
            work_dir = Path(cwd) if cwd else self.project_root
            
            # Ensure the directory exists
            if not work_dir.exists():
                return self.error(f"Working directory does not exist: {work_dir}")
            
            process = await asyncio.create_subprocess_shell(
                command,
                cwd=str(work_dir),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                stdin=asyncio.subprocess.DEVNULL  # Prevent hanging on input
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()  # Ensure cleanup
                return self.error(f"Command timed out after {timeout}s")
            
            output_parts = []
            
            if stdout:
                stdout_text = stdout.decode('utf-8', errors='replace')
                if stdout_text.strip():
                    output_parts.append(f"STDOUT:\n{stdout_text}")
            
            if stderr:
                stderr_text = stderr.decode('utf-8', errors='replace')
                if stderr_text.strip():
                    output_parts.append(f"STDERR:\n{stderr_text}")
            
            exit_code = process.returncode
            status = "Success" if exit_code == 0 else f"Failed (exit code: {exit_code})"
            
            output = "\n\n".join(output_parts) if output_parts else "(no output)"
            
            return self.success(f"{status}\n\n{output}")
        except Exception as e:
            return self.error(f"Command execution error: {str(e)}")
        
class RunPythonTool(BaseTool):
    
    name: str = "run_python"
    description: str = "Run a Python script or code"
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
    
    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Python code to execute"
                },
                "filepath": {
                    "type": "string",
                    "description": "Python file to run (alternative to code)"
                },
                "timeout": {
                    "type": "integer",
                    "description": "Timeout in seconds"
                }
            }
        }
    
    async def execute(
        self,
        code: str = None,
        filepath: str = None,
        timeout: int = 30
    ) -> ToolResult:
        try:
            if code:
                cmd = ["python", "-c", code]
            elif filepath:
                cmd = ["python", filepath]
            else:
                return self.error("Provide either code or filepath")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
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
                return self.error(f"Execution timed out after {timeout}s")
            
            output_parts = []
            
            if stdout:
                output_parts.append(f"Output:\n{stdout.decode()}")
            
            if stderr:
                output_parts.append(f"Errors:\n{stderr.decode()}")
            
            output = "\n\n".join(output_parts) if output_parts else "(no output)"
            
            if process.returncode == 0:
                return self.success(output)
            else:
                return self.error(output)
        except Exception as e:
            return self.error(str(e))