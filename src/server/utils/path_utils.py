from pathlib import Path
from fnmatch import fnmatch
from src.shared import PathSecurityError


class PathValidator:
    SENSITIVE_PATTERNS = [
        "*.env",
        ".env*",
        "*.key",
        "*.pem",
        "*secret*",
        "*credential*",
        "*password*",
        ".ssh/*",
        ".aws/*",
        ".config/*"
    ]

    def __init__(self, project_root: Path, allow_external: bool = True):
        self.project_root = project_root.resolve()
        self.allow_external = allow_external

    def _is_sensitive_file(self, filepath: Path) -> bool:
        """Check if the file matches any sensitive pattern."""
        filepath_str = str(filepath)
        filename = filepath.name
        
        for pattern in self.SENSITIVE_PATTERNS:
            # Check both full path and just filename
            if fnmatch(filename, pattern) or fnmatch(filepath_str, pattern):
                return True
            
            # Check if path contains pattern directory (e.g., .ssh/)
            if '/' in pattern:
                pattern_dir = pattern.rstrip('/*')
                if pattern_dir in filepath.parts:
                    return True
        
        return False

    def validate(self, filepath: str | Path) -> Path:
        if isinstance(filepath, str):
            filepath = Path(filepath)
        
        if filepath.is_absolute():
            full_path = filepath.resolve()
            
            # Check for sensitive files first
            if self._is_sensitive_file(full_path):
                raise PathSecurityError(
                    f"""Access denied: '{full_path}' matches sensitive file pattern. 
                    Files like .env, *.key, *.pem, and credential files are blocked for security."""
                )
            
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
            
            # Check for sensitive files
            if self._is_sensitive_file(full_path):
                raise PathSecurityError(
                    f"Access denied: '{full_path}' matches sensitive file pattern. "
                    f"Files like .env, *.key, *.pem, and credential files are blocked for security."
                )
        
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