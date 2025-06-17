"""
Advanced file editing tools
"""

import re
import difflib
from typing import Optional
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from ..core import FileOperationBase
from ..services import file_service, backup_service, history_service


class EditFileLinesTool(FileOperationBase):
    """Tool for editing specific lines in a file"""
    
    def __init__(self):
        super().__init__("edit_file_lines", "Replace specific lines in a file with new content")
    
    def execute(self, file_path: str, start_line: int, new_content: str, end_line: Optional[int] = None) -> str:
        try:
            path = self.validate_file_path(file_path)
            if not path.exists():
                return f"File '{file_path}' does not exist"
            
            # Create backup
            backup_path = backup_service.create_backup(str(path))
            
            # Read current content
            content = file_service.read_file(file_path)
            lines = content.splitlines(keepends=True)
            
            total_lines = len(lines)
            start_idx = start_line - 1
            end_idx = end_line if end_line else start_line
            
            if start_idx < 0 or start_idx >= total_lines:
                return f"Invalid line number {start_line}. File has {total_lines} lines"
            
            # Store original content for logging
            original_lines = lines[start_idx:end_idx]
            
            # Replace lines
            new_lines = new_content.splitlines(keepends=True)
            if new_content and not new_content.endswith('\n'):
                if new_lines:
                    new_lines[-1] += '\n'
            
            lines[start_idx:end_idx] = new_lines
            
            # Write back to file
            new_file_content = ''.join(lines)
            file_service.write_file(file_path, new_file_content)
            
            # Log the edit
            history_service.log_edit("edit_lines", str(path), {
                "start_line": start_line,
                "end_line": end_line,
                "original_lines": [line.rstrip() for line in original_lines],
                "new_lines": [line.rstrip() for line in new_lines],
                "backup": backup_path
            })
            
            return f"Successfully edited lines {start_line}-{end_line or start_line} in '{path}'"
            
        except Exception as e:
            return f"Error editing file lines: {str(e)}"


class InsertLinesTool(FileOperationBase):
    """Tool for inserting lines into a file"""
    
    def __init__(self):
        super().__init__("insert_lines", "Insert new lines at a specific position in the file")
    
    def execute(self, file_path: str, line_number: int, content: str) -> str:
        try:
            path = self.validate_file_path(file_path)
            if not path.exists():
                return f"File '{file_path}' does not exist"
            
            backup_path = backup_service.create_backup(str(path))
            
            # Read current content
            file_content = file_service.read_file(file_path)
            lines = file_content.splitlines(keepends=True)
            
            insert_idx = max(0, min(line_number - 1, len(lines)))
            new_lines = content.splitlines(keepends=True)
            
            # Ensure proper line endings
            if content and not content.endswith('\n'):
                if new_lines:
                    new_lines[-1] += '\n'
            
            lines[insert_idx:insert_idx] = new_lines
            
            # Write back to file
            new_file_content = ''.join(lines)
            file_service.write_file(file_path, new_file_content)
            
            history_service.log_edit("insert_lines", str(path), {
                "line_number": line_number,
                "inserted_lines": [line.rstrip() for line in new_lines],
                "backup": backup_path
            })
            
            return f"Successfully inserted {len(new_lines)} lines at line {line_number} in '{path}'"
            
        except Exception as e:
            return f"Error inserting lines: {str(e)}"


class DeleteLinesTool(FileOperationBase):
    """Tool for deleting lines from a file"""
    
    def __init__(self):
        super().__init__("delete_lines", "Delete specific lines from a file")
    
    def execute(self, file_path: str, start_line: int, end_line: Optional[int] = None) -> str:
        try:
            path = self.validate_file_path(file_path)
            if not path.exists():
                return f"File '{file_path}' does not exist"
            
            backup_path = backup_service.create_backup(str(path))
            
            # Read current content
            file_content = file_service.read_file(file_path)
            lines = file_content.splitlines(keepends=True)
            
            total_lines = len(lines)
            start_idx = start_line - 1
            end_idx = end_line if end_line else start_line
            
            if start_idx < 0 or start_idx >= total_lines:
                return f"Invalid line number {start_line}. File has {total_lines} lines"
            
            deleted_lines = lines[start_idx:end_idx]
            del lines[start_idx:end_idx]
            
            # Write back to file
            new_file_content = ''.join(lines)
            file_service.write_file(file_path, new_file_content)
            
            history_service.log_edit("delete_lines", str(path), {
                "start_line": start_line,
                "end_line": end_line,
                "deleted_lines": [line.rstrip() for line in deleted_lines],
                "backup": backup_path
            })
            
            return f"Successfully deleted lines {start_line}-{end_line or start_line} from '{path}'"
            
        except Exception as e:
            return f"Error deleting lines: {str(e)}"


class ReplaceInFileTool(FileOperationBase):
    """Tool for find and replace in a file"""
    
    def __init__(self):
        super().__init__("replace_in_file", "Find and replace text in a file")
    
    def execute(self, file_path: str, search_pattern: str, replace_with: str, use_regex: bool = False) -> str:
        try:
            path = self.validate_file_path(file_path)
            if not path.exists():
                return f"File '{file_path}' does not exist"
            
            backup_path = backup_service.create_backup(str(path))
            
            # Read current content
            content = file_service.read_file(file_path)
            original_content = content
            
            if use_regex:
                try:
                    content = re.sub(search_pattern, replace_with, content)
                    count = len(re.findall(search_pattern, original_content))
                except re.error as e:
                    return f"Invalid regex pattern: {e}"
            else:
                count = content.count(search_pattern)
                content = content.replace(search_pattern, replace_with)
            
            # Write back to file
            file_service.write_file(file_path, content)
            
            history_service.log_edit("replace_in_file", str(path), {
                "search_pattern": search_pattern,
                "replace_with": replace_with,
                "use_regex": use_regex,
                "replacements_made": count,
                "backup": backup_path
            })
            
            return f"Successfully made {count} replacements in '{path}'"
            
        except Exception as e:
            return f"Error replacing in file: {str(e)}"


class GetFileDiffTool(FileOperationBase):
    """Tool for showing file differences"""
    
    def __init__(self):
        super().__init__("get_file_diff", "Show differences between current file and its backup")
    
    def execute(self, file_path: str, backup_file: Optional[str] = None) -> str:
        try:
            path = self.validate_file_path(file_path)
            if not path.exists():
                return f"File '{file_path}' does not exist"
            
            if backup_file:
                backup_path = Path(backup_file).expanduser().resolve()
            else:
                # Find most recent backup
                backup_path_str = backup_service.get_latest_backup(path.name)
                if not backup_path_str:
                    return f"No backups found for '{file_path}'"
                backup_path = Path(backup_path_str)
            
            if not backup_path.exists():
                return f"Backup file '{backup_path}' does not exist"
            
            # Read both files
            current_content = file_service.read_file(file_path)
            backup_content = file_service.read_file(str(backup_path))
            
            current_lines = current_content.splitlines(keepends=True)
            backup_lines = backup_content.splitlines(keepends=True)
            
            diff = list(difflib.unified_diff(
                backup_lines,
                current_lines,
                fromfile=f"{path.name} (backup)",
                tofile=f"{path.name} (current)",
                lineterm=""
            ))
            
            if not diff:
                return "No differences found"
            
            return f"Differences for '{path}':\n\n" + "\n".join(diff)
            
        except Exception as e:
            return f"Error generating diff: {str(e)}"


class GetEditHistoryTool(FileOperationBase):
    """Tool for getting edit history"""
    
    def __init__(self):
        super().__init__("get_edit_history", "Get the history of file edits")
    
    def execute(self, limit: int = 20, file_path: Optional[str] = None) -> str:
        try:
            if file_path:
                entries = history_service.get_file_history(file_path, limit)
                if not entries:
                    return f"No edit history found for '{file_path}'"
                result = f"Edit History for '{file_path}' (last {len(entries)} entries):\n\n"
            else:
                entries = history_service.get_history(limit)
                if not entries:
                    return "No edit history available"
                result = f"Edit History (last {len(entries)} entries):\n\n"
            
            for entry in entries:
                timestamp = entry['timestamp']
                action = entry['action']
                file_path = entry['file']
                details = entry['details']
                
                result += f"{timestamp} - {action}\n"
                result += f"  File: {file_path}\n"
                
                if action == "edit_lines":
                    result += f"  Lines: {details['start_line']}-{details.get('end_line', details['start_line'])}\n"
                elif action == "insert_lines":
                    result += f"  Inserted at line: {details['line_number']}\n"
                elif action == "delete_lines":
                    result += f"  Deleted lines: {details['start_line']}-{details.get('end_line', details['start_line'])}\n"
                elif action == "replace_in_file":
                    result += f"  Replacements: {details['replacements_made']}\n"
                
                result += "\n"
            
            return result
            
        except Exception as e:
            return f"Error getting edit history: {str(e)}"




def register_file_editing_tools(mcp: FastMCP):
    """Register file editing tools with the MCP server"""
    
    edit_tool = EditFileLinesTool()
    insert_tool = InsertLinesTool()
    delete_tool = DeleteLinesTool()
    replace_tool = ReplaceInFileTool()
    diff_tool = GetFileDiffTool()
    history_tool = GetEditHistoryTool()
    
    @mcp.tool()
    def edit_file_lines(file_path: str, start_line: int, new_content: str, end_line: Optional[int] = None) -> str:
        """Replace specific lines in a file with new content"""
        return edit_tool.execute(file_path=file_path, start_line=start_line, 
                               new_content=new_content, end_line=end_line)
    
    @mcp.tool()
    def insert_lines(file_path: str, line_number: int, content: str) -> str:
        """Insert new lines at a specific position in the file"""
        return insert_tool.execute(file_path=file_path, line_number=line_number, content=content)
    
    @mcp.tool()
    def delete_lines(file_path: str, start_line: int, end_line: Optional[int] = None) -> str:
        """Delete specific lines from a file"""
        return delete_tool.execute(file_path=file_path, start_line=start_line, end_line=end_line)
    
    @mcp.tool()
    def replace_in_file(file_path: str, search_pattern: str, replace_with: str, use_regex: bool = False) -> str:
        """Find and replace text in a file"""
        return replace_tool.execute(file_path=file_path, search_pattern=search_pattern,
                                  replace_with=replace_with, use_regex=use_regex)
    
    @mcp.tool()
    def get_file_diff(file_path: str, backup_file: Optional[str] = None) -> str:
        """Show differences between current file and its backup"""
        return diff_tool.execute(file_path=file_path, backup_file=backup_file)
    
    @mcp.tool()
    def get_edit_history(limit: int = 20, file_path: Optional[str] = None) -> str:
        """Get the history of file edits"""
        return history_tool.execute(limit=limit, file_path=file_path)
