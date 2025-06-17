# MCP Local Server

A Model Context Protocol (MCP) server that provides local system access and file management capabilities. This server allows Claude Desktop to interact with your local file system, execute commands, and gather system information.

## Features

- **File Management**: List, read, write, and find files on your local system
- **System Information**: Get detailed information about your computer (OS, CPU, memory, etc.)
- **Process Monitoring**: View running processes and their resource usage
- **Command Execution**: Run safe shell commands with security restrictions
- **Cross-Platform**: Works on macOS, Windows, and Linux

## Available Tools

- `get_local_data(query)` - Get data from local system
- `list_files(directory, show_hidden)` - List files and directories
- `read_file(file_path)` - Read contents of text files
- `write_file(file_path, content)` - Write content to files
- `run_command(command)` - Execute shell commands safely
- `get_system_info()` - Get comprehensive system information
- `find_files(pattern, directory, max_results)` - Find files matching patterns
- `get_running_processes()` - View running processes and resource usage

## Installation and Setup

### Prerequisites

- Python 3.8 or higher
- Claude Desktop application
- Terminal/Command Prompt access

### Step 1: Clone or Download the Project

If you haven't already, ensure you have the MCP server files in your desired directory:

```
~/Desktop/Python/mcp/
├── app.py
├── requirements.txt
├── claude_desktop_config.json
├── venv/
└── README.md
```

### Step 2: Set Up Python Virtual Environment

#### macOS/Linux:

```bash
cd ~/Desktop/Python/mcp
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Windows:

```cmd
cd %USERPROFILE%\Desktop\Python\mcp
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Step 3: Test the Server

Test that the server runs correctly:

#### macOS/Linux:
```bash
source venv/bin/activate
python app.py
```

#### Windows:
```cmd
venv\Scripts\activate
python app.py
```

The server should start and wait for input. Press `Ctrl+C` to stop.

### Step 4: Configure Claude Desktop

#### macOS Configuration:

1. **Locate Claude Desktop config file:**
   ```bash
   ~/Library/Application Support/Claude/claude_desktop_config.json
   ```

2. **Create or edit the config file:**
   ```json
   {
     "mcpServers": {
       "my-local-server": {
         "command": "/Users/YOUR_USERNAME/Desktop/Python/mcp/venv/bin/python",
         "args": ["/Users/YOUR_USERNAME/Desktop/Python/mcp/app.py"],
         "env": {}
       }
     }
   }
   ```

   **Replace `YOUR_USERNAME` with your actual username.**

3. **Alternative method using the included config:**
   ```bash
   # Copy the provided config to Claude's directory
   cp ~/Desktop/Python/mcp/claude_desktop_config.json ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

#### Windows Configuration:

1. **Locate Claude Desktop config file:**
   ```
   %APPDATA%\Claude\claude_desktop_config.json
   ```

2. **Create or edit the config file:**
   ```json
   {
     "mcpServers": {
       "my-local-server": {
         "command": "C:\\Users\\YOUR_USERNAME\\Desktop\\Python\\mcp\\venv\\Scripts\\python.exe",
         "args": ["C:\\Users\\YOUR_USERNAME\\Desktop\\Python\\mcp\\app.py"],
         "env": {}
       }
     }
   }
   ```

   **Replace `YOUR_USERNAME` with your actual Windows username.**

3. **Using Command Prompt to create the config:**
   ```cmd
   # Create the directory if it doesn't exist
   mkdir "%APPDATA%\Claude" 2>nul
   
   # Copy and edit the config file
   copy "%USERPROFILE%\Desktop\Python\mcp\claude_desktop_config.json" "%APPDATA%\Claude\claude_desktop_config.json"
   ```

### Step 5: Restart Claude Desktop

After configuring the MCP server:

1. **Completely quit Claude Desktop** (not just close the window)
2. **Restart Claude Desktop**
3. **Verify the connection** by asking Claude to list files or get system information

## Usage Examples

Once configured, you can use these commands in Claude Desktop:

```
List files in my home directory
```

```
Read the contents of ~/Desktop/Python/mcp/app.py
```

```
Get my system information
```

```
Find all Python files in my Desktop folder
```

```
What processes are using the most CPU?
```

## Troubleshooting

### Common Issues:

1. **"Server not found" error:**
   - Verify the paths in your `claude_desktop_config.json` are correct
   - Ensure the virtual environment is properly created
   - Check that all dependencies are installed

2. **Permission errors:**
   - Make sure the Python files have execute permissions
   - On macOS/Linux: `chmod +x ~/Desktop/Python/mcp/app.py`

3. **Python not found:**
   - Verify Python is installed and accessible
   - Check virtual environment activation
   - Ensure the correct Python path in config

4. **Dependencies missing:**
   ```bash
   # Reinstall dependencies
   pip install -r requirements.txt
   ```

### Debugging Steps:

1. **Test server independently:**
   ```bash
   cd ~/Desktop/Python/mcp
   source venv/bin/activate  # macOS/Linux
   # or
   venv\Scripts\activate     # Windows
   python app.py
   ```

2. **Check Claude Desktop logs:**
   - macOS: `~/Library/Logs/Claude/`
   - Windows: `%APPDATA%\Claude\logs\`

3. **Verify config file syntax:**
   ```bash
   python -m json.tool ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

## Security Considerations

- The server includes security restrictions for command execution
- Dangerous commands (rm, del, format, sudo, etc.) are blocked
- File size limits are enforced (1MB for reading)
- Command execution has a 30-second timeout

## File Structure

```
~/Desktop/Python/mcp/
├── app.py                        # Main MCP server application
├── requirements.txt              # Python dependencies
├── claude_desktop_config.json    # Sample Claude Desktop configuration
├── venv/                         # Python virtual environment
│   ├── bin/                      # Executables (macOS/Linux)
│   ├── Scripts/                  # Executables (Windows)
│   └── lib/                      # Installed packages
└── README.md                     # This documentation
```

## Development

To modify or extend the server:

1. **Add new tools** in `app.py` using the `@mcp.tool()` decorator
2. **Update dependencies** in `requirements.txt` if needed
3. **Test changes** by restarting the server and Claude Desktop

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify all paths and configurations
3. Test the server independently before connecting to Claude
4. Review Claude Desktop logs for specific error messages

## Version Information

- **MCP Protocol Version**: 1.9.4
- **Python Requirements**: 3.8+
- **Supported Platforms**: macOS, Windows, Linux
