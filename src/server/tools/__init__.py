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


def get_all_tools(project_root: Path, allow_external: bool = True) -> list[BaseTool]:
    return [
        ReadFileTool(project_root, allow_external),
        WriteFileTool(project_root, allow_external),
        EditFileTool(project_root, allow_external),
        DeleteFileTool(project_root, allow_external),
        MoveFileTool(project_root, allow_external),
        CopyFileTool(project_root, allow_external),
        CreateDirectoryTool(project_root, allow_external),
        ListDirectoryTool(project_root, allow_external),
        DeleteDirectoryTool(project_root, allow_external),
        GetTreeTool(project_root, allow_external),
        SearchInFilesTool(project_root, allow_external),
        FindReplaceTool(project_root, allow_external),
        FindReplaceAllTool(project_root, allow_external),
        RunCommandTool(project_root, allow_external),
        RunPythonTool(project_root, allow_external),
        GitTool(project_root, allow_external),
        GitStatusTool(project_root, allow_external),
        GitDiffTool(project_root, allow_external),
        GitLogTool(project_root, allow_external),
        AnalyzeCodeTool(project_root, allow_external),
        GetFunctionsTool(project_root, allow_external),
        FormatCodeTool(project_root, allow_external),
        LintCodeTool(project_root, allow_external),
    ]