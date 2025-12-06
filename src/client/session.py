import asyncio
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from mcp import ClientSession
from mcp.client.stdio import stdio_client


class MCPSession:
    
    def __init__(self, session: ClientSession):
        self._session = session
    
    async def list_tools(self):
        return await self._session.list_tools()
    
    async def call_tool(self, name: str, arguments: dict):
        return await self._session.call_tool(name, arguments)
    
    async def list_resources(self):
        return await self._session.list_resources()
    
    async def read_resource(self, uri: str):
        return await self._session.read_resource(uri)
    
    async def list_prompts(self):
        return await self._session.list_prompts()
    
    async def get_prompt(self, name: str, arguments: dict | None = None):
        return await self._session.get_prompt(name, arguments)


class MCPSessionManager:
    
    def __init__(
        self,
        server_command: str,
        server_args: list[str] | None = None,
        env: dict | None = None,
        cwd: str | Path | None = None
    ):
        self.server_command = server_command
        self.server_args = server_args or []
        self.env = env
        self.cwd = Path(cwd) if cwd else None
    
    @asynccontextmanager
    async def connect(self):
        from mcp.client.stdio import StdioServerParameters
        
        server_params = StdioServerParameters(
            command=self.server_command,
            args=self.server_args,
            env=self.env
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                yield MCPSession(session)
    
    @classmethod
    def create(
        cls,
        project_root: str | Path | None = None,
        server_module: str = "src.server.main"
    ):
        env = {}
        if project_root:
            env["PROJECT_ROOT"] = str(project_root)
        
        return cls(
            server_command=sys.executable,
            server_args=["-m", server_module],
            env=env if env else None
        )
    
    @classmethod
    def for_python_server(
        cls,
        server_path: str | Path,
        project_root: str | Path | None = None
    ):
        env = {}
        if project_root:
            env["PROJECT_ROOT"] = str(project_root)
        
        server_path = Path(server_path)
        
        if server_path.suffix == ".py":
            args = [str(server_path)]
        else:
            args = ["-m", str(server_path)]
        
        return cls(
            server_command=sys.executable,
            server_args=args,
            env=env if env else None
        )
    
    @classmethod
    def for_node_server(
        cls,
        server_path: str | Path,
        project_root: str | Path | None = None
    ):
        env = {}
        if project_root:
            env["PROJECT_ROOT"] = str(project_root)
        
        return cls(
            server_command="node",
            server_args=[str(server_path)],
            env=env if env else None
        )
    
    @classmethod
    def for_npx_server(
        cls,
        package_name: str,
        project_root: str | Path | None = None
    ):
        env = {}
        if project_root:
            env["PROJECT_ROOT"] = str(project_root)
        
        return cls(
            server_command="npx",
            server_args=["-y", package_name],
            env=env if env else None
        )