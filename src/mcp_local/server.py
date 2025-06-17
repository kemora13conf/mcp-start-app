"""
Main MCP Local server implementation
"""

from mcp.server.fastmcp import FastMCP

from .tools.file_operations import register_file_operations
from .tools.file_editing import register_file_editing_tools
from .tools.search_tools import register_search_tools
from .services import backup_service, history_service, file_service


def create_server(name: str = "mcp-local") -> FastMCP:
    """Create and configure the MCP Local server"""
    
    # Create the FastMCP server
    mcp = FastMCP(name)
    
    # Initialize services
    backup_service.initialize()
    history_service.initialize()
    file_service.initialize()
    
    # Register all tool modules
    register_file_operations(mcp)
    register_file_editing_tools(mcp)
    register_search_tools(mcp)
    
    # Add a simple data query tool
    @mcp.tool()
    def get_local_data(query: str) -> str:
        """Get data from local system"""
        return f"Local data for query: '{query}'"
    
    return mcp


def main():
    """Main entry point for the server"""
    server = create_server()
    
    # Run the server
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
