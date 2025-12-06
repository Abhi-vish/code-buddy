import json
from pathlib import Path
from src.server.utils import read_file
from .base import BaseResource


class ConfigFileResource(BaseResource):
    
    def __init__(self, project_root: Path, config_name: str, filename: str):
        self.project_root = project_root
        self.config_name = config_name
        self.filename = filename
        self.name = config_name
        self.description = f"Configuration: {filename}"
        self._determine_mime_type()
    
    def _determine_mime_type(self):
        if self.filename.endswith((".json",)):
            self.mime_type = "application/json"
        elif self.filename.endswith((".yaml", ".yml")):
            self.mime_type = "text/yaml"
        elif self.filename.endswith((".toml",)):
            self.mime_type = "text/x-toml"
        elif self.filename.endswith((".ini", ".cfg")):
            self.mime_type = "text/plain"
        else:
            self.mime_type = "text/plain"
    
    def get_uri(self) -> str:
        return f"config://{self.config_name}"
    
    async def read(self) -> str:
        filepath = self.project_root / self.filename
        if not filepath.exists():
            return json.dumps({"error": f"Config file not found: {self.filename}"})
        return read_file(filepath)


class ConfigResourceProvider:
    
    CONFIG_FILES = {
        "package": "package.json",
        "pyproject": "pyproject.toml",
        "requirements": "requirements.txt",
        "dockerfile": "Dockerfile",
        "docker-compose": "docker-compose.yml",
        "makefile": "Makefile",
        "gitignore": ".gitignore",
        "env-example": ".env.example",
        "readme": "README.md",
        "cargo": "Cargo.toml",
        "go-mod": "go.mod",
        "tsconfig": "tsconfig.json",
        "eslint": ".eslintrc.json",
        "prettier": ".prettierrc",
    }
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
    
    def list_available(self) -> list[ConfigFileResource]:
        resources = []
        
        for config_name, filename in self.CONFIG_FILES.items():
            filepath = self.project_root / filename
            if filepath.exists():
                resources.append(
                    ConfigFileResource(self.project_root, config_name, filename)
                )
        
        return resources
    
    def get(self, uri: str) -> ConfigFileResource:
        if not uri.startswith("config://"):
            raise ValueError(f"Invalid config URI: {uri}")
        
        config_name = uri.replace("config://", "")
        
        if config_name not in self.CONFIG_FILES:
            raise ValueError(f"Unknown config: {config_name}")
        
        filename = self.CONFIG_FILES[config_name]
        return ConfigFileResource(self.project_root, config_name, filename)


class EnvironmentResource(BaseResource):
    
    name = "Environment Variables"
    description = "Environment variables template"
    mime_type = "text/plain"
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
    
    def get_uri(self) -> str:
        return "config://env"
    
    async def read(self) -> str:
        env_example = self.project_root / ".env.example"
        if env_example.exists():
            return read_file(env_example)
        
        env_file = self.project_root / ".env"
        if env_file.exists():
            content = read_file(env_file)
            lines = []
            for line in content.splitlines():
                if "=" in line and not line.strip().startswith("#"):
                    key = line.split("=")[0]
                    lines.append(f"{key}=<redacted>")
                else:
                    lines.append(line)
            return "\n".join(lines)
        
        return "No environment file found"