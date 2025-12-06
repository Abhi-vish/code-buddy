from pathlib import Path
from .base import BaseTool
from .file_tools import (
    ReadFileTool,
    WriteFileTool,
    EditFileTool,
    DeleteFileTool,
    MoveFileTool,
    CopyFileTool,
)
from .directory_tools import (
    CreateDirectoryTool,
    ListDirectoryTool,
    DeleteDirectoryTool,
    GetTreeTool,
)
from .search_tools import (
    SearchInFilesTool,
    FindReplaceTool,
    FindReplaceAllTool,
)
from .command_tools import (
    RunCommandTool,
    RunPythonTool,
)
from .git_tools import (
    GitTool,
    GitStatusTool,
    GitDiffTool,
    GitLogTool,
)
from .code_tools import (
    AnalyzeCodeTool,
    GetFunctionsTool,
    FormatCodeTool,
    LintCodeTool,
)


def get_all_tools(project_root: Path) -> list[BaseTool]:
    return [
        ReadFileTool(project_root),
        WriteFileTool(project_root),
        EditFileTool(project_root),
        DeleteFileTool(project_root),
        MoveFileTool(project_root),
        CopyFileTool(project_root),
        CreateDirectoryTool(project_root),
        ListDirectoryTool(project_root),
        DeleteDirectoryTool(project_root),
        GetTreeTool(project_root),
        SearchInFilesTool(project_root),
        FindReplaceTool(project_root),
        FindReplaceAllTool(project_root),
        RunCommandTool(project_root),
        RunPythonTool(project_root),
        GitTool(project_root),
        GitStatusTool(project_root),
        GitDiffTool(project_root),
        GitLogTool(project_root),
        AnalyzeCodeTool(project_root),
        GetFunctionsTool(project_root),
        FormatCodeTool(project_root),
        LintCodeTool(project_root),
    ]