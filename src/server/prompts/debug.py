from mcp.types import PromptArgument, PromptMessage
from .base import BasePrompt


class DebugErrorPrompt(BasePrompt):
    
    name = "debug_error"
    description = "Help debug an error"
    
    def get_arguments(self) -> list[PromptArgument]:
        return [
            PromptArgument(
                name="error",
                description="Error message",
                required=True
            ),
            PromptArgument(
                name="code",
                description="Related code",
                required=False
            ),
            PromptArgument(
                name="stack_trace",
                description="Stack trace",
                required=False
            )
        ]
    
    async def generate(
        self,
        error: str,
        code: str = "",
        stack_trace: str = ""
    ) -> list[PromptMessage]:
        
        parts = [f"Error: {error}"]
        
        if code:
            parts.append(f"\nCode:\n```\n{code}\n```")
        
        if stack_trace:
            parts.append(f"\nStack trace:\n```\n{stack_trace}\n```")
        
        parts.append("""
Help me:
1. Understand what's causing this error
2. Provide step-by-step fix instructions
3. Suggest how to prevent this in the future""")
        
        prompt = "\n".join(parts)
        return [self.create_user_message(prompt)]


class ExplainCodePrompt(BasePrompt):
    
    name = "explain_code"
    description = "Explain how code works"
    
    def get_arguments(self) -> list[PromptArgument]:
        return [
            PromptArgument(
                name="code",
                description="Code to explain",
                required=True
            ),
            PromptArgument(
                name="level",
                description="Explanation level (beginner, intermediate, advanced)",
                required=False
            )
        ]
    
    async def generate(self, code: str, level: str = "intermediate") -> list[PromptMessage]:
        level_context = {
            "beginner": "Explain as if I'm new to programming. Use simple terms.",
            "intermediate": "Explain assuming I know programming basics.",
            "advanced": "Provide a technical deep-dive with performance details."
        }
        
        context = level_context.get(level, level_context["intermediate"])
        
        prompt = f"""{context}

Explain this code: {code}

Cover:
1. What the code does overall
2. How each part works
3. Why certain approaches were used"""

        return [self.create_user_message(prompt)]


class FixBugPrompt(BasePrompt):
    
    name = "fix_bug"
    description = "Fix a bug in the code"
    
    def get_arguments(self) -> list[PromptArgument]:
        return [
            PromptArgument(
                name="code",
                description="Code with the bug",
                required=True
            ),
            PromptArgument(
                name="expected",
                description="Expected behavior",
                required=True
            ),
            PromptArgument(
                name="actual",
                description="Actual behavior",
                required=True
            )
        ]
    
    async def generate(self, code: str, expected: str, actual: str) -> list[PromptMessage]:
        prompt = f"""Fix the bug in this code.

Code:
{code}

Expected behavior: {expected}
Actual behavior: {actual}

Provide:
1. The root cause of the bug
2. Fixed code
3. Explanation of the fix"""

        return [self.create_user_message(prompt)]