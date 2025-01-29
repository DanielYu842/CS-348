import psycopg2
from psycopg2.extensions import connection

connection_params = {
    "dbname": "test_db",
    "user": "postgres",
    "password": "passcode",
    "host": "db",
    "port": "5432"
}

def get_db_connection() -> connection:
    try:
        conn = psycopg2.connect(**connection_params)
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        raise
