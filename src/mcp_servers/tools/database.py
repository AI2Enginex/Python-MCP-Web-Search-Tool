import os
from mcp_servers.utils.mysql_connection import DatabaseConnect
import asyncio
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Retrieve database connection parameters from environment variables
username=os.getenv("DB_USERNAME")
password=os.getenv("DB_PASSWORD") 
database=os.getenv("DB_DATABASE")
server=os.getenv("DB_SERVER")

# Class for interacting with a MySQL Database Server for performing read-only operations
# The AI assistant can use this class to retrieve table schemas and execute SELECT queries on the database.
class DatabaseTool:

    """
    A tool for interacting with a MySQL database.
    """

    def __init__(self):
        """
        Initialize the DatabaseTool with connection parameters.

        Args:
            user: Database username.
            password: Database password.
            database: Database name.
            server: Database server address.
        """
        # Initialize the DatabaseConnect instance with the provided connection parameters
        self.db = DatabaseConnect(user=username, password=password, database=database, server=server)

    # Async method to retrieve a list of all tables in the database
    async def get_tables_(self):
        """
        Retrieve a list of all tables in the database.

        Returns:
            List of table names.
        """
        print("\n[MCP DATABASE] get_tables_list() called")

        try:
            tables = await self.db.get_tables_list()

            print(
                "[MCP DATABASE] Table list retrieval completed."
            )

            return tables

        except Exception as e:

            print(
                f"[MCP DATABASE] Table list error: {e}"
            )

            return f"Database table list error: {e}"

    # Method to retrieve the schema of one or more tables
    async def get_schema(self, table_names: str):

        """
        Retrieve the schema of one or more MySQL tables.

        Args:
            table_names:
                List of table names whose schemas should be returned.

        Returns:
            Human-readable table schemas.
        """

        print("\n[MCP DATABASE] get_database_schema() called")

        print(
            f"[MCP DATABASE] Tables requested: "
            f"{table_names}"
        )

        try:

            schema = await self.db.get_table_schema(
                table_name=table_names
            )

            print(
                "[MCP DATABASE] Schema retrieval completed."
            )

            return schema


        except Exception as e:

            print(
                f"[MCP DATABASE] Schema error: {e}"
            )

            return f"Database schema error: {e}"

    # Method to execute a SQL SELECT query and return results
    async def execute_query(self, query: str):

        """
        Execute a read-only SQL SELECT query.

        Args:
            query:
                SQL SELECT query to execute.

        Returns:
            Query results formatted as text.
        """

        print("\n[MCP DATABASE] execute_sql() called")

        print(
            f"[MCP DATABASE] SQL: {query}"
        )

        try:

            rows, columns = await self.db.execute_select_query(
                query
            )

            if not rows:

                return "Query executed successfully. No rows returned."

            formatted_rows = []

            for row in rows:

                row_dict = dict(
                    zip(columns, row)
                )

                formatted_rows.append(row_dict)

            print(
                f"[MCP DATABASE] "
                f"Returned {len(formatted_rows)} rows."
            )

            return str(formatted_rows)
        

        except Exception as e:

            print(
                f"[MCP DATABASE] Query error: {e}"
            )

            return f"Database query error: {e}"  
        
        finally:
            # Close the database connection after executing the query
            print("[MCP DATABASE] Closing database connection.")
            await self.db.close()

if __name__ == "__main__":
    # Example usage
    async def main():

        try:
            db_tool = DatabaseTool()

            result = await db_tool.get_schema(
                ["employees"]
            )

            print(result)
        except Exception as e:
            print(f"Error: {e}")

        finally:
            await db_tool.db.close()  # Ensure the database connection is closed

    asyncio.run(main())
    