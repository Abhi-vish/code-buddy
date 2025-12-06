from pathlib import Path

MIME_TYPES = {
    ".py": "text/x-python",
    ".js": "application/javascript",
    ".ts": "application/typescript",
    ".jsx": "text/jsx",
    ".tsx": "text/tsx",
    ".html": "text/html",
    ".css": "text/css",
    ".json": "application/json",
    ".xml": "application/xml",
}

def get_mime_type(filepath: str) -> str:
    path = Path(filepath)
    ext = path.suffix.lower()
    return MIME_TYPES.get(ext, "text/plain")