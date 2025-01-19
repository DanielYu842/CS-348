from typing import Union, List, Dict

from fastapi import FastAPI, HTTPException
from queries.seed import GET_SEED_VALUES

app = FastAPI()


import psycopg2

# Define connection parameters
connection_params = {
    "dbname": "test_db",
    "user": "postgres",
    "password": "passcode",
    "host": "db",
    "port": "5432"
}

def get_db_connection():
    try:
        conn = psycopg2.connect(**connection_params)
        return conn
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to the database: {e}")

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/values")
def get_values() -> List[Dict[str, Union[int, str]]]:
    conn = get_db_connection()
    try:
        cur = conn.cursor()

        cur.execute(GET_SEED_VALUES)

        rows = cur.fetchall()

        cur.close()
        conn.close()

        return [{"id": row[0], "name": row[1], "value": row[2]} for row in rows]

    except psycopg2.Error as e: 
        raise HTTPException(status_code=500, detail=f"Error fetching values: {e}") 