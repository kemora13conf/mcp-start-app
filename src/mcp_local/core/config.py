"""
Configuration settings and constants for MCP Local
"""

from pathlib import Path
from typing import Dict, List

# Default exclude patterns (like VSCode)
DEFAULT_EXCLUDE_PATTERNS = [
    ".git/*", "node_modules/*", "__pycache__/*", "*.pyc", "*.pyo", 
    ".DS_Store", "Thumbs.db", "*.log", ".env", ".vscode/*", ".idea/*",
    "dist/*", "build/*", "*.egg-info/*", ".pytest_cache/*", 
    "coverage/*", ".coverage", "*.min.js", "*.min.css"
]

# Common file type groups
FILE_TYPE_GROUPS = {
    "code": ["*.py", "*.js", "*.ts", "*.jsx", "*.tsx", "*.java", "*.c", "*.cpp", "*.h", "*.cs", "*.php", "*.rb", "*.go", "*.rs", "*.swift"],
    "web": ["*.html", "*.css", "*.scss", "*.sass", "*.less", "*.vue", "*.svelte"],
    "config": ["*.json", "*.yaml", "*.yml", "*.toml", "*.ini", "*.cfg", "*.conf"],
    "docs": ["*.md", "*.txt", "*.rst", "*.doc", "*.docx", "*.pdf"],
    "data": ["*.csv", "*.xlsx", "*.xml", "*.sql"],
    "all": ["*"]
}

# Backup configuration
BACKUP_DIR = Path.home() / ".mcp_local_backups"
BACKUP_DIR.mkdir(exist_ok=True)

# File size limits
MAX_FILE_SIZE = 1024 * 1024  # 1MB

# History configuration
MAX_EDIT_HISTORY_ENTRIES = 100

# Security settings
DANGEROUS_COMMANDS = ['rm', 'del', 'format', 'sudo', 'su', 'passwd']

# Timeout settings
COMMAND_TIMEOUT = 30  # seconds
