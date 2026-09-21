from fastmcp import FastMCP
from mcp_servers.tools.web_search import WebSearchTool
from mcp_servers.tools.database import DatabaseTool
# Initialize the FastMCP server with a name. This instance will manage the registered tools and handle incoming requests.
mcp = FastMCP("My First MCP Server")

# Initialize the WebSearchTool. This tool will be used to perform web searches when called by the AI assistant.
web_search_tool = WebSearchTool()

# Initialize the DatabaseTool. This tool will be used to interact with the database when called by the AI assistant.
database_tool = DatabaseTool()

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
async def web_search(query: str,num_results: int = 5): # Function to perform a web search using the WebSearchTool
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
    results = await web_search_tool.search(query=query,num_results=num_results)

    # Format the results for better readability
    formatted_results = web_search_tool.format_search_results(results)
    
    print("[MCP SERVER] Web search completed")

    # Return the formatted results
    return formatted_results


@mcp.tool() # Decorator to register the function as an MCP tool
async def list_tables(): # Function to list all tables in the database using the DatabaseTool
    """
    List all tables in the database.

    Use this tool when the user asks for:
    - list of tables
    - available tables
    - database structure

    Returns:
        String containing the list of table names.
    """
    tables_ = " "
    print(f"[MCP SERVER] list_tables() called")

    # Retrieve the list of tables using the DatabaseTool
    tables = await database_tool.get_tables_()
    for tables in tables:
        print(f"[MCP SERVER] Table: {tables}")
        tables_ += f"{tables}\n"
        
    print("[MCP SERVER] Table listing completed")

    # Return the list of table names
    return tables_

@mcp.tool() # Decorator to register the function as an MCP tool
async def get_table_schema(table_name: str): # Function to retrieve table schema information from the database using the DatabaseTool
    """
    Retrieve table schema information from the database.
    Parameters:
        table_name: List of table names to retrieve schema information for.
        
    Use this tool when the user asks for:
    - database schema
    - table structure
    - column information

    Returns:
        Table schema information formatted as text.
    """

    print(f"[MCP SERVER] get_table_schema() called")

    # Retrieve the table schema using the DatabaseTool
    schema_info = await database_tool.get_schema(table_names=table_name)

    print("[MCP SERVER] Table schema retrieval completed")

    # Return the schema information
    return schema_info



@mcp.tool() # Decorator to register the function as an MCP tool
async def execute_query(query: str): # Function to execute a SQL query using the DatabaseTool
    """
    Execute a SQL query on the database.

    Use this tool when the user asks for:
    - database queries
    - data retrieval    

    Returns:
        Query results formatted as text.
    """

    print(f"[MCP SERVER] execute_query() called")

    # Execute the SQL query using the DatabaseTool
    results = await database_tool.execute_query(query=query)

    print("[MCP SERVER] SQL query execution completed")

    # Return the query results
    return results

if __name__ == "__main__":
    mcp.run()