"""
Main entry point for MCP Local
"""

import sys
import argparse
from .server import create_server


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="MCP Local Server")
    parser.add_argument("--name", default="mcp-local", 
                       help="Server name (default: mcp-local)")
    parser.add_argument("--transport", default="stdio", 
                       choices=["stdio"], help="Transport type (default: stdio)")
    
    args = parser.parse_args()
    
    try:
        # Create and run the server
        server = create_server(args.name)
        print(f"Starting MCP Local server: {args.name}", file=sys.stderr)
        server.run(transport=args.transport)
    except KeyboardInterrupt:
        print("\nServer stopped by user", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Error starting server: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
