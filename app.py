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
from typing import List, Dict, Optional, Tuple, Set
import difflib
import fnmatch
import mimetypes



# Default exclude patterns (like VSCode)
DEFAULT_EXCLUDE_PATTERNS = [
    ".git/*", "node_modules/*", "__pycache__/*", "*.pyc", "*.pyo", 
    ".DS_Store", "Thumbs.db", "*.log", ".env", ".vscode/*", ".idea/*",
    "dist/*", "build/*", "*.egg-info/*", ".pytest_cache/*", 
    "coverage/*", ".coverage", "*.min.js", "*.min.css"
]

# Common file type groups
FILE_TYPE_GROUPS = {
    "code": ["*.py", "*.js", "*.ts", "*.jsx", "*.tsx", "*.java", "*.c", "*.cpp", "*.h", "*.cs", "*.php", "*.rb", "*.go", "*.rs", "*.swift"],
    "web": ["*.html", "*.css", "*.scss", "*.sass", "*.less", "*.vue", "*.svelte"],
    "config": ["*.json", "*.yaml", "*.yml", "*.toml", "*.ini", "*.cfg", "*.conf"],
    "docs": ["*.md", "*.txt", "*.rst", "*.doc", "*.docx", "*.pdf"],
    "data": ["*.csv", "*.xlsx", "*.xml", "*.sql"],
    "all": ["*"]
}


# Create the MCP server using FastMCP
mcp = FastMCP("my-local-server")

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

@mcp.tool()
def search_adv(
    search_term: str,
    search_path: str = ".",
    case_sensitive: bool = False,
    whole_word: bool = False,
    use_regex: bool = False,
    include_patterns: Optional[str] = None,
    exclude_patterns: Optional[str] = None,
    file_types: str = "all",
    max_results: int = 1000,
    context_lines: int = 2,
    show_hidden: bool = False
) -> str:
    """
    VSCode-like search across files and directories
    
    Args:
        search_term: Text to search for
        search_path: Directory to search in (default: current directory)
        case_sensitive: Case sensitive search (default: False)
        whole_word: Match whole words only (default: False)
        use_regex: Use regular expressions (default: False)
        include_patterns: Comma-separated file patterns to include (e.g., "*.py,*.js")
        exclude_patterns: Comma-separated patterns to exclude (e.g., "*.log,test/*")
        file_types: File type group (code, web, config, docs, data, all) or custom patterns
        max_results: Maximum number of matches to return
        context_lines: Number of context lines to show around matches
        show_hidden: Include hidden files and directories
    """
    try:
        base_path = Path(search_path).expanduser().resolve()
        if not base_path.exists():
            return f"❌ Path '{search_path}' does not exist"
        
        # Prepare search pattern
        search_flags = 0 if case_sensitive else re.IGNORECASE
        
        if use_regex:
            try:
                if whole_word:
                    pattern = re.compile(r'\b' + search_term + r'\b', search_flags)
                else:
                    pattern = re.compile(search_term, search_flags)
            except re.error as e:
                return f"❌ Invalid regex pattern: {e}"
        else:
            # Escape special regex characters for literal search
            escaped_term = re.escape(search_term)
            if whole_word:
                pattern = re.compile(r'\b' + escaped_term + r'\b', search_flags)
            else:
                pattern = re.compile(escaped_term, search_flags)
        
        # Prepare file patterns
        if include_patterns:
            include_list = [p.strip() for p in include_patterns.split(',')]
        elif file_types in FILE_TYPE_GROUPS:
            include_list = FILE_TYPE_GROUPS[file_types]
        else:
            # Custom file types
            include_list = [p.strip() for p in file_types.split(',')]
        
        # Prepare exclude patterns - always use defaults plus any additional ones
        exclude_list = DEFAULT_EXCLUDE_PATTERNS.copy()
        if exclude_patterns:
            exclude_list.extend([p.strip() for p in exclude_patterns.split(',')])
        
        # Search files
        matches = []
        files_searched = 0
        files_with_matches = 0
        
        def search_in_file(file_path: Path) -> List[Dict]:
            """Search for pattern in a single file"""
            nonlocal files_searched
            files_searched += 1
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                
                file_matches = []
                for line_num, line in enumerate(lines, 1):
                    if pattern.search(line):
                        # Get context lines
                        start_line = max(0, line_num - context_lines - 1)
                        end_line = min(len(lines), line_num + context_lines)
                        
                        context = []
                        for i in range(start_line, end_line):
                            prefix = ">>> " if i == line_num - 1 else "    "
                            context.append(f"{prefix}{i+1:4d}: {lines[i].rstrip()}")
                        
                        # Highlight matches in the main line
                        highlighted_line = lines[line_num - 1].rstrip()
                        highlighted_line = pattern.sub(f"**{search_term}**", highlighted_line)
                        
                        file_matches.append({
                            "line_number": line_num,
                            "line_content": lines[line_num - 1].strip(),
                            "highlighted_line": highlighted_line,
                            "context": context,
                            "column": pattern.search(line).start() + 1 if pattern.search(line) else 0
                        })
                
                return file_matches
            except Exception:
                return []
        
        # Walk through directory
        for root, dirs, files in os.walk(base_path):
            root_path = Path(root)
            
            # Filter directories
            if not show_hidden:
                dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            # Check if directory should be excluded
            if should_exclude_file(root_path, exclude_list):
                dirs.clear()  # Don't recurse into excluded directories
                continue
            
            for file_name in files:
                file_path = root_path / file_name
                
                # Skip hidden files if not requested
                if not show_hidden and file_name.startswith('.'):
                    continue
                
                # Check file patterns
                matches_include = any(fnmatch.fnmatch(file_name, pattern) for pattern in include_list)
                if not matches_include:
                    continue
                
                # Check exclude patterns
                if should_exclude_file(file_path, exclude_list):
                    continue
                
                # Check if it's a text file
                if not is_text_file(file_path):
                    continue
                
                # Search in file
                file_matches = search_in_file(file_path)
                if file_matches:
                    files_with_matches += 1
                    relative_path = file_path.relative_to(base_path)
                    
                    for match in file_matches:
                        matches.append({
                            "file": str(relative_path),
                            "full_path": str(file_path),
                            **match
                        })
                        
                        if len(matches) >= max_results:
                            break
                
                if len(matches) >= max_results:
                    break
            
            if len(matches) >= max_results:
                break
        
        # Format results
        if not matches:
            return f"🔍 No matches found for '{search_term}' in {files_searched} files"
        
        result = f"🔍 **Search Results for '{search_term}'**\n"
        result += f"Found {len(matches)} matches in {files_with_matches} files (searched {files_searched} files)\n"
        result += f"Search path: {base_path}\n"
        result += f"Options: {'Case sensitive' if case_sensitive else 'Case insensitive'}"
        if whole_word:
            result += ", Whole word"
        if use_regex:
            result += ", Regex"
        result += f", File types: {file_types}\n\n"
        
        # Group matches by file
        files_dict = {}
        for match in matches:
            file_path = match["file"]
            if file_path not in files_dict:
                files_dict[file_path] = []
            files_dict[file_path].append(match)
        
        # Display results
        for file_path, file_matches in list(files_dict.items())[:50]:  # Limit files shown
            result += f"📄 **{file_path}** ({len(file_matches)} matches)\n"
            
            for match in file_matches[:10]:  # Limit matches per file
                result += f"   Line {match['line_number']}, Column {match['column']}\n"
                if context_lines > 0:
                    result += "\n".join(f"     {line}" for line in match['context'])
                else:
                    result += f"     >>> {match['line_number']:4d}: {match['highlighted_line']}"
                result += "\n\n"
            
            if len(file_matches) > 10:
                result += f"     ... and {len(file_matches) - 10} more matches\n\n"
        
        if len(files_dict) > 50:
            result += f"... and {len(files_dict) - 50} more files with matches\n"
        
        if len(matches) >= max_results:
            result += f"\n⚠️ Results limited to {max_results} matches. Use more specific search terms or increase max_results.\n"
        
        return result
        
    except Exception as e:
        return f"❌ Search error: {str(e)}"

@mcp.tool()
def replace_adv(
    search_term: str,
    replace_with: str,
    search_path: str = ".",
    case_sensitive: bool = False,
    whole_word: bool = False,
    use_regex: bool = False,
    include_patterns: Optional[str] = None,
    exclude_patterns: Optional[str] = None,
    file_types: str = "all",
    dry_run: bool = True,
    backup: bool = True
) -> str:
    """
    VSCode-like find and replace across multiple files
    
    Args:
        search_term: Text to find
        replace_with: Text to replace with
        search_path: Directory to search in
        case_sensitive: Case sensitive search
        whole_word: Match whole words only
        use_regex: Use regular expressions
        include_patterns: File patterns to include
        exclude_patterns: Patterns to exclude
        file_types: File type group or patterns
        dry_run: Preview changes without applying them
        backup: Create backups before replacing
    """
    try:
        base_path = Path(search_path).expanduser().resolve()
        if not base_path.exists():
            return f"❌ Path '{search_path}' does not exist"
        
        # Prepare search pattern (same as vscode_search)
        search_flags = 0 if case_sensitive else re.IGNORECASE
        
        if use_regex:
            try:
                if whole_word:
                    pattern = re.compile(r'\b' + search_term + r'\b', search_flags)
                else:
                    pattern = re.compile(search_term, search_flags)
            except re.error as e:
                return f"❌ Invalid regex pattern: {e}"
        else:
            escaped_term = re.escape(search_term)
            if whole_word:
                pattern = re.compile(r'\b' + escaped_term + r'\b', search_flags)
            else:
                pattern = re.compile(escaped_term, search_flags)
        
        # Prepare file patterns (same logic as vscode_search)
        if include_patterns:
            include_list = [p.strip() for p in include_patterns.split(',')]
        elif file_types in FILE_TYPE_GROUPS:
            include_list = FILE_TYPE_GROUPS[file_types]
        else:
            include_list = [p.strip() for p in file_types.split(',')]
        
        exclude_list = DEFAULT_EXCLUDE_PATTERNS.copy()
        if exclude_patterns:
            exclude_list.extend([p.strip() for p in exclude_patterns.split(',')])
        
        # Find and replace
        changes = []
        files_processed = 0
        total_replacements = 0
        
        for root, dirs, files in os.walk(base_path):
            root_path = Path(root)
            
            # Filter directories and check exclusions (same as search)
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            if should_exclude_file(root_path, exclude_list):
                dirs.clear()
                continue
            
            for file_name in files:
                file_path = root_path / file_name
                
                if file_name.startswith('.'):
                    continue
                
                matches_include = any(fnmatch.fnmatch(file_name, pattern) for pattern in include_list)
                if not matches_include:
                    continue
                
                if should_exclude_file(file_path, exclude_list):
                    continue
                
                if not is_text_file(file_path):
                    continue
                
                # Process file
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        original_content = f.read()
                    
                    # Count matches
                    matches = pattern.findall(original_content)
                    if not matches:
                        continue
                    
                    files_processed += 1
                    file_replacements = len(matches)
                    total_replacements += file_replacements
                    
                    # Perform replacement
                    new_content = pattern.sub(replace_with, original_content)
                    
                    relative_path = file_path.relative_to(base_path)
                    change_info = {
                        "file": str(relative_path),
                        "full_path": str(file_path),
                        "replacements": file_replacements,
                        "original_size": len(original_content),
                        "new_size": len(new_content)
                    }
                    changes.append(change_info)
                    
                    # Apply changes if not dry run
                    if not dry_run:
                        # Create backup if requested
                        if backup:
                            backup_path = create_backup(str(file_path))
                            change_info["backup"] = backup_path
                        
                        # Write new content
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        
                        # Log the edit
                        log_edit("vscode_replace", str(file_path), {
                            "search_term": search_term,
                            "replace_with": replace_with,
                            "replacements": file_replacements,
                            "backup": change_info.get("backup", "")
                        })
                
                except Exception as e:
                    changes.append({
                        "file": str(file_path.relative_to(base_path)),
                        "error": str(e)
                    })
        
        # Format results
        mode = "DRY RUN" if dry_run else "APPLIED"
        result = f"🔄 **Find and Replace Results ({mode})**\n"
        result += f"Search: '{search_term}' → Replace: '{replace_with}'\n"
        result += f"Found {total_replacements} replacements in {files_processed} files\n"
        result += f"Search path: {base_path}\n\n"
        
        if not changes:
            result += "❌ No matches found to replace\n"
            return result
        
        # Show file changes
        for change in changes[:20]:  # Limit display
            if "error" in change:
                result += f"❌ {change['file']}: {change['error']}\n"
            else:
                result += f"✅ {change['file']}: {change['replacements']} replacements"
                if not dry_run and change.get('backup'):
                    result += f" (backup: {Path(change['backup']).name})"
                result += "\n"
        
        if len(changes) > 20:
            result += f"... and {len(changes) - 20} more files\n"
        
        if dry_run:
            result += f"\n💡 This was a dry run. Use dry_run=False to apply changes.\n"
        else:
            result += f"\n✅ Replacements applied successfully!\n"
        
        return result
        
    except Exception as e:
        return f"❌ Replace error: {str(e)}"

@mcp.tool()
def search_files_by_name(
    filename_pattern: str,
    search_path: str = ".",
    case_sensitive: bool = False,
    exact_match: bool = False,
    show_hidden: bool = False,
    exclude_patterns: Optional[str] = None
) -> str:
    """
    Search for files by name pattern (like VSCode's file search)
    
    Args:
        filename_pattern: Pattern to match filenames
        search_path: Directory to search in
        case_sensitive: Case sensitive filename matching
        exact_match: Exact filename match (no wildcards)
        show_hidden: Include hidden files
        exclude_patterns: Patterns to exclude
    """
    try:
        base_path = Path(search_path).expanduser().resolve()
        if not base_path.exists():
            return f"❌ Path '{search_path}' does not exist"
        
        # Prepare exclude patterns
        exclude_list = DEFAULT_EXCLUDE_PATTERNS.copy()
        if exclude_patterns:
            exclude_list.extend([p.strip() for p in exclude_patterns.split(',')])
        
        # Prepare search pattern
        if exact_match:
            if case_sensitive:
                match_func = lambda name: name == filename_pattern
            else:
                match_func = lambda name: name.lower() == filename_pattern.lower()
        else:
            # Use fnmatch for pattern matching
            if case_sensitive:
                match_func = lambda name: fnmatch.fnmatch(name, filename_pattern)
            else:
                match_func = lambda name: fnmatch.fnmatch(name.lower(), filename_pattern.lower())
        
        # Search for files
        matches = []
        total_files = 0
        
        for root, dirs, files in os.walk(base_path):
            root_path = Path(root)
            
            # Filter directories
            if not show_hidden:
                dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            if should_exclude_file(root_path, exclude_list):
                dirs.clear()
                continue
            
            for file_name in files:
                total_files += 1
                
                if not show_hidden and file_name.startswith('.'):
                    continue
                
                file_path = root_path / file_name
                if should_exclude_file(file_path, exclude_list):
                    continue
                
                if match_func(file_name):
                    relative_path = file_path.relative_to(base_path)
                    file_stat = file_path.stat()
                    
                    matches.append({
                        "file": str(relative_path),
                        "full_path": str(file_path),
                        "size": file_stat.st_size,
                        "modified": datetime.datetime.fromtimestamp(file_stat.st_mtime),
                        "type": "📁" if file_path.is_dir() else "📄"
                    })
        
        # Format results
        if not matches:
            return f"🔍 No files found matching pattern '{filename_pattern}' (searched {total_files} files)"
        
        result = f"📂 **File Search Results**\n"
        result += f"Pattern: '{filename_pattern}'\n"
        result += f"Found {len(matches)} files (searched {total_files} total)\n"
        result += f"Search path: {base_path}\n\n"
        
        # Sort by relevance (exact matches first, then by name)
        matches.sort(key=lambda x: (x["file"].lower().find(filename_pattern.lower()), x["file"]))
        
        for match in matches[:100]:  # Limit results
            size_str = f"{match['size']:,} bytes" if match['size'] < 1024 else f"{match['size']/1024:.1f} KB"
            modified_str = match['modified'].strftime("%Y-%m-%d %H:%M")
            result += f"{match['type']} **{match['file']}**\n"
            result += f"     Size: {size_str}, Modified: {modified_str}\n"
            result += f"     Path: {match['full_path']}\n\n"
        
        if len(matches) > 100:
            result += f"... and {len(matches) - 100} more files\n"
        
        return result
        
    except Exception as e:
        return f"❌ File search error: {str(e)}"

@mcp.tool()
def get_search_stats(search_path: str = ".") -> str:
    """Get statistics about files in the search path"""
    try:
        base_path = Path(search_path).expanduser().resolve()
        if not base_path.exists():
            return f"❌ Path '{search_path}' does not exist"
        
        stats = {
            "total_files": 0,
            "total_dirs": 0,
            "text_files": 0,
            "binary_files": 0,
            "hidden_files": 0,
            "total_size": 0,
            "file_types": {},
            "largest_files": []
        }
        
        for root, dirs, files in os.walk(base_path):
            stats["total_dirs"] += len(dirs)
            
            for file_name in files:
                file_path = Path(root) / file_name
                try:
                    file_stat = file_path.stat()
                    stats["total_files"] += 1
                    stats["total_size"] += file_stat.st_size
                    
                    if file_name.startswith('.'):
                        stats["hidden_files"] += 1
                    
                    # File type
                    ext = file_path.suffix.lower()
                    if ext:
                        stats["file_types"][ext] = stats["file_types"].get(ext, 0) + 1
                    else:
                        stats["file_types"]["(no extension)"] = stats["file_types"].get("(no extension)", 0) + 1
                    
                    # Text vs binary
                    if is_text_file(file_path):
                        stats["text_files"] += 1
                    else:
                        stats["binary_files"] += 1
                    
                    # Track largest files
                    stats["largest_files"].append({
                        "path": str(file_path.relative_to(base_path)),
                        "size": file_stat.st_size
                    })
                except:
                    continue
        
        # Sort largest files
        stats["largest_files"].sort(key=lambda x: x["size"], reverse=True)
        stats["largest_files"] = stats["largest_files"][:10]
        
        # Format results
        size_mb = stats["total_size"] / (1024 * 1024)
        
        result = f"📊 **Directory Statistics**\n"
        result += f"Path: {base_path}\n\n"
        result += f"**Overview:**\n"
        result += f"• Total files: {stats['total_files']:,}\n"
        result += f"• Total directories: {stats['total_dirs']:,}\n"
        result += f"• Total size: {size_mb:.1f} MB\n"
        result += f"• Text files: {stats['text_files']:,}\n"
        result += f"• Binary files: {stats['binary_files']:,}\n"
        result += f"• Hidden files: {stats['hidden_files']:,}\n\n"
        
        # Top file types
        sorted_types = sorted(stats["file_types"].items(), key=lambda x: x[1], reverse=True)
        result += f"**File Types (top 10):**\n"
        for ext, count in sorted_types[:10]:
            result += f"• {ext}: {count:,} files\n"
        
        # Largest files
        result += f"\n**Largest Files:**\n"
        for file_info in stats["largest_files"]:
            size_str = f"{file_info['size']/1024/1024:.1f} MB" if file_info['size'] > 1024*1024 else f"{file_info['size']/1024:.1f} KB"
            result += f"• {file_info['path']}: {size_str}\n"
        
        return result
        
    except Exception as e:
        return f"❌ Stats error: {str(e)}"

if __name__ == "__main__":
    # Run the MCP server using stdio transport
    mcp.run(transport="stdio")