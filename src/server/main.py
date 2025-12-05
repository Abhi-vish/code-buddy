import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    Prompt,
    TextContent,
    TextResourceContents,
)

from .config import ServerConfig
from .tools import get_all_tools
from .resources import ResourceManager
from .prompts import get_all_prompts
from src.shared import logger, ToolResultStatus


class CodingAgentServer:
    
    def __init__(self, config: ServerConfig = None):
        self.config = config or ServerConfig.from_env()
        self.server = Server(self.config.name)
        self.tools = get_all_tools(self.config.project_root)
        self.resource_manager = ResourceManager(self.config.project_root)
        self.prompts = get_all_prompts()
        self._tool_map = {tool.name: tool for tool in self.tools}
        self._prompt_map = {prompt.name: prompt for prompt in self.prompts}
        self._register_handlers()
    
    def _register_handlers(self):
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            return [tool.to_mcp_tool() for tool in self.tools]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            if name not in self._tool_map:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]
            
            tool = self._tool_map[name]
            result = await tool.execute(**arguments)
            
            return [TextContent(type="text", text=result.content)]
        
        @self.server.list_resources()
        async def list_resources() -> list[Resource]:
            resources = self.resource_manager.list_all()
            return [r.to_mcp_resource() for r in resources]
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> list[TextResourceContents]:
            content = await self.resource_manager.read(uri)
            
            if uri.startswith("file://"):
                mime_type = "text/plain"
            elif uri.endswith(".json") or "summary" in uri or "files" in uri:
                mime_type = "application/json"
            else:
                mime_type = "text/plain"
            
            return [TextResourceContents(
                uri=uri,
                mimeType=mime_type,
                text=content
            )]
        
        @self.server.list_prompts()
        async def list_prompts() -> list[Prompt]:
            return [prompt.to_mcp_prompt() for prompt in self.prompts]
        
        @self.server.get_prompt()
        async def get_prompt(name: str, arguments: dict | None):
            if name not in self._prompt_map:
                raise ValueError(f"Unknown prompt: {name}")
            
            prompt = self._prompt_map[name]
            return await prompt.get_result(**(arguments or {}))
    
    async def run(self):
        async with stdio_server() as (read_stream, write_stream):
            logger.info(f"Starting {self.config.name} v{self.config.version}")
            logger.info(f"Project root: {self.config.project_root}")
            
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


def main():
    config = ServerConfig.from_env()
    server = CodingAgentServer(config)
    asyncio.run(server.run())


if __name__ == "__main__":
    main()