# MCP Start App

A comprehensive Model Context Protocol (MCP) server for advanced local file management and system operations.

## Features

### 🗂️ File Operations
- **Read/Write Files**: Full support for text file operations with encoding handling
- **List Directories**: Browse filesystem with size information and hidden file support
- **File Information**: Detailed metadata including permissions, timestamps, and size
- **Path Validation**: Robust path handling with security checks

### ✏️ Advanced File Editing
- **Line-based Editing**: Edit, insert, or delete specific lines in files
- **Find & Replace**: Text replacement with regex support across multiple files
- **Diff Viewing**: Compare current files with backups
- **Edit History**: Track all file modifications with detailed logs

### 🔍 Advanced Search Capabilities
- **VSCode-like Search**: Advanced search across multiple files with context
- **File Type Filtering**: Search by extension groups (code, web, config, etc.)
- **Pattern Matching**: Support for wildcards and regex
- **Context Display**: Show surrounding lines for search results
- **File Name Search**: Find files by name patterns
- **Search Statistics**: Analyze file distribution and sizes

### 💻 System Operations
- **Command Execution**: Safe execution of system commands
- **System Information**: Hardware and software details
- **Process Management**: View running processes
- **File Finding**: Advanced file discovery with patterns

### 🔧 Code Tools
- **Syntax Validation**: Check syntax for Python, JavaScript, JSON, etc.
- **Code Formatting**: Format code using standard formatters (Black, Prettier)
- **Language Detection**: Auto-detect programming languages

### 🔄 Backup & History
- **Automatic Backups**: Files are backed up before modifications
- **Edit Tracking**: Complete history of all file operations
- **Restoration**: Easy restore from backups
- **History Analysis**: Statistics and insights on editing patterns

### 🛡️ Security & Safety
- **Path Validation**: Prevents directory traversal attacks
- **File Size Limits**: Configurable limits to prevent memory issues
- **Command Filtering**: Restricted dangerous command execution
- **Backup System**: Automatic backup before destructive operations

## Quick Start

### 1. Installation

```bash
# Clone or navigate to the project
cd /Users/{{USERNAME}}/Documents/mcp-start-app

# Run the installation script (sets up venv and installs everything)
./scripts/install.sh
```

### 2. Activation

```bash
# Activate the virtual environment
source venv/bin/activate

# Run the server
mcp-start-app
```

### 3. Alternative Run Methods

```bash
# Using the run script (auto-activates venv)
./scripts/run_server.py

# Direct Python execution
source venv/bin/activate
python -m mcp_start_app.main
```

## Configuration

### Claude Desktop Configuration

Add to your Claude Desktop config file:

```json
{
  "mcpServers": {
    "mcp-start-app": {
      "command": "/Users/{{USERNAME}}/Documents/mcp-start-app/scripts/run_server.py",
      "args": []
    }
  }
}
```

## Available Tools

### Basic File Operations
- `list_files(directory, show_hidden)` - List directory contents
- `read_file(file_path)` - Read text file contents  
- `write_file(file_path, content)` - Write content to file
- `get_file_lines(file_path, start_line, end_line)` - Get specific lines
- `get_file_info(file_path)` - Get detailed file information

### Advanced File Editing
- `edit_file_lines(file_path, start_line, new_content, end_line)` - Edit specific lines
- `insert_lines(file_path, line_number, content)` - Insert new lines
- `delete_lines(file_path, start_line, end_line)` - Delete lines
- `replace_in_file(file_path, search_pattern, replace_with, use_regex)` - Find & replace
- `get_file_diff(file_path, backup_file)` - Show file differences
- `get_edit_history(limit, file_path)` - View edit history

### Advanced Search Tools
- `search_adv(search_term, search_path, case_sensitive, whole_word, use_regex, include_patterns, exclude_patterns, file_types, max_results, context_lines, show_hidden)` - Advanced multi-file search
- `replace_adv(search_term, replace_with, search_path, case_sensitive, whole_word, use_regex, include_patterns, exclude_patterns, file_types, dry_run, backup)` - Advanced multi-file replace
- `search_files_by_name(filename_pattern, search_path, case_sensitive, exact_match, show_hidden, exclude_patterns)` - Search files by name
- `search_in_files(search_pattern, directory, file_pattern, use_regex)` - Simple text search
- `get_search_stats(search_path)` - Get directory statistics

### System Tools
- `run_command(command)` - Execute system commands (with safety restrictions)
- `get_system_info()` - Get comprehensive system information
- `find_files(pattern, directory, max_results)` - Find files by pattern
- `get_running_processes()` - View running processes

### Code Tools
- `validate_syntax(file_path)` - Check code syntax
- `format_code(file_path, language)` - Format code files

### Data Tools
- `get_local_data(query)` - Local data queries

## Project Structure

```
mcp-start-app/
├── 📁 venv/                        # Virtual environment
├── 📁 src/mcp_local/               # Main package
│   ├── 📁 core/                    # Core utilities & config
│   ├── 📁 services/                # Business logic layer
│   ├── 📁 tools/                   # MCP tool implementations
│   │   ├── file_operations.py      # Basic file tools
│   │   ├── file_editing.py         # Advanced editing tools
│   │   ├── search_tools.py         # Search and replace tools
│   │   ├── system_tools.py         # System operation tools
│   │   └── code_tools.py           # Code formatting and validation
│   ├── main.py                     # Entry point
│   └── server.py                   # Server configuration
├── 📁 tests/                       # Test suite
├── 📁 scripts/                     # Installation & run scripts
├── requirements.txt                # Dependencies
├── pyproject.toml                  # Python packaging
└── README.md                       # This file
```

## Development

### Running Tests

```bash
source venv/bin/activate
pytest                    # Run all tests
pytest --cov             # Run with coverage
```

### Code Quality

```bash
source venv/bin/activate
black src/ tests/         # Format code
isort src/ tests/         # Sort imports  
flake8 src/ tests/        # Lint code
mypy src/                 # Type checking
```

## License

This project is licensed under the MIT License.
