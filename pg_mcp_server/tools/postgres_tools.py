from server import mcp
import utils.postgres_tools_util as pg_util

POSTGRES_TOOLS_INSTANCE = None

@mcp.tool()
def make_postgres_query(query: str) -> str:
    """
    Executes a PostgreSQL query and returns the result as a string.
    
    Args:
        query (str): The SQL query to execute.
    
    Returns:
        str: The result of the query.
    """
    if POSTGRES_TOOLS_INSTANCE is None:
        return "operation failed; please init_postgres_database before querying"

    result = POSTGRES_TOOLS_INSTANCE.query(query)
    if result is None:
        return "Query failed or database not available."
    return str(result)

@mcp.tool()
def init_postgres_database(pg_dump_file: str) -> bool:
    """
    Initializes a PostgreSQL database using a dump file and connects to it.
    
    Args:
        pg_dump_file (str): The path to the PostgreSQL dump file.
    
    Returns:
        bool: True if the database was initialized successfully, False otherwise.
    """
    global POSTGRES_TOOLS_INSTANCE

    if POSTGRES_TOOLS_INSTANCE is None:
        POSTGRES_TOOLS_INSTANCE = pg_util.Postgres_Tools(pg_dump_file)
    
    if POSTGRES_TOOLS_INSTANCE.create_database():
        return POSTGRES_TOOLS_INSTANCE.connect()
    return False


@mcp.tool()
def delete_postgres_database() -> bool:
    """
    Deletes the PostgreSQL database.
    
    Returns:
        bool: True if the database was deleted successfully, False otherwise.
    """
    if POSTGRES_TOOLS_INSTANCE is None:
        return False

    POSTGRES_TOOLS_INSTANCE.disconnect()
    POSTGRES_TOOLS_INSTANCE.delete_database()
    POSTGRES_TOOLS_INSTANCE = None
    return True
