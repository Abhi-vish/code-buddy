import asyncio
from pathlib import Path
from .base import BaseTool
from src.shared import ToolResult
from src.server.utils import PathValidator


class DockerTool(BaseTool):

    name: str = "docker_tool"
    description: str = "Run docker commands"

    def __init__(self, project_root: Path, allow_external: bool = True):
        self.project_root = project_root
        self.allow_external = allow_external
        self.path_validator = PathValidator(project_root, allow_external)

    def get_input_schema(self) -> dict:
        return {
            "type":"object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Docker command to execute"
                }
            },
            "required": ["command"]
        }
    
    async def execute(self, command: str) -> ToolResult:
        try: 
            process = await asyncio.create_subprocess_shell(
                f"docker {command}",
                cwd=self.project_root,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()
            output = stdout.decode().strip()

            if process.returncode == 0:
                return self.success(output)
            else:
                return self.error(output)
        except Exception as e:
            return self.error(f"{str(e)}")
            

class DockerBuildTool(BaseTool):

    name: str = "docker_build_tool"
    description: str = "Build Docker image"

    def __init__(self, project_root: Path, allow_external: bool = True):
        self.project_root = project_root
        self.allow_external = allow_external
        self.path_validator = PathValidator(project_root, allow_external)

    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "tag": {
                    "type": "string",
                    "description": "Tag for the Docker image"
                },
                "dockerfile": {
                    "type": "string",
                    "description": "Path to the Dockerfile"
                },
                "context":{
                    "type": "string",
                    "description": "Build context path"
                }
            },
            "required":["tag"]
        }
    
    async def execute(
            self,
            tag: str,
            dockerfile: str = "Dockerfile",
            context: str = "."
    ) -> ToolResult:
        try: 
            cmd = f"docker build -t {tag} -f {dockerfile} {context}"

            process = await asyncio.create_subprocess_shell(
                cmd,
                cwd=self.project_root,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()
            output = stdout.decode() + stderr.decode()

            if process.returncode == 0:
                return self.success(f"Built image: {tag}\n{output}")
            else:
                return self.error(output)
        except Exception as e:
            return self.error(f"Error building image: {str(e)}")
        

class DockerComposeTool(BaseTool):

    name: str = "docker_compose_tool"
    description: str = "run docker-compose commands"

    def __init__(self, project_root: Path, allow_external: bool = True):
        self.project_root = project_root
        self.allow_external = allow_external
        self.path_validator = PathValidator(project_root, allow_external)

    def get_input_schema(self) -> dict:
        return {
            "type":"object",
            "properties":{
                "command":{
                    "type":"string",
                    "enum": ["up", "down", "build", "pull", "push", "logs"],
                    "description": "Docker-compose command to execute"
                },
                "detach":{
                    "type":"boolean",
                    "description":"Run containers in background (only for 'up' command)"
                },
                "service":{
                    "type":"string",
                    "description":"Specific service to target (optional)"
                }
            },
            "required":["command"]
        }
    
    async def execute(
            self,
            command: str,
            detach: bool = True,
            service: str = ""
    ) -> ToolResult:
        try:
            cmd = f"docker-compose {command}"

            if command == "up" and detach:
                cmd += " -d"

            if service:
                cmd += f" {service}"

            process = await asyncio.create_subprocess_shell(
                cmd,
                cwd=self.project_root,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()
            output = stdout.decode() + stderr.decode()
            if process.returncode == 0:
                return self.success(output)
            else:
                return self.error(output)
        except Exception as e:
            return self.error(f"Error running docker-compose command: {str(e)}")