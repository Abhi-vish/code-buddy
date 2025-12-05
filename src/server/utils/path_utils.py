from pathlib import Path
from src.shared import PathSecurityError


class PathValidator:
    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()

    def validate(self, filepath: str | Path) -> Path:
        if isinstance(filepath, str):
            filepath = Path(filepath)
        
        if filepath.is_absolute():
            full_path = filepath.resolve()
        else:
            full_path = (self.project_root / filepath).resolve()
        
        try:
            full_path.relative_to(self.project_root)
        except ValueError:
            raise PathSecurityError(f"Access to path '{full_path}' is outside the project root '{self.project_root}'")
        
        return full_path
    
    def get_relative(self, filepath: Path) -> Path:
        try:
            return str(filepath.relative_to(self.project_root))
        except ValueError:
            return str(filepath)
        
    def is_safe(self, filepath: str | Path) -> bool:
        try:
            self.validate(filepath)
            return True
        except PathSecurityError:
            return False