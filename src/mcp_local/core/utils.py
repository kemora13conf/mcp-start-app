"""
Core utilities and helper functions
"""

import mimetypes
import fnmatch
from pathlib import Path
from typing import List

from .config import DEFAULT_EXCLUDE_PATTERNS


def should_exclude_file(file_path: Path, exclude_patterns: List[str]) -> bool:
    """Check if file should be excluded based on patterns"""
    rel_path = str(file_path)
    
    for pattern in exclude_patterns:
        if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(file_path.name, pattern):
            return True
        # Check parent directories
        for parent in file_path.parents:
            if fnmatch.fnmatch(str(parent), pattern):
                return True
    return False


def is_text_file(file_path: Path) -> bool:
    """Check if file is likely a text file"""
    try:
        # Check file extension
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type and mime_type.startswith('text'):
            return True
        
        # Check common text extensions
        text_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.scss', 
                          '.json', '.xml', '.yaml', '.yml', '.md', '.txt', '.log', 
                          '.ini', '.cfg', '.conf', '.sh', '.bat', '.sql', '.r', '.php',
                          '.rb', '.go', '.rs', '.swift', '.java', '.c', '.cpp', '.h',
                          '.cs', '.vue', '.svelte', '.toml', '.dockerfile'}
        
        if file_path.suffix.lower() in text_extensions:
            return True
        
        # Try reading first few bytes
        if file_path.stat().st_size > 1024 * 1024:  # Skip files larger than 1MB
            return False
            
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            if b'\0' in chunk:  # Binary file
                return False
        return True
    except:
        return False


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def validate_path(path_str: str) -> Path:
    """Validate and resolve a file path"""
    path = Path(path_str).expanduser().resolve()
    return path


def get_relative_path(file_path: Path, base_path: Path) -> str:
    """Get relative path from base path"""
    try:
        return str(file_path.relative_to(base_path))
    except ValueError:
        return str(file_path)
