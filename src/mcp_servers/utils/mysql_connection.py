import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
)

# Class to manage asynchronous MySQL database connections and operations
class DatabaseConnect:

    def __init__(
        self,
        user: str,
        password: str,
        database: str,
        server: str,
    ):
        self.user = user
        self.password = password
        self.database_name = database
        self.server = server

        # Async SQLAlchemy engine
        self.engine: AsyncEngine = create_async_engine(
            f"mysql+aiomysql://"
            f"{self.user}:{self.password}"
            f"@{self.server}:3306/"
            f"{self.database_name}",
            pool_pre_ping=True,
        )

    # Async method to retrieve the data from the entire table, querying all rows and columns.
    async def read_table(self, table_name: str):
        """
        Read an entire table asynchronously.

        Returns:
            list[dict]: Rows from the table.
        """
        # Create a SQL query to select all rows from the specified table
        query = text(f"SELECT * FROM `{table_name}`")

        async with self.engine.connect() as conn: # Create an asynchronous connection to the database

            result = await conn.execute(query) # Execute the query asynchronously

            rows = result.mappings().all()

            return [dict(row) for row in rows]

    # Async method to retrieve the schema of a specific table, including column names, data types, and constraints.
    async def get_table_schema(self, table_name: str):
        """
        Retrieve schema information for a table.
        """
        # Generate a SQL query to get column information from the INFORMATION_SCHEMA.COLUMNS table
        query = text("""
            SELECT
                COLUMN_NAME,
                DATA_TYPE,
                IS_NULLABLE,
                COLUMN_KEY
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = :database_name
            AND TABLE_NAME = :table_name
        """)

        async with self.engine.connect() as conn: # Create an asynchronous connection to the database

            # Execute the query asynchronously with parameters for database and table names
            result = await conn.execute(
                query,
                {
                    "database_name": self.database_name,
                    "table_name": table_name,
                },
            )

            rows = result.mappings().all()

        if not rows:
            return (
                f"Table '{table_name}' "
                "does not exist or has no columns."
            )

        schema_lines = [
            f"Table: {table_name}",
            "Columns:",
        ]

        for row in rows:

            col_info = (
                f"- {row['COLUMN_NAME']} "
                f"({row['DATA_TYPE']})"
            )

            if row["COLUMN_KEY"] == "PRI":
                col_info += " [PRIMARY KEY]"

            if row["IS_NULLABLE"] == "NO":
                col_info += " [NOT NULL]"

            schema_lines.append(col_info)

        return "\n".join(schema_lines)

    # Async method to retrieve schemas for multiple tables concurrently.
    # This method uses asyncio.gather to run multiple get_table_schema calls in parallel.
    async def get_multiple_table_schemas(
        self,
        table_names: list[str],
    ):
        """
        Retrieve schemas for multiple tables concurrently.
        """
        tasks = [
            self.get_table_schema(table)
            for table in table_names
        ]

        schemas = await asyncio.gather(*tasks) # Run all schema retrieval tasks concurrently and wait for their completion

        return "\n\n".join(schemas)

    # Async method to execute a SELECT query and return the results.
    # This method ensures that only SELECT queries are executed, raising an error for any other type of query.
    async def execute_select_query(self, query: str):
        """
        Execute a SELECT query asynchronously.

        Only SELECT queries are allowed.
        """

        query = query.strip()

        if not query.lower().startswith("select"):
            raise ValueError(
                "Only SELECT queries are allowed."
            )

        async with self.engine.connect() as conn: # Create an asynchronous connection to the database

            result = await conn.execute(
                text(query)
            )

            rows = result.fetchall()

            columns = list(result.keys())

            return rows, columns

    # Async method to close the database connection and dispose of the engine.
    async def close(self):
        """
        Dispose of the async database engine.
        """

        await self.engine.dispose()