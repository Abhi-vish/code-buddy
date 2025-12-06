import fnmatch
from pathlib import Path
from src.shared import INCLUDE_PATTERN, EXCLUDE_DIRS, BINARY_EXTENSIONS

def should_include_file(filepath: Path) -> bool:
    for part in filepath.parts:
        if part in EXCLUDE_DIRS:
            return False
        if part.startswith(".") and part not in {".env.example",".gitignore", ".dockerignore"}:
            return False
        
    if filepath.suffix.lower() in BINARY_EXTENSIONS:
        return False
    
    if filepath.suffix.lower() in BINARY_EXTENSIONS:
        return False
    
    name = filepath.name
    for pattern in INCLUDE_PATTERN:
        if fnmatch.fnmatch(name, pattern):
            return True    
    return False

def should_exclude_file(dirpath: Path) -> bool:
    name = dirpath.name
    if name in EXCLUDE_DIRS:
        return True
    if name.startswith(".") and name not in {".gitub", ".gitlab"}:
        return True
    return False

def matches_pattern(filepath:Path, pattern:str) -> bool:
    return fnmatch.fnmatch(filepath.name, pattern)