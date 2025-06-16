# app.py
from mcp.server.fastmcp import FastMCP
import os
import subprocess
import platform
import psutil
from pathlib import Path
import json

# Create the MCP server using FastMCP
mcp = FastMCP("my-local-server")

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
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"Successfully wrote {len(content)} characters to '{path}'"
    except Exception as e:
        return f"Error writing file: {str(e)}"

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