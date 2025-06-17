# enhanced_app.py
from mcp.server.fastmcp import FastMCP
import os
import subprocess
import platform
import psutil
from pathlib import Path
import json
import datetime
import shutil
import re
from typing import List, Dict, Optional, Tuple
import difflib

# Create the MCP server using FastMCP
mcp = FastMCP("enhanced-local-server")

# Global variable to store edit history
EDIT_HISTORY = []
BACKUP_DIR = Path.home() / ".mcp_backups"
BACKUP_DIR.mkdir(exist_ok=True)

def log_edit(action: str, file_path: str, details: dict):
    """Log file editing actions"""
    timestamp = datetime.datetime.now().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "action": action,
        "file": file_path,
        "details": details
    }
    EDIT_HISTORY.append(log_entry)
    
    # Keep only last 100 entries
    if len(EDIT_HISTORY) > 100:
        EDIT_HISTORY.pop(0)

def create_backup(file_path: str) -> str:
    """Create a backup of the file before editing"""
    try:
        path = Path(file_path).expanduser().resolve()
        if not path.exists():
            return ""
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{path.name}_{timestamp}.backup"
        backup_path = BACKUP_DIR / backup_name
        
        shutil.copy2(path, backup_path)
        return str(backup_path)
    except Exception:
        return ""

# Original functions (keeping them)
@mcp.tool()
def get_local_data(query: str) -> str:
    """Get data from local system"""
    result = f"Local data for query: '{query}'"
    return result

@mcp.tool()
def list_files(directory: str = ".", show_hidden: bool = False) -> str:
    """List files and directories in the specified path"""
    try:
        path = Path(directory).expanduser().resolve()
        if not path.exists():
            return f"Directory '{directory}' does not exist"
        
        items = []
        for item in path.iterdir():
            if not show_hidden and item.name.startswith('.'):
                continue
            item_type = "📁" if item.is_dir() else "📄"
            size = f" ({item.stat().st_size} bytes)" if item.is_file() else ""
            items.append(f"{item_type} {item.name}{size}")
        
        return f"Contents of '{path}':\n" + "\n".join(sorted(items))
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def read_file(file_path: str) -> str:
    """Read the contents of a text file"""
    try:
        path = Path(file_path).expanduser().resolve()
        if not path.exists():
            return f"File '{file_path}' does not exist"
        
        if path.stat().st_size > 1024 * 1024:  # 1MB limit
            return f"File too large (>1MB). Size: {path.stat().st_size} bytes"
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return f"Contents of '{path}':\n\n{content}"
    except Exception as e:
        return f"Error reading file: {str(e)}"

@mcp.tool()
def write_file(file_path: str, content: str) -> str:
    """Write content to a file"""
    try:
        path = Path(file_path).expanduser().resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create backup if file exists
        backup_path = create_backup(str(path)) if path.exists() else ""
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        log_edit("write_file", str(path), {
            "content_length": len(content),
            "backup": backup_path
        })
        
        return f"Successfully wrote {len(content)} characters to '{path}'"
    except Exception as e:
        return f"Error writing file: {str(e)}"

# NEW ADVANCED EDITING FUNCTIONS

@mcp.tool()
def get_file_lines(file_path: str, start_line: int = 1, end_line: Optional[int] = None) -> str:
    """Get specific lines from a file (1-indexed)"""
    try:
        path = Path(file_path).expanduser().resolve()
        if not path.exists():
            return f"File '{file_path}' does not exist"
        
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        total_lines = len(lines)
        start_idx = max(0, start_line - 1)
        end_idx = min(total_lines, end_line) if end_line else total_lines
        
        if start_idx >= total_lines:
            return f"Start line {start_line} exceeds file length ({total_lines} lines)"
        
        selected_lines = lines[start_idx:end_idx]
        result = f"Lines {start_line}-{start_idx + len(selected_lines)} of '{path}':\n\n"
        
        for i, line in enumerate(selected_lines, start=start_line):
            result += f"{i:4d}: {line.rstrip()}\n"
        
        return result
    except Exception as e:
        return f"Error reading file lines: {str(e)}"

@mcp.tool()
def edit_file_lines(file_path: str, start_line: int, new_content: str, end_line: Optional[int] = None) -> str:
    """Replace specific lines in a file with new content"""
    try:
        path = Path(file_path).expanduser().resolve()
        if not path.exists():
            return f"File '{file_path}' does not exist"
        
        # Create backup
        backup_path = create_backup(str(path))
        
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        total_lines = len(lines)
        start_idx = start_line - 1
        end_idx = end_line if end_line else start_line
        
        if start_idx < 0 or start_idx >= total_lines:
            return f"Invalid line number {start_line}. File has {total_lines} lines"
        
        # Store original content for logging
        original_lines = lines[start_idx:end_idx]
        
        # Replace lines
        new_lines = new_content.split('\n')
        if new_content and not new_content.endswith('\n'):
            new_lines = [line + '\n' for line in new_lines[:-1]] + [new_lines[-1]]
        else:
            new_lines = [line + '\n' for line in new_lines if line or new_lines[-1]]
        
        lines[start_idx:end_idx] = new_lines
        
        # Write back to file
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        log_edit("edit_lines", str(path), {
            "start_line": start_line,
            "end_line": end_line,
            "original_lines": [line.rstrip() for line in original_lines],
            "new_lines": [line.rstrip() for line in new_lines],
            "backup": backup_path
        })
        
        return f"Successfully edited lines {start_line}-{end_line or start_line} in '{path}'"
    except Exception as e:
        return f"Error editing file lines: {str(e)}"

@mcp.tool()
def insert_lines(file_path: str, line_number: int, content: str) -> str:
    """Insert new lines at a specific position in the file"""
    try:
        path = Path(file_path).expanduser().resolve()
        if not path.exists():
            return f"File '{file_path}' does not exist"
        
        backup_path = create_backup(str(path))
        
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        insert_idx = max(0, min(line_number - 1, len(lines)))
        new_lines = content.split('\n')
        
        # Ensure proper line endings
        new_lines = [line + '\n' for line in new_lines if line.strip() or len(new_lines) == 1]
        
        lines[insert_idx:insert_idx] = new_lines
        
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        log_edit("insert_lines", str(path), {
            "line_number": line_number,
            "inserted_lines": [line.rstrip() for line in new_lines],
            "backup": backup_path
        })
        
        return f"Successfully inserted {len(new_lines)} lines at line {line_number} in '{path}'"
    except Exception as e:
        return f"Error inserting lines: {str(e)}"

@mcp.tool()
def delete_lines(file_path: str, start_line: int, end_line: Optional[int] = None) -> str:
    """Delete specific lines from a file"""
    try:
        path = Path(file_path).expanduser().resolve()
        if not path.exists():
            return f"File '{file_path}' does not exist"
        
        backup_path = create_backup(str(path))
        
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        total_lines = len(lines)
        start_idx = start_line - 1
        end_idx = end_line if end_line else start_line
        
        if start_idx < 0 or start_idx >= total_lines:
            return f"Invalid line number {start_line}. File has {total_lines} lines"
        
        deleted_lines = lines[start_idx:end_idx]
        del lines[start_idx:end_idx]
        
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        log_edit("delete_lines", str(path), {
            "start_line": start_line,
            "end_line": end_line,
            "deleted_lines": [line.rstrip() for line in deleted_lines],
            "backup": backup_path
        })
        
        return f"Successfully deleted lines {start_line}-{end_line or start_line} from '{path}'"
    except Exception as e:
        return f"Error deleting lines: {str(e)}"

@mcp.tool()
def replace_in_file(file_path: str, search_pattern: str, replace_with: str, use_regex: bool = False) -> str:
    """Find and replace text in a file"""
    try:
        path = Path(file_path).expanduser().resolve()
        if not path.exists():
            return f"File '{file_path}' does not exist"
        
        backup_path = create_backup(str(path))
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        if use_regex:
            content = re.sub(search_pattern, replace_with, content)
            count = len(re.findall(search_pattern, original_content))
        else:
            count = content.count(search_pattern)
            content = content.replace(search_pattern, replace_with)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        log_edit("replace_in_file", str(path), {
            "search_pattern": search_pattern,
            "replace_with": replace_with,
            "use_regex": use_regex,
            "replacements_made": count,
            "backup": backup_path
        })
        
        return f"Successfully made {count} replacements in '{path}'"
    except Exception as e:
        return f"Error replacing in file: {str(e)}"

@mcp.tool()
def search_in_files(search_pattern: str, directory: str = ".", file_pattern: str = "*", use_regex: bool = False) -> str:
    """Search for text patterns across multiple files"""
    try:
        path = Path(directory).expanduser().resolve()
        if not path.exists():
            return f"Directory '{directory}' does not exist"
        
        import fnmatch
        matches = []
        
        for file_path in path.rglob(file_pattern):
            if file_path.is_file():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if use_regex:
                        found = re.findall(search_pattern, content, re.MULTILINE)
                        if found:
                            lines = content.split('\n')
                            for i, line in enumerate(lines, 1):
                                if re.search(search_pattern, line):
                                    matches.append(f"{file_path}:{i}: {line.strip()}")
                    else:
                        if search_pattern in content:
                            lines = content.split('\n')
                            for i, line in enumerate(lines, 1):
                                if search_pattern in line:
                                    matches.append(f"{file_path}:{i}: {line.strip()}")
                except:
                    continue
        
        if not matches:
            return f"No matches found for '{search_pattern}' in {directory}"
        
        result = f"Found {len(matches)} matches for '{search_pattern}':\n\n"
        result += "\n".join(matches[:50])  # Limit to 50 results
        
        if len(matches) > 50:
            result += f"\n\n... and {len(matches) - 50} more matches"
        
        return result
    except Exception as e:
        return f"Error searching files: {str(e)}"

@mcp.tool()
def get_file_diff(file_path: str, backup_file: Optional[str] = None) -> str:
    """Show differences between current file and its backup"""
    try:
        path = Path(file_path).expanduser().resolve()
        if not path.exists():
            return f"File '{file_path}' does not exist"
        
        if backup_file:
            backup_path = Path(backup_file).expanduser().resolve()
        else:
            # Find most recent backup
            backups = list(BACKUP_DIR.glob(f"{path.name}_*.backup"))
            if not backups:
                return f"No backups found for '{file_path}'"
            backup_path = max(backups, key=lambda x: x.stat().st_mtime)
        
        if not backup_path.exists():
            return f"Backup file '{backup_path}' does not exist"
        
        with open(path, 'r', encoding='utf-8') as f:
            current_lines = f.readlines()
        
        with open(backup_path, 'r', encoding='utf-8') as f:
            backup_lines = f.readlines()
        
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

@mcp.tool()
def get_edit_history(limit: int = 20) -> str:
    """Get the history of file edits"""
    try:
        if not EDIT_HISTORY:
            return "No edit history available"
        
        result = f"Edit History (last {min(limit, len(EDIT_HISTORY))} entries):\n\n"
        
        for entry in EDIT_HISTORY[-limit:]:
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

@mcp.tool()
def format_code(file_path: str, language: str = "auto") -> str:
    """Format code in a file (requires appropriate formatters installed)"""
    try:
        path = Path(file_path).expanduser().resolve()
        if not path.exists():
            return f"File '{file_path}' does not exist"
        
        # Auto-detect language from extension
        if language == "auto":
            ext = path.suffix.lower()
            lang_map = {
                '.py': 'python',
                '.js': 'javascript',
                '.ts': 'typescript',
                '.json': 'json',
                '.html': 'html',
                '.css': 'css',
                '.java': 'java',
                '.cpp': 'cpp',
                '.c': 'c'
            }
            language = lang_map.get(ext, 'unknown')
        
        backup_path = create_backup(str(path))
        
        # Try to format based on language
        formatters = {
            'python': 'black',
            'javascript': 'prettier',
            'typescript': 'prettier',
            'json': 'prettier',
            'html': 'prettier',
            'css': 'prettier'
        }
        
        formatter = formatters.get(language)
        if not formatter:
            return f"No formatter available for language: {language}"
        
        # Check if formatter is installed
        try:
            result = subprocess.run([formatter, '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                return f"Formatter '{formatter}' not installed"
        except FileNotFoundError:
            return f"Formatter '{formatter}' not found in PATH"
        
        # Format the file
        if formatter == 'black':
            cmd = ['black', str(path)]
        elif formatter == 'prettier':
            cmd = ['prettier', '--write', str(path)]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            log_edit("format_code", str(path), {
                "language": language,
                "formatter": formatter,
                "backup": backup_path
            })
            return f"Successfully formatted {language} code in '{path}'"
        else:
            return f"Formatting failed: {result.stderr}"
            
    except Exception as e:
        return f"Error formatting code: {str(e)}"

@mcp.tool()
def validate_syntax(file_path: str) -> str:
    """Check syntax of a code file"""
    try:
        path = Path(file_path).expanduser().resolve()
        if not path.exists():
            return f"File '{file_path}' does not exist"
        
        ext = path.suffix.lower()
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if ext == '.py':
            import ast
            try:
                ast.parse(content)
                return f"✅ Python syntax is valid in '{path}'"
            except SyntaxError as e:
                return f"❌ Python syntax error in '{path}' at line {e.lineno}: {e.msg}"
        
        elif ext in ['.js', '.ts']:
            # Try Node.js syntax check
            try:
                result = subprocess.run(['node', '--check', str(path)], capture_output=True, text=True)
                if result.returncode == 0:
                    return f"✅ JavaScript/TypeScript syntax is valid in '{path}'"
                else:
                    return f"❌ JavaScript/TypeScript syntax error in '{path}':\n{result.stderr}"
            except FileNotFoundError:
                return "Node.js not found - cannot validate JavaScript/TypeScript syntax"
        
        elif ext == '.json':
            try:
                json.loads(content)
                return f"✅ JSON syntax is valid in '{path}'"
            except json.JSONDecodeError as e:
                return f"❌ JSON syntax error in '{path}' at line {e.lineno}: {e.msg}"
        
        else:
            return f"Syntax validation not supported for file type: {ext}"
            
    except Exception as e:
        return f"Error validating syntax: {str(e)}"

# Keep the original functions
@mcp.tool()
def run_command(command: str) -> str:
    """Execute a shell command and return the output"""
    try:
        # Security: Only allow safe commands
        dangerous_commands = ['rm', 'del', 'format', 'sudo', 'su', 'passwd']
        if any(cmd in command.lower() for cmd in dangerous_commands):
            return "Error: Command not allowed for security reasons"
        
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=30
        )
        
        output = f"Exit code: {result.returncode}\n"
        if result.stdout:
            output += f"Output:\n{result.stdout}\n"
        if result.stderr:
            output += f"Error:\n{result.stderr}\n"
        
        return output
    except subprocess.TimeoutExpired:
        return "Error: Command timed out (30s limit)"
    except Exception as e:
        return f"Error executing command: {str(e)}"

@mcp.tool()
def get_system_info() -> str:
    """Get system information about the laptop"""
    try:
        info = {
            "Operating System": platform.system(),
            "OS Version": platform.version(),
            "Machine": platform.machine(),
            "Processor": platform.processor(),
            "Python Version": platform.python_version(),
            "Current Directory": os.getcwd(),
            "Home Directory": str(Path.home()),
            "CPU Count": psutil.cpu_count(),
            "Memory Total": f"{psutil.virtual_memory().total // (1024**3)} GB",
            "Memory Available": f"{psutil.virtual_memory().available // (1024**3)} GB",
            "Disk Usage": f"{psutil.disk_usage('/').free // (1024**3)} GB free"
        }
        
        return json.dumps(info, indent=2)
    except Exception as e:
        return f"Error getting system info: {str(e)}"

@mcp.tool()
def find_files(pattern: str, directory: str = ".", max_results: int = 50) -> str:
    """Find files matching a pattern in the specified directory"""
    try:
        from pathlib import Path
        import fnmatch
        
        path = Path(directory).expanduser().resolve()
        if not path.exists():
            return f"Directory '{directory}' does not exist"
        
        matches = []
        count = 0
        
        for file_path in path.rglob("*"):
            if count >= max_results:
                break
            if fnmatch.fnmatch(file_path.name, pattern):
                matches.append(str(file_path.relative_to(path)))
                count += 1
        
        if not matches:
            return f"No files found matching pattern '{pattern}' in '{directory}'"
        
        result = f"Found {len(matches)} files matching '{pattern}':\n"
        result += "\n".join(matches)
        
        if count >= max_results:
            result += f"\n\n(Limited to {max_results} results)"
        
        return result
    except Exception as e:
        return f"Error finding files: {str(e)}"

@mcp.tool()
def get_running_processes() -> str:
    """Get information about running processes"""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                proc_info = proc.info
                if proc_info['cpu_percent'] > 0 or proc_info['memory_percent'] > 1:
                    processes.append(proc_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sort by CPU usage
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        
        result = "Top processes by CPU usage:\n"
        result += f"{'PID':<8} {'Name':<25} {'CPU%':<8} {'Memory%':<8}\n"
        result += "-" * 50 + "\n"
        
        for proc in processes[:20]:  # Top 20 processes
            result += f"{proc['pid']:<8} {proc['name'][:24]:<25} {proc['cpu_percent']:<8.1f} {proc['memory_percent']:<8.1f}\n"
        
        return result
    except Exception as e:
        return f"Error getting process info: {str(e)}"

if __name__ == "__main__":
    # Run the MCP server using stdio transport
    mcp.run(transport="stdio")