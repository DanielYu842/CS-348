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