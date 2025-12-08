import asyncio
import json
from pathlib import Path
from .base import BaseTool
from src.shared import ToolResult
from src.server.utils import PathValidator
import aiohttp


class HttpRequestTool(BaseTool):

    name: str = "http_request_tool"
    description: str = "Make HTTP requests to specified URLs"

    def __init__(self, project_root: Path, allow_external: bool = True):
        self.project_root = project_root
        self.allow_external = allow_external
        self.path_validator = PathValidator(project_root, allow_external)

    def get_input_schema(self) -> dict:
        return {
            "type":"object",
            "properties": {
                "url":{
                    "type": "string",
                    "description": "The URL to make the HTTP request to"
                },
                "method":{
                    "type": "string",
                    "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"],
                    "description": "HTTP method to use"
                },
                "headers":{
                    "type":"object",
                    "description":"HTTP headers as key-value pairs"
                },
                "body": {
                    "type": "string",
                    "description": "Request body (JSON String)"
                },
                "timeout":{
                    "type": "integer",
                    "description": "Timeout for the request in seconds"
                }
            },
            "required": ["url", "method"]
        }
    
    async def execute(
            self, 
            url: str,
            method: str,
            headers: dict = None,
            body: str = None,
            timeout: int = None
    ) -> ToolResult:
        try:
            async with aiohttp.clientSession() as session:
                kwargs = {
                    "method": method,
                    "url": url,
                    "timeout":aiohttp.clientTimeout(total=timeout)
                }

                if headers:
                    kwargs["headers"] = headers
                
                if body:
                    kwargs["data"] = body
                    if not headers or "Content-Type" not in headers:
                        kwargs.setdefault("headers", {})["Content-Type"] = "application/json"

                async with session.request(**kwargs) as response:
                    status = response.status
                    response_header = dict(response.headers)

                    try:
                        body = await response.text()
                        body_str = json.dumps(json.loads(body), indent=2)
                    except Exception:
                        body_str = await response.text()
                
                    result = f"Status: {status}"
                    result += f"\nHeaders: {json.dumps(response_header, indent=2)}"
                    result += f"\nBody: {body_str}"

                    return self.success(result)
        except Exception as e:
            try:
                import urllib.request
                import urllib.error

                req = urllib.request.Request(url, method=method)
                if headers:
                    for key, value in headers.items():
                        req.add_header(key, value)

                if body:
                    req.data = body.encode('utf-8')

                with urllib.request.urlopen(req, timeout=timeout) as response:
                    status = response.status
                    body_str = response.read().decode('utf-8')

                    try:
                        body_str = json.dumps(json.loads(body_str), indent=2)
                    except Exception:
                        pass
                    
                    return self.success(f"Status: {status}\nBody: {body_str}")
            except urllib.error.HTTPError as http_err:
                return self.error(f"HTTP error occurred: {str(http_err)}")
        
        except Exception as e:
            return self.error(f"Error making HTTP request: {str(e)}")
        

class CurlTool(BaseTool):

    name: str = "curl_tool"
    description: str = "Make HTTP requests using curl command"

    def __init__(self, project_root: Path, allow_external: bool = True):
        self.project_root = project_root
        self.allow_external = allow_external
        self.path_validator = PathValidator(project_root, allow_external)

    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "curl_command": {
                    "type": "string",
                    "description": "The full curl command to execute"
                }
            },
            "required": ["curl_command"]
        }
    
    async def execute(
            self,
            curl_command: str
    ) -> ToolResult:
        try:
            process = await asyncio.create_subprocess_shell(
                curl_command,
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
            return self.error(f"Error executing curl command: {str(e)}")