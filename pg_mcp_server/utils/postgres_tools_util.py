import uuid
import psycopg2
from psycopg2 import OperationalError, ProgrammingError
import subprocess

PG_TRIALS = 5

class Postgres_Tools:
    def __init__(self, pg_dump_file):
        self.db_name = f"tmp_{uuid.uuid4().hex[:8]}"
        self.pg_dump_file = pg_dump_file
        self.conn = None
        self.cur = None
        self.database_exists = False

    def create_database(self):
        try:
            subprocess.check_call(['createdb', self.db_name])
            subprocess.check_call(['psql', self.db_name, '-f', self.pg_dump_file])
        except subprocess.CalledProcessError as e:
            print(f"Database creation or import failed: {e}")
            return False
        self.database_exists = True
        return True

    def connect(self):
        i = 0
        while not self.database_exists and i < PG_TRIALS:
            self.database_exists = self.create_database()
            i += 1
        try:
            self.conn = psycopg2.connect(dbname=self.db_name)
            self.cur = self.conn.cursor()
        except OperationalError as e:
            print(f"Failed to connect to database: {e}")
            return False
        return True

    def verify_database(self):
        try:
            if self.cur is None:
                print("No database connection to verify.")
                return False
            self.cur.execute("SELECT 1;")
            return self.cur.fetchone() == (1,)
        except (OperationalError, ProgrammingError) as e:
            print(f"Database verification failed: {e}")
            return False

    def query(self, sql):
        if not self.database_exists or not self.verify_database():
            print("Database does not exist or is not verified.")
            return None
        try:
            self.cur.execute(sql)
            return self.cur.fetchall()
        except Exception as e:
            print(f"Query failed: {e}")
            return None

    def disconnect(self):
        if not self.database_exists:
            print("No active database connection to disconnect.")
            return
        try:
            if self.cur:
                self.cur.close()
            if self.conn:
                self.conn.close()
        except Exception as e:
            print(f"Error during disconnect: {e}")

    def delete_database(self):
        try:
            subprocess.check_call(['dropdb', self.db_name])
            self.database_exists = False
            print(f"Database {self.db_name} deleted successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to delete database: {e}")
    
