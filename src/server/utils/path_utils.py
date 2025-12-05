from pathlib import Path
from src.shared import PathSecurityError


class PathValidator:
    def __init__(self, project_root: Path, allow_external: bool = True):
        self.project_root = project_root.resolve()
        self.allow_external = allow_external

    def validate(self, filepath: str | Path) -> Path:
        if isinstance(filepath, str):
            filepath = Path(filepath)
        
        if filepath.is_absolute():
            full_path = filepath.resolve()
            
            # If external paths are allowed, just validate the path exists or can be created
            if self.allow_external:
                return full_path
            
            # Otherwise, check if it's within project root
            try:
                full_path.relative_to(self.project_root)
            except ValueError:
                raise PathSecurityError(f"Access to path '{full_path}' is outside the project root '{self.project_root}'")
        else:
            # Relative paths are always resolved against project root
            full_path = (self.project_root / filepath).resolve()
        
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