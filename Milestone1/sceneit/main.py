from fastapi import FastAPI
from queries.create_tables import CREATE_TABLES_SQL
from static.vars import MOVIES_CSV_PATH
from utils.insert_data import insert_movies
from utils.db import get_db_connection

app = FastAPI()

def setup_database():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute(CREATE_TABLES_SQL)
    conn.commit()

    insert_movies(MOVIES_CSV_PATH)

    cur.close()
    conn.close()

setup_database()


@app.get("/")
def read_root():
    return {"message": "hello world sceneit"}

@app.get("/data/{table_name}")
def get_table_data(table_name: str):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                query = f"SELECT * FROM {table_name};"  # Using parameterized table name
                cur.execute(query)
                rows = cur.fetchall()
                columns = [desc[0] for desc in cur.description]

        return [dict(zip(columns, row)) for row in rows]  # Convert to list of dictionaries

    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Error fetching values: {e}")