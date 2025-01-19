from typing import Union

from fastapi import FastAPI

app = FastAPI()


import psycopg2

# Define connection parameters
connection_params = {
    "dbname": "test_db",
    "user": "postgres",
    "password": "passcode",
    "host": "postgres",  # e.g., "localhost" or an IP address
    "port": "5432"        # Default PostgreSQL port
}

try:
    # Establish the connection
    conn = psycopg2.connect(**connection_params)
    print("Connection to the database was successful.")

    # Create a cursor object
    cur = conn.cursor()

    # Execute an SQL query
    cur.execute("SELECT version();")

    # Fetch the result
    db_version = cur.fetchone()
    print(f"PostgreSQL version: {db_version}")

    # Close the cursor and connection
    cur.close()
    conn.close()

except psycopg2.Error as e:
    print(f"Error connecting to PostgreSQL: {e}")

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}