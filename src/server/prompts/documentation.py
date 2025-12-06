from mcp.types import PromptArgument, PromptMessage
from .base import BasePrompt


class GenerateDocstringPrompt(BasePrompt):
    
    name = "generate_docstring"
    description = "Generate docstring for a function or class"
    
    def get_arguments(self) -> list[PromptArgument]:
        return [
            PromptArgument(
                name="code",
                description="Function or class code",
                required=True
            ),
            PromptArgument(
                name="style",
                description="Docstring style (google, numpy, sphinx)",
                required=False
            )
        ]
    
    async def generate(self, code: str, style: str = "google") -> list[PromptMessage]:
        prompt = f"""Generate a {style}-style docstring for this code:
{code}

Include:
1. Brief description
2. Parameters with types
3. Return value with type
4. Raises section if applicable
5. Example usage"""

        return [self.create_user_message(prompt)]


class GenerateReadmePrompt(BasePrompt):
    
    name = "generate_readme"
    description = "Generate README documentation"
    
    def get_arguments(self) -> list[PromptArgument]:
        return [
            PromptArgument(
                name="project_name",
                description="Name of the project",
                required=True
            ),
            PromptArgument(
                name="description",
                description="Brief project description",
                required=True
            ),
            PromptArgument(
                name="files_summary",
                description="Summary of project files",
                required=False
            )
        ]
    
    async def generate(
        self,
        project_name: str,
        description: str,
        files_summary: str = ""
    ) -> list[PromptMessage]:
        
        context = ""
        if files_summary:
            context = f"\n\nProject structure:\n{files_summary}"
        
        prompt = f"""Generate a README.md for this project:

Project: {project_name}
Description: {description}{context}

Include:
1. Title and description
2. Installation instructions
3. Usage examples
4. Configuration options
5. Contributing guidelines
6. License section placeholder"""

        return [self.create_user_message(prompt)]


class GenerateTestsPrompt(BasePrompt):
    
    name = "generate_tests"
    description = "Generate unit tests for code"
    
    def get_arguments(self) -> list[PromptArgument]:
        return [
            PromptArgument(
                name="code",
                description="Code to test",
                required=True
            ),
            PromptArgument(
                name="framework",
                description="Test framework (pytest, unittest)",
                required=False
            )
        ]
    
    async def generate(self, code: str, framework: str = "pytest") -> list[PromptMessage]:
        prompt = f"""Generate comprehensive unit tests using {framework}:
{code}
Include:
1. Tests for normal behavior
2. Edge cases
3. Error handling tests
4. Mocking where appropriate
5. Clear test names

Generate production-ready test code."""

        return [self.create_user_message(prompt)]


class GenerateAPIDocsPrompt(BasePrompt):
    
    name = "generate_api_docs"
    description = "Generate API documentation"
    
    def get_arguments(self) -> list[PromptArgument]:
        return [
            PromptArgument(
                name="code",
                description="API code (endpoints, functions)",
                required=True
            ),
            PromptArgument(
                name="format",
                description="Documentation format (markdown, openapi)",
                required=False
            )
        ]
    
    async def generate(self, code: str, format: str = "markdown") -> list[PromptMessage]:
        prompt = f"""Generate {format} API documentation for:
{code}

Include:
1. Endpoint/function descriptions
2. Request/response formats
3. Parameters and types
4. Example requests and responses
5. Error codes and messages"""

        return [self.create_user_message(prompt)]