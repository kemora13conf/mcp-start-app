"""
Core module for MCP Local

This module contains the foundational classes, utilities, and configuration
for the MCP Local file manager.
"""

from .base import ToolBase, FileOperationBase, SearchBase, ServiceBase
from .config import (
    DEFAULT_EXCLUDE_PATTERNS,
    FILE_TYPE_GROUPS,
    BACKUP_DIR,
    MAX_FILE_SIZE,
    MAX_EDIT_HISTORY_ENTRIES,
    DANGEROUS_COMMANDS,
    COMMAND_TIMEOUT
)
from .exceptions import (
    MCPFileManagerError,
    FileNotFoundError,
    FileAccessError,
    FileSizeError,
    InvalidPathError,
    SearchError,
    BackupError,
    CommandError,
    ValidationError
)
from .utils import (
    should_exclude_file,
    is_text_file,
    format_file_size,
    validate_path,
    get_relative_path
)

__all__ = [
    # Base classes
    "ToolBase",
    "FileOperationBase", 
    "SearchBase",
    "ServiceBase",
    
    # Configuration
    "DEFAULT_EXCLUDE_PATTERNS",
    "FILE_TYPE_GROUPS",
    "BACKUP_DIR",
    "MAX_FILE_SIZE",
    "MAX_EDIT_HISTORY_ENTRIES",
    "DANGEROUS_COMMANDS",
    "COMMAND_TIMEOUT",
    
    # Exceptions
    "MCPFileManagerError",
    "FileNotFoundError",
    "FileAccessError",
    "FileSizeError",
    "InvalidPathError",
    "SearchError",
    "BackupError",
    "CommandError",
    "ValidationError",
    
    # Utilities
    "should_exclude_file",
    "is_text_file",
    "format_file_size",
    "validate_path",
    "get_relative_path"
]
