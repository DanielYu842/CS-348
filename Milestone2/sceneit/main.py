from fastapi import FastAPI, HTTPException
import psycopg2
from typing import Optional, List
from queries.create_tables import CREATE_TABLES_SQL
from static.vars import MOVIES_CSV_PATH, USERS_CSV_PATH,REVIEWS_CSV_PATH
from utils.insert_data import insert_movies, insert_users, insert_reviews
from utils.db import get_db_connection
import psycopg2.extras
from pydantic import BaseModel
from datetime import date

app = FastAPI()
update_tables = True

def setup_database():
    conn = get_db_connection()
    cur = conn.cursor()
    
    
    if update_tables:
        print("Dropping all tables")
        cur.execute("Drop table if exists Movie cascade; Drop table if exists Users cascade; Drop table if exists reviews cascade;")
    cur.execute(CREATE_TABLES_SQL)
    conn.commit()
    insert_movies(MOVIES_CSV_PATH)
    insert_users(USERS_CSV_PATH)
    insert_reviews(REVIEWS_CSV_PATH)
    cur.close()
    conn.close()

setup_database()

# Request/Response Models
class MovieCreate(BaseModel):
    title: str
    info: Optional[str] = None
    critics_consensus: Optional[str] = None
    rating: Optional[str] = None
    in_theaters_date: Optional[date] = None
    on_streaming_date: Optional[date] = None
    runtime_in_minutes: Optional[int] = None
    tomatometer_status: Optional[str] = None
    tomatometer_rating: Optional[int] = None
    tomatometer_count: Optional[int] = None
    audience_rating: Optional[int] = None
    audience_count: Optional[int] = None
    genres: List[str] = []
    writers: List[str] = []
    actors: List[str] = []
    studios: List[str] = []
    directors: List[str] = []

class MovieUpdate(MovieCreate):
    pass

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


@app.get("/reviews/search")
def search_comments_by_movie_id(movie_id: int):
    query = f"SELECT * FROM Reviews join (Select user_id, username, email from Users) Users on Reviews.user_id = Users.user_id where movie_id = {movie_id}"
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(query)
                rows = cur.fetchall()
                return {
                    "count": len(rows),
                    "results": rows
                }
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
            
@app.get("/movies/search")
def search_movies(
    title: Optional[str] = None,
    genres: Optional[List[str]] = None,
    writers: Optional[List[str]] = None,
    actors: Optional[List[str]] = None,
    studios: Optional[List[str]] = None,
    directors: Optional[List[str]] = None,
    year: Optional[int] = None
):
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                query = """
                    WITH matched_movies AS (
                        SELECT DISTINCT m.*
                        FROM Movie m
                        LEFT JOIN MovieGenre mg ON m.movie_id = mg.movie_id
                        LEFT JOIN Genre g ON mg.genre_id = g.genre_id
                        LEFT JOIN MovieWriter mw ON m.movie_id = mw.movie_id
                        LEFT JOIN Writer w ON mw.writer_id = w.writer_id
                        LEFT JOIN MovieActor ma ON m.movie_id = ma.movie_id
                        LEFT JOIN Actor a ON ma.actor_id = a.actor_id
                        LEFT JOIN MovieStudio ms ON m.movie_id = ms.movie_id
                        LEFT JOIN Studio s ON ms.studio_id = s.studio_id
                        LEFT JOIN MovieDirector md ON m.movie_id = md.movie_id
                        LEFT JOIN Director d ON md.director_id = d.director_id
                        WHERE 1=1
                """
                params = []

                if title:
                    query += " AND m.title ~* %s"
                    params.append(title)

                if genres:
                    genre_conditions = []
                    for genre in genres:
                        genre_conditions.append("g.name ~* %s")
                        params.append(genre)
                    if genre_conditions:
                        query += f" AND ({' OR '.join(genre_conditions)})"

                if writers:
                    writer_conditions = []
                    for writer in writers:
                        writer_conditions.append("w.name ~* %s")
                        params.append(writer)
                    if writer_conditions:
                        query += f" AND ({' OR '.join(writer_conditions)})"

                if actors:
                    actor_conditions = []
                    for actor in actors:
                        actor_conditions.append("a.name ~* %s")
                        params.append(actor)
                    if actor_conditions:
                        query += f" AND ({' OR '.join(actor_conditions)})"

                if studios:
                    studio_conditions = []
                    for studio in studios:
                        studio_conditions.append("s.name ~* %s")
                        params.append(studio)
                    if studio_conditions:
                        query += f" AND ({' OR '.join(studio_conditions)})"

                if directors:
                    director_conditions = []
                    for director in directors:
                        director_conditions.append("d.name ~* %s")
                        params.append(director)
                    if director_conditions:
                        query += f" AND ({' OR '.join(director_conditions)})"

                if year:
                    query += " AND EXTRACT(YEAR FROM m.in_theaters_date) = %s"
                    params.append(year)

                query += """
                    )
                    SELECT 
                        m.*,
                        ARRAY_AGG(DISTINCT g.name) FILTER (WHERE g.name IS NOT NULL) as genres,
                        ARRAY_AGG(DISTINCT w.name) FILTER (WHERE w.name IS NOT NULL) as writers,
                        ARRAY_AGG(DISTINCT a.name) FILTER (WHERE a.name IS NOT NULL) as actors,
                        ARRAY_AGG(DISTINCT s.name) FILTER (WHERE s.name IS NOT NULL) as studios,
                        ARRAY_AGG(DISTINCT d.name) FILTER (WHERE d.name IS NOT NULL) as directors
                    FROM matched_movies m
                    LEFT JOIN MovieGenre mg ON m.movie_id = mg.movie_id
                    LEFT JOIN Genre g ON mg.genre_id = g.genre_id
                    LEFT JOIN MovieWriter mw ON m.movie_id = mw.movie_id
                    LEFT JOIN Writer w ON mw.writer_id = w.writer_id
                    LEFT JOIN MovieActor ma ON m.movie_id = ma.movie_id
                    LEFT JOIN Actor a ON ma.actor_id = a.actor_id
                    LEFT JOIN MovieStudio ms ON m.movie_id = ms.movie_id
                    LEFT JOIN Studio s ON ms.studio_id = s.studio_id
                    LEFT JOIN MovieDirector md ON m.movie_id = md.movie_id
                    LEFT JOIN Director d ON md.director_id = d.director_id
                    GROUP BY m.movie_id, m.title, m.info, m.critics_consensus, 
                             m.rating, m.in_theaters_date, m.on_streaming_date,
                             m.runtime_in_minutes, m.tomatometer_status,
                             m.tomatometer_rating, m.tomatometer_count,
                             m.audience_rating, m.audience_count
                    ORDER BY m.title 
                    LIMIT 50
                """

                cur.execute(query, params)
                rows = cur.fetchall()

                return {
                    "count": len(rows),
                    "results": rows
                }

    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/movies/", status_code=201)
def create_movie(movie: MovieCreate):
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                # Insert movie
                cur.execute("""
                    INSERT INTO Movie (title, info, critics_consensus, rating, 
                                     in_theaters_date, on_streaming_date, runtime_in_minutes,
                                     tomatometer_status, tomatometer_rating, tomatometer_count,
                                     audience_rating, audience_count)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING movie_id
                """, (movie.title, movie.info, movie.critics_consensus, movie.rating,
                     movie.in_theaters_date, movie.on_streaming_date, movie.runtime_in_minutes,
                     movie.tomatometer_status, movie.tomatometer_rating, movie.tomatometer_count,
                     movie.audience_rating, movie.audience_count))
                
                movie_id = cur.fetchone()['movie_id']

                # Insert related entities and relationships
                for genre in movie.genres:
                    cur.execute("INSERT INTO Genre (name) VALUES (%s) ON CONFLICT (name) DO NOTHING RETURNING genre_id", (genre,))
                    result = cur.fetchone()
                    if result:
                        genre_id = result['genre_id']
                    else:
                        cur.execute("SELECT genre_id FROM Genre WHERE name = %s", (genre,))
                        genre_id = cur.fetchone()['genre_id']
                    cur.execute("INSERT INTO MovieGenre (movie_id, genre_id) VALUES (%s, %s)", (movie_id, genre_id))

                # Similar process for writers, actors, studios, directors
                for writer in movie.writers:
                    cur.execute("INSERT INTO Writer (name) VALUES (%s) ON CONFLICT (name) DO NOTHING RETURNING writer_id", (writer,))
                    result = cur.fetchone()
                    if result:
                        writer_id = result['writer_id']
                    else:
                        cur.execute("SELECT writer_id FROM Writer WHERE name = %s", (writer,))
                        writer_id = cur.fetchone()['writer_id']
                    cur.execute("INSERT INTO MovieWriter (movie_id, writer_id) VALUES (%s, %s)", (movie_id, writer_id))

                for actor in movie.actors:
                    cur.execute("INSERT INTO Actor (name) VALUES (%s) ON CONFLICT (name) DO NOTHING RETURNING actor_id", (actor,))
                    result = cur.fetchone()
                    if result:
                        actor_id = result['actor_id']
                    else:
                        cur.execute("SELECT actor_id FROM Actor WHERE name = %s", (actor,))
                        actor_id = cur.fetchone()['actor_id']
                    cur.execute("INSERT INTO MovieActor (movie_id, actor_id) VALUES (%s, %s)", (movie_id, actor_id))

                for studio in movie.studios:
                    cur.execute("INSERT INTO Studio (name) VALUES (%s) ON CONFLICT (name) DO NOTHING RETURNING studio_id", (studio,))
                    result = cur.fetchone()
                    if result:
                        studio_id = result['studio_id']
                    else:
                        cur.execute("SELECT studio_id FROM Studio WHERE name = %s", (studio,))
                        studio_id = cur.fetchone()['studio_id']
                    cur.execute("INSERT INTO MovieStudio (movie_id, studio_id) VALUES (%s, %s)", (movie_id, studio_id))

                for director in movie.directors:
                    cur.execute("INSERT INTO Director (name) VALUES (%s) ON CONFLICT (name) DO NOTHING RETURNING director_id", (director,))
                    result = cur.fetchone()
                    if result:
                        director_id = result['director_id']
                    else:
                        cur.execute("SELECT director_id FROM Director WHERE name = %s", (director,))
                        director_id = cur.fetchone()['director_id']
                    cur.execute("INSERT INTO MovieDirector (movie_id, director_id) VALUES (%s, %s)", (movie_id, director_id))

                conn.commit()

                # Return the created movie with all relationships
                return get_movie(movie_id)

    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/movies/{movie_id}")
def get_movie(movie_id: int):
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                query = """
                    SELECT 
                        m.*,
                        ARRAY_AGG(DISTINCT g.name) FILTER (WHERE g.name IS NOT NULL) as genres,
                        ARRAY_AGG(DISTINCT w.name) FILTER (WHERE w.name IS NOT NULL) as writers,
                        ARRAY_AGG(DISTINCT a.name) FILTER (WHERE a.name IS NOT NULL) as actors,
                        ARRAY_AGG(DISTINCT s.name) FILTER (WHERE s.name IS NOT NULL) as studios,
                        ARRAY_AGG(DISTINCT d.name) FILTER (WHERE d.name IS NOT NULL) as directors
                    FROM Movie m
                    LEFT JOIN MovieGenre mg ON m.movie_id = mg.movie_id
                    LEFT JOIN Genre g ON mg.genre_id = g.genre_id
                    LEFT JOIN MovieWriter mw ON m.movie_id = mw.movie_id
                    LEFT JOIN Writer w ON mw.writer_id = w.writer_id
                    LEFT JOIN MovieActor ma ON m.movie_id = ma.movie_id
                    LEFT JOIN Actor a ON ma.actor_id = a.actor_id
                    LEFT JOIN MovieStudio ms ON m.movie_id = ms.movie_id
                    LEFT JOIN Studio s ON ms.studio_id = s.studio_id
                    LEFT JOIN MovieDirector md ON m.movie_id = md.movie_id
                    LEFT JOIN Director d ON md.director_id = d.director_id
                    WHERE m.movie_id = %s
                    GROUP BY m.movie_id, m.title, m.info, m.critics_consensus, 
                             m.rating, m.in_theaters_date, m.on_streaming_date,
                             m.runtime_in_minutes, m.tomatometer_status,
                             m.tomatometer_rating, m.tomatometer_count,
                             m.audience_rating, m.audience_count
                """
                cur.execute(query, (movie_id,))
                movie = cur.fetchone()
                
                if movie is None:
                    raise HTTPException(status_code=404, detail="Movie not found")
                
                return movie

    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.put("/movies/{movie_id}")
def update_movie(movie_id: int, movie: MovieUpdate):
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                # Check if movie exists
                cur.execute("SELECT movie_id FROM Movie WHERE movie_id = %s", (movie_id,))
                if cur.fetchone() is None:
                    raise HTTPException(status_code=404, detail="Movie not found")

                # Update movie details
                cur.execute("""
                    UPDATE Movie 
                    SET title = %s, info = %s, critics_consensus = %s, rating = %s,
                        in_theaters_date = %s, on_streaming_date = %s, runtime_in_minutes = %s,
                        tomatometer_status = %s, tomatometer_rating = %s, tomatometer_count = %s,
                        audience_rating = %s, audience_count = %s
                    WHERE movie_id = %s
                """, (movie.title, movie.info, movie.critics_consensus, movie.rating,
                     movie.in_theaters_date, movie.on_streaming_date, movie.runtime_in_minutes,
                     movie.tomatometer_status, movie.tomatometer_rating, movie.tomatometer_count,
                     movie.audience_rating, movie.audience_count, movie_id))

                # Delete existing relationships
                cur.execute("DELETE FROM MovieGenre WHERE movie_id = %s", (movie_id,))
                cur.execute("DELETE FROM MovieWriter WHERE movie_id = %s", (movie_id,))
                cur.execute("DELETE FROM MovieActor WHERE movie_id = %s", (movie_id,))
                cur.execute("DELETE FROM MovieStudio WHERE movie_id = %s", (movie_id,))
                cur.execute("DELETE FROM MovieDirector WHERE movie_id = %s", (movie_id,))

                # Insert new relationships (same code as create endpoint)
                # ... (insert code for genres, writers, actors, studios, directors) ...

                conn.commit()
                return get_movie(movie_id)

    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: int):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Check if movie exists
                cur.execute("SELECT movie_id FROM Movie WHERE movie_id = %s", (movie_id,))
                if cur.fetchone() is None:
                    raise HTTPException(status_code=404, detail="Movie not found")

                # Delete relationships first
                cur.execute("DELETE FROM MovieGenre WHERE movie_id = %s", (movie_id,))
                cur.execute("DELETE FROM MovieWriter WHERE movie_id = %s", (movie_id,))
                cur.execute("DELETE FROM MovieActor WHERE movie_id = %s", (movie_id,))
                cur.execute("DELETE FROM MovieStudio WHERE movie_id = %s", (movie_id,))
                cur.execute("DELETE FROM MovieDirector WHERE movie_id = %s", (movie_id,))

                # Delete the movie
                cur.execute("DELETE FROM Movie WHERE movie_id = %s", (movie_id,))
                conn.commit()

                return {"message": "Movie deleted successfully"}

    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")