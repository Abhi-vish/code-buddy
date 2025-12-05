from .base import BasePrompt
from .code_review import CodeReviewPrompt, QuickReviewPrompt
from .debug import DebugErrorPrompt, ExplainCodePrompt, FixBugPrompt
from .documentation import (
    GenerateDocstringPrompt,
    GenerateReadmePrompt,
    GenerateTestsPrompt,
    GenerateAPIDocsPrompt,
)


def get_all_prompts() -> list[BasePrompt]:
    return [
        CodeReviewPrompt(),
        QuickReviewPrompt(),
        # RefactorCodePrompt(),
        # ExtractFunctionPrompt(),
        # OptimizeCodePrompt(),
        DebugErrorPrompt(),
        ExplainCodePrompt(),
        FixBugPrompt(),
        GenerateDocstringPrompt(),
        GenerateReadmePrompt(),
        GenerateTestsPrompt(),
        GenerateAPIDocsPrompt(),
    ]


