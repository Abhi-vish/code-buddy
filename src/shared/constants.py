from pathlib import Path

DEFAULT_PROJECT_ROOT = Path.cwd()

MAX_FILE_SIZE = 1024 * 1024

INCLUDE_PATTERN = [
    "*.py", "*.js", "*.ts","*.jsx", ".tsx",
    "*.html", ".css"
]

EXCLUDE_DIRS = [
    "__pycache__",
    ".git",
    "node_modules",
    "dist",
    "build",
    ".env",
    ".vscode",
    ".venv"
]

BINARY_EXTENSIONS = {
    ".pyc",".pyo", ".exe", ".dll", ".so", ".dylib",
}
