"""
Basic file operation tools
"""

from typing import Optional
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from ..core import FileOperationBase
from ..core.exceptions import FileNotFoundError, FileAccessError
from ..services import file_service, backup_service, history_service


class ListFilesTool(FileOperationBase):
    """Tool for listing directory contents"""
    
    def __init__(self):
        super().__init__("list_files", "List files and directories in the specified path")
    
    def execute(self, directory: str = ".", show_hidden: bool = False) -> str:
        try:
            items = file_service.list_directory(directory, show_hidden, include_size=True)
            
            if not items:
                return f"Directory '{directory}' is empty"
            
            result = f"Contents of '{directory}':\n"
            for item in items:
                icon = "📁" if item["is_dir"] else "📄"
                size_info = f" ({item.get('size_formatted', '')})" if item.get('size_formatted') else ""
                result += f"{icon} {item['name']}{size_info}\n"
            
            return result
            
        except Exception as e:
            return f"Error: {str(e)}"


class ReadFileTool(FileOperationBase):
    """Tool for reading file contents"""
    
    def __init__(self):
        super().__init__("read_file", "Read the contents of a text file")
    
    def execute(self, file_path: str) -> str:
        try:
            content = file_service.read_file(file_path)
            path = self.validate_file_path(file_path)
            return f"Contents of '{path}':\n\n{content}"
            
        except Exception as e:
            return f"Error reading file: {str(e)}"


class WriteFileTool(FileOperationBase):
    """Tool for writing file contents"""
    
    def __init__(self):
        super().__init__("write_file", "Write content to a file")
    
    def execute(self, file_path: str, content: str) -> str:
        try:
            path = self.validate_file_path(file_path)
            
            # Create backup if file exists
            backup_path = ""
            if path.exists():
                backup_path = backup_service.create_backup(str(path))
            
            # Write the file
            file_service.write_file(file_path, content)
            
            # Log the edit
            history_service.log_edit("write_file", str(path), {
                "content_length": len(content),
                "backup": backup_path
            })
            
            return f"Successfully wrote {len(content)} characters to '{path}'"
            
        except Exception as e:
            return f"Error writing file: {str(e)}"


class GetFileLinesTool(FileOperationBase):
    """Tool for getting specific lines from a file"""
    
    def __init__(self):
        super().__init__("get_file_lines", "Get specific lines from a file (1-indexed)")
    
    def execute(self, file_path: str, start_line: int = 1, end_line: Optional[int] = None) -> str:
        try:
            path = self.validate_file_path(file_path)
            if not path.exists():
                return f"File '{file_path}' does not exist"
            
            content = file_service.read_file(file_path)
            lines = content.splitlines()
            
            total_lines = len(lines)
            start_idx = max(0, start_line - 1)
            end_idx = min(total_lines, end_line) if end_line else total_lines
            
            if start_idx >= total_lines:
                return f"Start line {start_line} exceeds file length ({total_lines} lines)"
            
            selected_lines = lines[start_idx:end_idx]
            result = f"Lines {start_line}-{start_idx + len(selected_lines)} of '{path}':\n\n"
            
            for i, line in enumerate(selected_lines, start=start_line):
                result += f"{i:4d}: {line}\n"
            
            return result
            
        except Exception as e:
            return f"Error reading file lines: {str(e)}"


class GetFileInfoTool(FileOperationBase):
    """Tool for getting file information"""
    
    def __init__(self):
        super().__init__("get_file_info", "Get detailed information about a file or directory")
    
    def execute(self, file_path: str) -> str:
        try:
            info = file_service.get_file_info(file_path)
            
            result = f"Information for '{info['path']}':\n"
            result += f"  Name: {info['name']}\n"
            result += f"  Size: {info['size_formatted']} ({info['size']} bytes)\n"
            result += f"  Type: {'File' if info['is_file'] else 'Directory' if info['is_dir'] else 'Other'}\n"
            result += f"  Extension: {info['extension'] or 'None'}\n"
            result += f"  Permissions: {info['permissions']}\n"
            result += f"  Parent: {info['parent']}\n"
            
            import datetime
            result += f"  Modified: {datetime.datetime.fromtimestamp(info['modified_time']).strftime('%Y-%m-%d %H:%M:%S')}\n"
            result += f"  Created: {datetime.datetime.fromtimestamp(info['created_time']).strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            if info['is_symlink']:
                result += "  Type: Symbolic Link\n"
            
            return result
            
        except Exception as e:
            return f"Error getting file info: {str(e)}"


def register_file_operations(mcp: FastMCP):
    """Register file operation tools with the MCP server"""
    
    list_tool = ListFilesTool()
    read_tool = ReadFileTool()
    write_tool = WriteFileTool()
    lines_tool = GetFileLinesTool()
    info_tool = GetFileInfoTool()
    
    @mcp.tool()
    def list_files(directory: str = ".", show_hidden: bool = False) -> str:
        """List files and directories in the specified path"""
        return list_tool.execute(directory=directory, show_hidden=show_hidden)
    
    @mcp.tool()
    def read_file(file_path: str) -> str:
        """Read the contents of a text file"""
        return read_tool.execute(file_path=file_path)
    
    @mcp.tool()
    def write_file(file_path: str, content: str) -> str:
        """Write content to a file"""
        return write_tool.execute(file_path=file_path, content=content)
    
    @mcp.tool()
    def get_file_lines(file_path: str, start_line: int = 1, end_line: Optional[int] = None) -> str:
        """Get specific lines from a file (1-indexed)"""
        return lines_tool.execute(file_path=file_path, start_line=start_line, end_line=end_line)
    
    @mcp.tool()
    def get_file_info(file_path: str) -> str:
        """Get detailed information about a file or directory"""
        return info_tool.execute(file_path=file_path)

