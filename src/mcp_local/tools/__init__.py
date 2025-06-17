"""
Tools module for MCP Local

This module contains all the MCP tools organized by functionality.
"""

from .file_operations import register_file_operations
from .file_editing import register_file_editing_tools
from .search_tools import register_search_tools

__all__ = [
    "register_file_operations",
    "register_file_editing_tools"
    "register_search_tools"
]
