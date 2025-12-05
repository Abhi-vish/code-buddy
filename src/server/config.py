import os
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class ServerConfig:
    name: str = "coding-agent"
    version: str = "1.0.0"
    project_root: Path = field(default_factory=Path.cwd)
    max_file_size: int = 1024 * 1024
    max_depth: int = 4
    log_level: str = "INFO"
    
    @classmethod
    def from_env(cls) -> "ServerConfig":
        return cls(
            name=os.getenv("MCP_SERVER_NAME", "coding-agent"),
            version=os.getenv("MCP_SERVER_VERSION", "1.0.0"),
            project_root=Path(os.getenv("PROJECT_ROOT", os.getcwd())),
            max_file_size=int(os.getenv("MAX_FILE_SIZE", 1024 * 1024)),
            max_depth=int(os.getenv("MAX_DEPTH", 4)),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )
    
    @classmethod
    def from_dict(cls, data: dict) -> "ServerConfig":
        return cls(
            name=data.get("name", "coding-agent"),
            version=data.get("version", "1.0.0"),
            project_root=Path(data.get("project_root", os.getcwd())),
            max_file_size=data.get("max_file_size", 1024 * 1024),
            max_depth=data.get("max_depth", 4),
            log_level=data.get("log_level", "INFO"),
        )