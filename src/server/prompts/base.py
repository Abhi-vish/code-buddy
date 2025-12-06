from abc import ABC, abstractmethod
from mcp.types import Prompt, PromptArgument, PromptMessage, TextContent, GetPromptResult


class BasePrompt(ABC):

    name: str
    description: str

    @abstractmethod
    def get_arguments(self) -> list[PromptArgument]:
        pass

    @staticmethod
    async def generate(self, **kwargs) -> list[PromptMessage]:
        pass

    def to_mcp_prompt(self) -> Prompt:
        return Prompt(
            name=self.name,
            description=self.description,
            arguments=self.get_arguments()
        )
    
    async def get_result(self, **kwargs) -> GetPromptResult:
        messages = await self.generate(**kwargs)
        return GetPromptResult(
            description=self.description,
            messages=messages
        )
    
    def create_user_message(self, text: str) -> PromptMessage:
        return PromptMessage(
            role="user",
            contents=[TextContent(text=text)]
        )
    
    def create_assistant_message(self, text: str) -> PromptMessage:
        return PromptMessage(
            role="assistant",
            contents=TextContent(type="text",text=text)
        )