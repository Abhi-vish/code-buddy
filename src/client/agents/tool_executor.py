from dataclasses import dataclass
from src.client.llm import ToolCall


@dataclass
class ToolExecutionResult:
    tool_call_id: str
    tool_name: str
    result: str
    success: bool


class ToolExecutor:
    
    def __init__(self, session):
        self.session = session
    
    async def execute(self, tool_call: ToolCall) -> ToolExecutionResult:
        try:
            result = await self.session.call_tool(
                tool_call.name,
                tool_call.arguments
            )
            
            content = result.content[0].text if result.content else "No output"
            
            return ToolExecutionResult(
                tool_call_id=tool_call.id,
                tool_name=tool_call.name,
                result=content,
                success=True
            )
        except Exception as e:
            return ToolExecutionResult(
                tool_call_id=tool_call.id,
                tool_name=tool_call.name,
                result=f"Error: {str(e)}",
                success=False
            )
    
    async def execute_all(self, tool_calls: list[ToolCall]) -> list[ToolExecutionResult]:
        results = []
        for tool_call in tool_calls:
            result = await self.execute(tool_call)
            results.append(result)
        return results