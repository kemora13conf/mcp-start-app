"""
Configuration settings for MCP File Manager.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional

class Settings:
    """Configuration settings."""
    
    # Server settings
    SERVER_NAME: str = "mcp-file-manager"
    DEFAULT_TRANSPORT: str = "stdio"
    
    # File operation settings
    MAX_FILE_SIZE_BYTES: int = int(os.getenv("MCP_MAX_FILE_SIZE", 1024 * 1024))  # 1MB
    DEFAULT_ENCODING: str = "utf-8"
    
    # Backup settings
    BACKUP_DIR: Path = Path.home() / ".mcp_backups"
    MAX_EDIT_HISTORY: int = int(os.getenv("MCP_MAX_HISTORY", 100))
    BACKUP_RETENTION_DAYS: int = int(os.getenv("MCP_BACKUP_RETENTION", 30))
    
    # Search settings
    DEFAULT_MAX_SEARCH_RESULTS: int = 1000
    DEFAULT_CONTEXT_LINES: int = 2
    
    # Security settings
    DANGEROUS_COMMANDS: List[str] = ["rm", "del", "format", "sudo", "su", "passwd"]
    COMMAND_TIMEOUT: int = 30
    
    # File type detection
    TEXT_EXTENSIONS: set = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.scss', 
        '.json', '.xml', '.yaml', '.yml', '.md', '.txt', '.log', 
        '.ini', '.cfg', '.conf', '.sh', '.bat', '.sql', '.r', '.php',
        '.rb', '.go', '.rs', '.swift', '.java', '.c', '.cpp', '.h',
        '.cs', '.vue', '.svelte', '.toml', '.dockerfile'
    }
    
    # Exclude patterns for searches
    DEFAULT_EXCLUDE_PATTERNS: List[str] = [
        ".git/*", "node_modules/*", "__pycache__/*", "*.pyc", "*.pyo", 
        ".DS_Store", "Thumbs.db", "*.log", ".env", ".vscode/*", ".idea/*",
        "dist/*", "build/*", "*.egg-info/*", ".pytest_cache/*", 
        "coverage/*", ".coverage", "*.min.js", "*.min.css"
    ]
    
    @classmethod
    def get_backup_dir(cls) -> Path:
        """Get backup directory, creating it if needed."""
        cls.BACKUP_DIR.mkdir(exist_ok=True)
        return cls.BACKUP_DIR
    
    @classmethod
    def load_from_env(cls) -> Dict[str, any]:
        """Load settings from environment variables."""
        return {
            "max_file_size": cls.MAX_FILE_SIZE_BYTES,
            "backup_dir": str(cls.BACKUP_DIR),
            "max_history": cls.MAX_EDIT_HISTORY,
            "backup_retention_days": cls.BACKUP_RETENTION_DAYS,
        }


# Global settings instance
settings = Settings()
