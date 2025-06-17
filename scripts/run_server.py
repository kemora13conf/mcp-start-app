#!/usr/bin/env python3
"""
Quick start script for MCP Local server using virtual environment
"""

import sys
import os

# Get the project root directory
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

# Activate virtual environment
venv_python = os.path.join(project_root, "venv", "bin", "python")
if os.path.exists(venv_python):
    # Use venv python
    python_exe = venv_python
else:
    # Fallback to system python
    python_exe = sys.executable

# Add the src directory to the path
src_dir = os.path.join(project_root, "src")
sys.path.insert(0, src_dir)

# Import and run the main function
try:
    from mcp_local.main import main
    main()
except ImportError as e:
    print(f"Error importing mcp_local: {e}", file=sys.stderr)
    print("Make sure you have installed the package with:", file=sys.stderr)
    print("  source venv/bin/activate", file=sys.stderr)
    print("  pip install -e .", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"Error starting server: {e}", file=sys.stderr)
    sys.exit(1)
