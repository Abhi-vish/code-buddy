from dataclasses import dataclass
from typing import Any
from enum import Enum


class ToolResultStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"

@dataclass
class ToolResult:
    status: ToolResultStatus
    content: str
    data: Any | None = None

@dataclass
class FileInfo:
    path: str
    name: str
    extension: str
    size: int
    is_directory: bool
    mime_type: str 

@dataclass
class SearchMatch:
    file_path: str
    line_number: int
    line_content: str
    match_start: int
    match_end: int

@dataclass
class ProjectSummary:
    root_path: str
    total_files: int
    total_directories: int
    total_lines: int
    files_by_extension: dict[str, int]
    main_directories: list[str]

    