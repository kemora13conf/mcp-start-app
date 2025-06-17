"""
Constants and configuration for the MCP File Manager.
"""

from pathlib import Path
from typing import List, Dict

# Default exclude patterns (like VSCode)
DEFAULT_EXCLUDE_PATTERNS: List[str] = [
    ".git/*", "node_modules/*", "__pycache__/*", "*.pyc", "*.pyo", 
    ".DS_Store", "Thumbs.db", "*.log", ".env", ".vscode/*", ".idea/*",
    "dist/*", "build/*", "*.egg-info/*", ".pytest_cache/*", 
    "coverage/*", ".coverage", "*.min.js", "*.min.css"
]

# Common file type groups
FILE_TYPE_GROUPS: Dict[str, List[str]] = {
    "code": ["*.py", "*.js", "*.ts", "*.jsx", "*.tsx", "*.java", "*.c", "*.cpp", "*.h", "*.cs", "*.php", "*.rb", "*.go", "*.rs", "*.swift"],
    "web": ["*.html", "*.css", "*.scss", "*.sass", "*.less", "*.vue", "*.svelte"],
    "config": ["*.json", "*.yaml", "*.yml", "*.toml", "*.ini", "*.cfg", "*.conf"],
    "docs": ["*.md", "*.txt", "*.rst", "*.doc", "*.docx", "*.pdf"],
    "data": ["*.csv", "*.xlsx", "*.xml", "*.sql"],
    "all": ["*"]
}

# Common text file extensions
TEXT_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.scss', 
    '.json', '.xml', '.yaml', '.yml', '.md', '.txt', '.log', 
    '.ini', '.cfg', '.conf', '.sh', '.bat', '.sql', '.r', '.php',
    '.rb', '.go', '.rs', '.swift', '.java', '.c', '.cpp', '.h',
    '.cs', '.vue', '.svelte', '.toml', '.dockerfile'
}

# File size limits
MAX_FILE_SIZE_BYTES = 1024 * 1024  # 1MB

# Backup configuration
BACKUP_DIR = Path.home() / ".mcp_backups"
BACKUP_DIR.mkdir(exist_ok=True)

# History configuration
MAX_EDIT_HISTORY = 100

# Formatters mapping
FORMATTERS = {
    'python': 'black',
    'javascript': 'prettier',
    'typescript': 'prettier',
    'json': 'prettier',
    'html': 'prettier',
    'css': 'prettier'
}

# Language detection mapping
LANGUAGE_MAP = {
    '.py': 'python',
    '.js': 'javascript',
    '.ts': 'typescript',
    '.json': 'json',
    '.html': 'html',
    '.css': 'css',
    '.java': 'java',
    '.cpp': 'cpp',
    '.c': 'c'
}
