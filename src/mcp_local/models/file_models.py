"""
Data models for file operations.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any


@dataclass
class FileInfo:
    """Information about a file."""
    path: Path
    name: str
    size: int
    modified: datetime
    is_directory: bool
    is_text: bool
    mime_type: Optional[str] = None
    
    @property
    def relative_path(self) -> str:
        """Get relative path as string."""
        return str(self.path)
    
    @property
    def extension(self) -> str:
        """Get file extension."""
        return self.path.suffix.lower()


@dataclass
class EditRecord:
    """Record of a file edit operation."""
    timestamp: datetime
    action: str
    file_path: str
    details: Dict[str, Any]
    backup_path: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "action": self.action,
            "file": self.file_path,
            "details": self.details,
            "backup": self.backup_path
        }


@dataclass
class SearchMatch:
    """A single search match result."""
    file_path: str
    line_number: int
    column: int
    line_content: str
    highlighted_line: str
    context_lines: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "file": self.file_path,
            "line_number": self.line_number,
            "column": self.column,
            "line_content": self.line_content,
            "highlighted_line": self.highlighted_line,
            "context": self.context_lines
        }


@dataclass
class SearchResults:
    """Collection of search results."""
    search_term: str
    matches: List[SearchMatch]
    files_searched: int
    files_with_matches: int
    search_path: str
    options: Dict[str, Any]
    
    @property
    def total_matches(self) -> int:
        """Total number of matches."""
        return len(self.matches)
    
    def group_by_file(self) -> Dict[str, List[SearchMatch]]:
        """Group matches by file."""
        grouped = {}
        for match in self.matches:
            if match.file_path not in grouped:
                grouped[match.file_path] = []
            grouped[match.file_path].append(match)
        return grouped


@dataclass
class ReplaceResult:
    """Result of a find and replace operation."""
    file_path: str
    replacements_made: int
    original_size: int
    new_size: int
    backup_path: Optional[str] = None
    error: Optional[str] = None
    
    @property
    def success(self) -> bool:
        """Whether the replacement was successful."""
        return self.error is None
