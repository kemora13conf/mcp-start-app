#!/bin/bash
# Install script for MCP Local using virtual environment

set -e  # Exit on any error

echo "🚀 Installing MCP Local..."

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Check if Python 3.8+ is available
python_cmd=""
if command -v python3 &> /dev/null; then
    python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
        python_cmd="python3"
    fi
elif command -v python &> /dev/null; then
    if python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
        python_cmd="python"
    fi
fi

if [ -z "$python_cmd" ]; then
    echo "❌ Error: Python 3.8+ is required but not found"
    exit 1
fi

echo "✅ Using Python: $python_cmd"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    $python_cmd -m venv venv
else
    echo "📦 Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Install the package in development mode
echo "🔨 Installing MCP Local in development mode..."
pip install -e .

echo ""
echo "✅ Installation complete!"
echo ""
echo "🎯 To use MCP Local:"
echo ""
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Run the server directly:"
echo "   mcp-local"
echo ""
echo "3. Or use the run script:"
echo "   ./scripts/run_server.py"
echo ""
echo "📋 For Claude Desktop, add this to your configuration:"
echo ""
echo '{
  "mcpServers": {
    "mcp-local": {
      "command": "'"$PROJECT_ROOT"'/scripts/run_server.py",
      "args": []
    }
  }
}'
echo ""
echo "🔧 To run tests:"
echo "   source venv/bin/activate"
echo "   pytest"
echo ""
echo "🎉 MCP Local is ready to use!"
