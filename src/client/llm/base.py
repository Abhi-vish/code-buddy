from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncIterator


@dataclass
class Message:
    role:str
    content: str
    
@dataclass
class ToolCall:
    id:str
    name:str
    arguments:str
    
@dataclass
class LLMResponse:
    content: str | None
    tool_calls: list[ToolCall] | None
    finish_reason: str
    
class BaseLLM(ABC):
    
    model: str
    
    @abstractmethod
    async def chat(
        self, 
        messages: list[Message],
        tools: list[dict] | None = None
    ) -> LLMResponse:
        pass
    
    @abstractmethod
    async def chat_stream(
        self, 
        message: list[Message],
        tools: list[dict] | None = None
    ) -> AsyncIterator[str]:
        pass
    
    def format_tool_result(self,tool_call_id:str, result: str) -> Message:
        return Message(role="tool", content=result)