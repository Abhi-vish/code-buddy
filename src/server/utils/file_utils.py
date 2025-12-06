from pathlib import Path
from src.shared import MAX_FILE_SIZE, FileInfo, FileAccessError
from .mime_types import get_mime_type
from .patterns import should_include_file, should_exclude_file


def read_file(filepath: Path, encoding:str='utf-8') -> str:
    if not filepath.exists():
        raise FileAccessError(f"File '{filepath}' does not exist.")
    
    if not filepath.is_file():
        raise FileAccessError(f"Path '{filepath}' is not a file.")
    
    if filepath.stat().st_size > MAX_FILE_SIZE:
        raise FileAccessError(f"File '{filepath}' exceeds maximum size of {MAX_FILE_SIZE} bytes.")
    
    try:
        return filepath.read_text(encoding=encoding)
    except UnicodeDecodeError as e:
        return filepath.read_text(encoding="latin-1")


def write_file(filepath: Path, content: str, encoding:str="utf-8") -> None:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(content, encoding=encoding)

def get_file_info(filepath: Path, project_root: Path) -> FileInfo:
    stat = filepath.stat()
    rel_path = str(filepath.relative_to(project_root))

    return FileInfo(
        path=rel_path,
        name=filepath.name,
        extension=filepath.suffix,
        size=stat.st_size,
        is_directory=filepath.is_dir(),
        mime_type=get_mime_type(filepath)
    )

def collect_project_files(project_root:Path) -> list[Path]:
    files = []

    for filepath in project_root.rglob("*"):
        if filepath.is_file() and should_include_file(filepath):
            try: 
                if filepath.stat().st_size <= MAX_FILE_SIZE:
                    files.append(filepath)
            except OSError:
                continue
    
    return sorted(files)


def get_directory_tree(directory: Path, max_depth: int= 4) -> list[tuple[Path, int]]:
    result = []

    def traverse(current: Path, depth: int):
        if depth > max_depth:
            return
        
        try:
            entries = sorted(current.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
        except PermissionError:
            return
        
        for entry in entries:
            if entry.is_dir():
                if not should_exclude_file(entry):
                    result.append((entry, depth))
                    traverse(entry, depth + 1)
            else:
                if should_include_file(entry):
                    result.append((entry, depth))
            
    traverse(directory, 0)
    return result

