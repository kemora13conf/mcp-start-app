"""
Custom exceptions for MCP File Manager
"""


class MCPFileManagerError(Exception):
    """Base exception for MCP File Manager"""
    pass


class FileNotFoundError(MCPFileManagerError):
    """Raised when a file is not found"""
    pass


class FileAccessError(MCPFileManagerError):
    """Raised when file access is denied"""
    pass


class FileSizeError(MCPFileManagerError):
    """Raised when file is too large"""
    pass


class InvalidPathError(MCPFileManagerError):
    """Raised when path is invalid"""
    pass


class SearchError(MCPFileManagerError):
    """Raised when search operation fails"""
    pass


class BackupError(MCPFileManagerError):
    """Raised when backup operation fails"""
    pass


class CommandError(MCPFileManagerError):
    """Raised when command execution fails"""
    pass


class ValidationError(MCPFileManagerError):
    """Raised when validation fails"""
    pass
