#!/bin/bash
# Convenience script to activate the virtual environment and start development

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run ./scripts/install.sh first"
    exit 1
fi

echo "🔧 Activating MCP Local development environment..."
echo "📁 Project directory: $PROJECT_ROOT"
echo ""
echo "✅ Virtual environment activated!"
echo ""
echo "🚀 Available commands:"
echo "  mcp-local          - Run the MCP Local server"
echo "  pytest             - Run tests"
echo "  black src/ tests/  - Format code"
echo "  isort src/ tests/  - Sort imports"
echo "  flake8 src/ tests/ - Lint code"
echo "  pip list           - Show installed packages"
echo ""
echo "📝 To deactivate: type 'deactivate'"
echo ""

# Activate the virtual environment in the current shell
source venv/bin/activate

# Start a new shell with the activated environment
exec bash --rcfile <(echo "source venv/bin/activate; PS1='(mcp-local) \u@\h:\w\$ '")
