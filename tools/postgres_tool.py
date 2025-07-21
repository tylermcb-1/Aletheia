from pydantic import BaseModel
import subprocess
import time
import sys
import psycopg2

# constants that are (possibly) temporary
DB_NAME = "aletheia_db"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_PORT = "5432"
CONTAINER_NAME = "aletheia_postgres"

class PostgresImport(BaseModel):
    pg_dump_path: str


def postgres_tool(input_data: PostgresImport) -> str:
    """
    Example tool that echoes a message.
    """


    return "tbd"


def init_pg_dump_file(pg_dump_path: str):
    """
    Initialize the pg_dump file by creating a PostgreSQL database and user.
    """
    try:
        # start postgres docker container
        subprocess.run([
            "docker", "run", "--name", CONTAINER_NAME,
            "-e", f"POSTGRES_PASSWORD={DB_PASSWORD}",
            "-e", f"POSTGRES_DB={DB_NAME}",
            "-p", f"{DB_PORT}:5432", "-d", "--rm", "postgres"
        ], check=True)
        time.sleep(5)  # wait for the container to start

        subprocess.run(["docker", "cp", input_data.pg_dump_path, f"{CONTAINER_NAME}:/dump.sql"], check=True)

        # Restore the dump file to tempdb
        subprocess.run([
            "docker", "exec", "-i", CONTAINER_NAME,
            "psql", "-U", DB_USER, "-d", DB_NAME, "-f", "/dump.sql"
        ], check=True)

        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER,
            password=DB_PASSWORD, host="localhost", port=DB_PORT
        )

        return conn
    except Exception as e:
        subprocess.run(["docker", "stop", CONTAINER_NAME])
        print(f"Error initializing pg_dump file: {e}", file=sys.stderr)

def close_pg_connection(conn):
    """
    Close the PostgreSQL connection.
    """
    if conn:
        conn.close()
    
    subprocess.run(["docker", "stop", CONTAINER_NAME])


