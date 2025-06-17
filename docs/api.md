# API Documentation

## File Operations

### `list_files(directory: str = ".", show_hidden: bool = False) -> str`
List files and directories in the specified path.

**Parameters:**
- `directory`: Path to list (default: current directory)
- `show_hidden`: Include hidden files (default: False)

**Returns:** String listing of files with types and sizes

### `read_file(file_path: str) -> str`
Read the contents of a text file.

**Parameters:**
- `file_path`: Path to the file to read

**Returns:** File contents as string

### `write_file(file_path: str, content: str) -> str`
Write content to a file.

**Parameters:**
- `file_path`: Path to the file to write
- `content`: Content to write

**Returns:** Success message

## File Editing

### `edit_file_lines(file_path: str, start_line: int, new_content: str, end_line: Optional[int] = None) -> str`
Replace specific lines in a file with new content.

### `insert_lines(file_path: str, line_number: int, content: str) -> str`
Insert new lines at a specific position in the file.

### `delete_lines(file_path: str, start_line: int, end_line: Optional[int] = None) -> str`
Delete specific lines from a file.

## Search Tools

### `search_adv(...) -> str`
Advanced search across files with VSCode-like functionality.

**Features:**
- Regex support
- Case sensitivity options
- File type filtering
- Exclude patterns
- Context lines

## Backup and History

All file modifications automatically create backups and are logged in the edit history.
