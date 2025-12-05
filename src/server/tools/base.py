from abc import ABC, abstractmethod
from typing import Any
from mcp.types import Tool, TextContent
from src.shared.models import ToolResult, ToolResultStatus


class BaseTool(ABC):

    name: str
    description: str

    @abstractmethod
    def get_input_schema(self) -> dict:
        pass

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        pass

    def to_mcp_tool(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema=self.get_input_schema()
        )
    
    def success(self, content: str, data: Any = None) -> ToolResult:
        return ToolResult(
            status=ToolResultStatus.SUCCESS,
            content=content,
            data=data
        )
    
    def error(self, content: str) -> ToolResult:
        return ToolResult(
            status=ToolResultStatus.ERROR,
            content=content
        )
    
    def to_text_content(self, text: str) -> TextContent:
        return [TextContent(
            text=text
        )]