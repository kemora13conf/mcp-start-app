"""
Base classes and interfaces for MCP File Manager
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pathlib import Path


class ToolBase(ABC):
    """Base class for all MCP tools"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    def execute(self, **kwargs) -> str:
        """Execute the tool with given parameters"""
        pass
    
    def validate_params(self, **kwargs) -> bool:
        """Validate tool parameters"""
        return True


class FileOperationBase(ToolBase):
    """Base class for file operations"""
    
    def __init__(self, name: str, description: str):
        super().__init__(name, description)
    
    def validate_file_path(self, file_path: str) -> Path:
        """Validate and return resolved file path"""
        from .utils import validate_path
        from .exceptions import InvalidPathError
        
        try:
            path = validate_path(file_path)
            return path
        except Exception as e:
            raise InvalidPathError(f"Invalid file path '{file_path}': {e}")
    
    def check_file_exists(self, path: Path) -> bool:
        """Check if file exists"""
        return path.exists()
    
    def check_file_size(self, path: Path, max_size: int) -> bool:
        """Check if file size is within limits"""
        from .config import MAX_FILE_SIZE
        
        if not path.exists():
            return True
        
        return path.stat().st_size <= max_size


class SearchBase(ToolBase):
    """Base class for search operations"""
    
    def __init__(self, name: str, description: str):
        super().__init__(name, description)
    
    def prepare_search_patterns(self, include_patterns: Optional[str], 
                               exclude_patterns: Optional[str], 
                               file_types: str) -> tuple:
        """Prepare include and exclude patterns for search"""
        from .config import FILE_TYPE_GROUPS, DEFAULT_EXCLUDE_PATTERNS
        
        # Prepare include patterns
        if include_patterns:
            include_list = [p.strip() for p in include_patterns.split(',')]
        elif file_types in FILE_TYPE_GROUPS:
            include_list = FILE_TYPE_GROUPS[file_types]
        else:
            include_list = [p.strip() for p in file_types.split(',')]
        
        # Prepare exclude patterns
        exclude_list = DEFAULT_EXCLUDE_PATTERNS.copy()
        if exclude_patterns:
            exclude_list.extend([p.strip() for p in exclude_patterns.split(',')])
        
        return include_list, exclude_list


class ServiceBase(ABC):
    """Base class for services"""
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the service"""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup resources"""
        pass
