from fastmcp import FastMCP
from mcp_servers.web_search import WebSearchTool

# Initialize the FastMCP server with a name. This instance will manage the registered tools and handle incoming requests.
mcp = FastMCP("My First MCP Server")

# Initialize the WebSearchTool. This tool will be used to perform web searches when called by the AI assistant.
web_search_tool = WebSearchTool()

# MCP tool functions. Each function is decorated with @mcp.tool() 
# to register it as a callable tool in the MCP server.

@mcp.tool() # Decorator to register the function as an MCP tool
def add(a: int, b: int): # Function to add two numbers together
    """Add two numbers together."""
    return a + b

@mcp.tool() # Decorator to register the function as an MCP tool
def subtract(a: int, b: int): # Function to subtract two numbers
    """Subtract two numbers."""
    return a - b    

@mcp.tool() # Decorator to register the function as an MCP tool
def multiply(a: int, b: int):   # Function to multiply two numbers
    """Multiply two numbers."""
    return a * b
    
@mcp.tool() # Decorator to register the function as an MCP tool
def divide(a: int, b: int): # Function to divide two numbers
    """Divide two numbers."""
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b    

@mcp.tool() # Decorator to register the function as an MCP tool
def web_search(query: str,num_results: int = 5): # Function to perform a web search using the WebSearchTool
    """
    Search the web for current information.

    Use this tool when the user asks for:
    - current information
    - recent news
    - latest events
    - information that may have changed recently
    - information that requires web search

    Args:
        query: The search query.
        num_results: Number of search results to return.

    Returns:
        Formatted web search results.
    """

    print(f"[MCP SERVER] web_search() called")

    print(f"[MCP SERVER] query = {query}")

    print(f"[MCP SERVER] num_results = {num_results}")

    # Perform the web search using the WebSearchTool
    results = web_search_tool.search(query=query,num_results=num_results)

    # Format the results for better readability
    formatted_results = (web_search_tool.format_search_results(results))
    
    print("[MCP SERVER] Web search completed")

    # Return the formatted results
    return formatted_results


if __name__ == "__main__":
    mcp.run()