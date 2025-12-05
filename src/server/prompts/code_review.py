from mcp.types import PromptArgument, PromptMessage
from .base import BasePrompt


class CodeReviewPrompt(BasePrompt):
    
    name = "code_review"
    description = "Review code and provide detailed feedback"
    
    def get_arguments(self) -> list[PromptArgument]:
        return [
            PromptArgument(
                name="code",
                description="Code to review",
                required=True
            ),
            PromptArgument(
                name="language",
                description="Programming language",
                required=False
            ),
            PromptArgument(
                name="focus",
                description="Specific areas to focus on",
                required=False
            )
        ]
    
    async def generate(
        self,
        code: str,
        language: str = "python",
        focus: str = ""
    ) -> list[PromptMessage]:
        
        focus_text = f"\n\nFocus areas: {focus}" if focus else ""
        
        prompt = f"""Review this {language} code and provide detailed feedback.

            Code:
            {language}
            {code}
        """
        return [
            PromptMessage(
                role="user",
                content=prompt
            )
        ]
    
class QuickReviewPrompt(BasePrompt):
    
    name = "quick_code_review"
    description = "Provide a quick review of the given code snippet"
    
    def get_arguments(self) -> list[PromptArgument]:
        return [
            PromptArgument(
                name="code_snippet",
                description="Code snippet to review",
                required=True
            ),
            PromptArgument(
                name="language",
                description="Programming language",
                required=False
            )
        ]
    
    async def generate(
        self,
        code_snippet: str,
        language: str = "python"
    ) -> list[PromptMessage]:
        
        prompt = f"""Provide a quick review of this {language} code snippet.

            Code:
            {language}
            {code_snippet}
        """
        return [
            PromptMessage(
                role="user",
                content=prompt
            )
        ]