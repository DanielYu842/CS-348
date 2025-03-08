from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from typing import Optional, List
from queries.create_tables import CREATE_TABLES_SQL
from static.vars import MOVIES_CSV_PATH, USERS_CSV_PATH,REVIEWS_CSV_PATH
from utils.insert_data import insert_movies, insert_users, insert_reviews
from utils.db import get_db_connection
import psycopg2.extras
from pydantic import BaseModel
from datetime import date
from fastapi import FastAPI, HTTPException
import psycopg2
import psycopg2.extras
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from utils.db import get_db_connection
from datetime import datetime
import random

update_tables = True
from enum import Enum


app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)
class LikeCreate(BaseModel):
    user_id: int
    review_id: Optional[int] = None
    comment_id: Optional[int] = None

@app.post("/likes/")
def like_item(like: LikeCreate):
    if not like.review_id and not like.comment_id:
        raise HTTPException(status_code=400, detail="Must provide either review_id or comment_id")
    if like.review_id and like.comment_id:
        raise HTTPException(status_code=400, detail="Cannot like both a review and a comment at the same time")

    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                # Check if user exists
                cur.execute("SELECT user_id FROM Users WHERE user_id = %s", (like.user_id,))
                if cur.fetchone() is None:
                    raise HTTPException(status_code=404, detail="User not found")

                if like.review_id:
                    # Check if review exists
                    cur.execute("SELECT review_id FROM Reviews WHERE review_id = %s", (like.review_id,))
                    if cur.fetchone() is None:
                        raise HTTPException(status_code=404, detail="Review not found")

                    # Check if user already liked this review
                    cur.execute("SELECT like_id FROM Likes WHERE user_id = %s AND review_id = %s", (like.user_id, like.review_id))
                    if cur.fetchone():
                        raise HTTPException(status_code=400, detail="User has already liked this review")

                    # Insert like for review
                    cur.execute("""
                        INSERT INTO Likes (user_id, review_id, created_at) 
                        VALUES (%s, %s, NOW()) 
                        RETURNING like_id, user_id, review_id, created_at
                    """, (like.user_id, like.review_id))

                elif like.comment_id:
                    # Check if comment exists
                    cur.execute("SELECT comment_id FROM Comments WHERE comment_id = %s", (like.comment_id,))
                    if cur.fetchone() is None:
                        raise HTTPException(status_code=404, detail="Comment not found")

                    # Check if user already liked this comment
                    cur.execute("SELECT like_id FROM Likes WHERE user_id = %s AND comment_id = %s", (like.user_id, like.comment_id))
                    if cur.fetchone():
                        raise HTTPException(status_code=400, detail="User has already liked this comment")

                    # Insert like for comment
                    cur.execute("""
                        INSERT INTO Likes (user_id, comment_id, created_at) 
                        VALUES (%s, %s, NOW()) 
                        RETURNING like_id, user_id, comment_id, created_at
                    """, (like.user_id, like.comment_id))

                new_like = cur.fetchone()
                return new_like

    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


class ReviewCreate(BaseModel):
    movie_id: int
    user_id: int
    title: str
    content: str
    rating: float  # Rating should be between 0 and 100


@app.post("/reviews/")
def create_review(review: ReviewCreate):
    if not (0 <= review.rating <= 100):
        raise HTTPException(status_code=400, detail="Rating must be between 0 and 100")

    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                # Check if movie exists
                cur.execute("SELECT movie_id FROM Movie WHERE movie_id = %s", (review.movie_id,))
                if cur.fetchone() is None:
                    raise HTTPException(status_code=404, detail="Movie not found")

                # Check if user exists
                cur.execute("SELECT user_id FROM Users WHERE user_id = %s", (review.user_id,))
                if cur.fetchone() is None:
                    raise HTTPException(status_code=404, detail="User not found")

                # Insert the review
                cur.execute("""
                    INSERT INTO Reviews (movie_id, user_id, title, content, rating, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
                    RETURNING review_id, movie_id, user_id, title, content, rating, created_at, updated_at
                """, (review.movie_id, review.user_id, review.title, review.content, review.rating))

                new_review = cur.fetchone()
                return new_review

    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

def setup_database():
    conn = get_db_connection()
    cur = conn.cursor()
    
    
    if update_tables:
        print("Dropping all tables")
        cur.execute("Drop table if exists Movie cascade; Drop table if exists Users cascade; Drop table if exists reviews cascade; Drop table if exists Likes cascade")
    cur.execute(CREATE_TABLES_SQL)
    conn.commit()
    insert_movies(MOVIES_CSV_PATH)
    insert_users(USERS_CSV_PATH)
    insert_reviews(REVIEWS_CSV_PATH)
    create_review(ReviewCreate(movie_id=1,user_id=3,title="Great Movie!",content="I really enjoyed the cinematography and the story.",rating=85.5))

    repeats = []
    for _ in range(50):
        id = random.randint(1, 10)
        rid = random.randint(1, 10)
        data =LikeCreate(
            user_id=id,  # user_id from 1 to 10
            review_id=rid,  # review_id from 1 to 10
            comment_id=None  # comment_id is set to None
        )
        if (id,rid) in repeats: continue
        repeats.append((id,rid))
        like_item(data)


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
    # Note to self:
    # should return review_id's instead, then have a function that takes a review_id and gets all the information about the review
    # Eg - review likes, replies to the review, rating, etc
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
    genres: Optional[List[str]] = Query(None),
    writers: Optional[List[str]] = Query(None),
    actors: Optional[List[str]] = Query(None),
    studios: Optional[List[str]] = Query(None),
    directors: Optional[List[str]] = Query(None),
    year: Optional[int] = None,
    rating: Optional[str] = None
):
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                # Build base query
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
                WHERE 1=1
                """
                
                params = []
                
                if title:
                    query += " AND m.title ILIKE %s"
                    params.append(f"%{title}%")
                
                if genres:
                    for genre in genres:
                        query += """ 
                        AND EXISTS (
                            SELECT 1 
                            FROM MovieGenre mg_inner 
                            JOIN Genre g_inner ON mg_inner.genre_id = g_inner.genre_id 
                            WHERE mg_inner.movie_id = m.movie_id 
                            AND g_inner.name ILIKE %s
                        )
                        """
                        params.append(f"%{genre}%")
                
                if writers:
                    for writer in writers:
                        query += """ 
                        AND EXISTS (
                            SELECT 1 
                            FROM MovieWriter mw_inner 
                            JOIN Writer w_inner ON mw_inner.writer_id = w_inner.writer_id 
                            WHERE mw_inner.movie_id = m.movie_id 
                            AND w_inner.name ILIKE %s
                        )
                        """
                        params.append(f"%{writer}%")
                
                if actors:
                    for actor in actors:
                        query += """ 
                        AND EXISTS (
                            SELECT 1 
                            FROM MovieActor ma_inner 
                            JOIN Actor a_inner ON ma_inner.actor_id = a_inner.actor_id 
                            WHERE ma_inner.movie_id = m.movie_id 
                            AND a_inner.name ILIKE %s
                        )
                        """
                        params.append(f"%{actor}%")
                
                if year:
                    query += " AND EXTRACT(YEAR FROM m.in_theaters_date) = %s"
                    params.append(year)

                if rating:
                    query += " AND m.rating ~* %s"
                    params.append(rating)

                if studios:
                    for studio in studios:
                        query += """ 
                        AND EXISTS (
                            SELECT 1 
                            FROM MovieStudio ms_inner 
                            JOIN Studio s_inner ON ms_inner.studio_id = s_inner.studio_id 
                            WHERE ms_inner.movie_id = m.movie_id 
                            AND s_inner.name ILIKE %s
                        )
                        """
                        params.append(f"%{studio}%")
                
                if directors:
                    for director in directors:
                        query += """ 
                        AND EXISTS (
                            SELECT 1 
                            FROM MovieDirector md_inner 
                            JOIN Director d_inner ON md_inner.director_id = d_inner.director_id 
                            WHERE md_inner.movie_id = m.movie_id 
                            AND d_inner.name ILIKE %s
                        )
                        """
                        params.append(f"%{director}%")
                
                # Add group by and ordering
                query += """
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


@app.get("/user_profile/{user_id}/user_liked")
def get_liked_reviews_and_comments(user_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT review_id, comment_id FROM Likes
        WHERE user_id = %s
        """
        cursor.execute(query, (user_id,))
        likes = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Separate review IDs and comment IDs
        review_ids = [like[0] for like in likes if like[0] is not None]
        comment_ids = [like[1] for like in likes if like[1] is not None]
        
        return {"review_ids": review_ids, "comment_ids": comment_ids}
    
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

from utils.review_info import get_review_info
from utils.user_profile import review_ids_from_user

@app.get("/user_profile/{user_id}/user_reviews")
def get_reviews_from_user(user_id: int):
    try:
        # Fetch review IDs for the given user
        review_ids = review_ids_from_user(user_id)
        # print(review_ids)
        # If no reviews are found, return a message
        if not review_ids:
            return {"message": "No reviews found for this user."}

        # Fetch detailed review information for each review_id
        reviews_data = []
        for review_id in review_ids:
            # print('here', review_id)
            review_info = get_review_info(review_id)
            reviews_data.append(review_info)

        return {"count": len(reviews_data), "results": reviews_data}
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
@app.get("/movies_top")
def get_movies_by_rating(best: bool = True):
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                query = f"""
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
                WHERE m.audience_rating IS NOT NULL
                GROUP BY m.movie_id
                ORDER BY m.audience_rating {"DESC" if best else "ASC"}
                LIMIT 10
                """

                cur.execute(query)
                rows = cur.fetchall()

                return {
                    "count": len(rows),
                    "results": rows
                }
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    
# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

@app.post("/users/signup")
def create_user(user: UserCreate):
    try:
        hashed_password = pwd_context.hash(user.password)

        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    INSERT INTO Users (username, email, password_hash, created_at, updated_at) 
                    VALUES (%s, %s, %s, NOW(), NOW()) 
                    RETURNING user_id, username, email, created_at
                """, (user.username, user.email, hashed_password))

                new_user = cur.fetchone()
                return new_user

    except psycopg2.errors.UniqueViolation:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/users/login")
def login_user(user: UserLogin):
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT user_id, username, email, password_hash FROM Users WHERE email = %s", (user.email,))
                db_user = cur.fetchone()

                if not db_user or not pwd_context.verify(user.password, db_user["password_hash"]):
                    return {"success": False, "message": "Invalid credentials"}

                return {"success": True, "user": {"user_id": db_user["user_id"], "username": db_user["username"], "email": db_user["email"]}}

    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


class CommentCreate(BaseModel):
    review_id: int
    user_id: int
    content: str

@app.post("/comments/")
def create_comment(comment: CommentCreate):
    if not comment.content.strip():
        raise HTTPException(status_code=400, detail="Comment content cannot be empty")

    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT review_id FROM Reviews WHERE review_id = %s", (comment.review_id,))
                if cur.fetchone() is None:
                    raise HTTPException(status_code=404, detail="Review not found")

                cur.execute("SELECT user_id FROM Users WHERE user_id = %s", (comment.user_id,))
                if cur.fetchone() is None:
                    raise HTTPException(status_code=404, detail="User not found")

                cur.execute("""
                    INSERT INTO Comments (review_id, user_id, content, created_at, updated_at)
                    VALUES (%s, %s, %s, NOW(), NOW())
                    RETURNING comment_id, review_id, user_id, content, created_at, updated_at
                """, (comment.review_id, comment.user_id, comment.content))

                new_comment = cur.fetchone()
                return new_comment

    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    

@app.get("/movies_top_reviewed")
def get_top_reviewed_movies():
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                # query = """
                # with groupedReviews as (
                # select movie_id, count(*) as reviewCount from reviews group by movie_id order by reviewCount desc limit 10
                # )

                # select * from groupedReviews;
                # """

                query = f"""

                with groupedReviews as (
                select movie_id, count(*) as reviewCount from reviews group by movie_id order by reviewCount desc limit 10
                )

                SELECT 
                    m.*,
                    groupedReviews.reviewCount,
                    ARRAY_AGG(DISTINCT g.name) FILTER (WHERE g.name IS NOT NULL) as genres,
                    ARRAY_AGG(DISTINCT w.name) FILTER (WHERE w.name IS NOT NULL) as writers,
                    ARRAY_AGG(DISTINCT a.name) FILTER (WHERE a.name IS NOT NULL) as actors,
                    ARRAY_AGG(DISTINCT s.name) FILTER (WHERE s.name IS NOT NULL) as studios,
                    ARRAY_AGG(DISTINCT d.name) FILTER (WHERE d.name IS NOT NULL) as directors
                FROM Movie m
                inner join groupedReviews on groupedReviews.movie_id = m.movie_id
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
                WHERE m.audience_rating IS NOT NULL
                GROUP BY m.movie_id,groupedReviews.reviewCount
                order by groupedReviews.reviewCount desc;
                """
                
                cur.execute(query)
                rows = cur.fetchall()

                return {
                    "count": len(rows),
                    "results": rows
                }

    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/users/top_likes")
def get_top_users_by_likes():
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                query = """
                SELECT 
                    u.username, 
                    COUNT(*) AS total_likes
                FROM Users u
                inner join Likes l ON u.user_id = l.user_id
                GROUP BY u.user_id
                ORDER BY total_likes DESC
                LIMIT 10;
                """
                cur.execute(query)
                rows = cur.fetchall()

                return {
                    "count": len(rows),
                    "results": rows
                }

    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    

@app.get("/reviews/{review_id}")
def get_review_with_comments(review_id: int):
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                # Fetch review details along with like count
                cur.execute("""
                    SELECT 
                        r.review_id, r.movie_id, r.user_id, r.title, r.content, r.rating, 
                        r.created_at, r.updated_at,
                        u.username, u.email,
                        COALESCE(like_count.likes, 0) AS like_count
                    FROM Reviews r
                    JOIN Users u ON r.user_id = u.user_id
                    LEFT JOIN (
                        SELECT review_id, COUNT(*) AS likes
                        FROM Likes 
                        WHERE review_id IS NOT NULL
                        GROUP BY review_id
                    ) like_count ON r.review_id = like_count.review_id
                    WHERE r.review_id = %s
                """, (review_id,))
                
                review = cur.fetchone()
                
                if not review:
                    raise HTTPException(status_code=404, detail="Review not found")

                # Fetch all comments with like count for each comment
                cur.execute("""
                    SELECT 
                        c.comment_id, c.review_id, c.user_id, c.content, c.created_at, c.updated_at,
                        u.username, u.email,
                        COALESCE(like_count.likes, 0) AS like_count
                    FROM Comments c
                    JOIN Users u ON c.user_id = u.user_id
                    LEFT JOIN (
                        SELECT comment_id, COUNT(*) AS likes
                        FROM Likes 
                        WHERE comment_id IS NOT NULL
                        GROUP BY comment_id
                    ) like_count ON c.comment_id = like_count.comment_id
                    WHERE c.review_id = %s
                    ORDER BY c.created_at ASC
                """, (review_id,))

                comments = cur.fetchall()

                return {
                    "review": review,
                    "comments": comments
                }

    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


class ReviewSortOptions(str, Enum):
    created_at = "created_at"
    most_comments = "most_comments"


@app.get("/reviews/")
def get_all_reviews(sort_by: ReviewSortOptions = ReviewSortOptions.created_at):
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                # Base query to fetch reviews with like and comment count
                query = """
                    SELECT 
                        r.review_id, r.movie_id, r.user_id, r.title, r.content, r.rating, 
                        r.created_at, r.updated_at,
                        u.username, u.email,
                        COALESCE(like_count.likes, 0) AS like_count,
                        COALESCE(comment_count.comments, 0) AS comment_count
                    FROM Reviews r
                    JOIN Users u ON r.user_id = u.user_id
                    LEFT JOIN (
                        SELECT review_id, COUNT(*) AS likes
                        FROM Likes 
                        WHERE review_id IS NOT NULL
                        GROUP BY review_id
                    ) like_count ON r.review_id = like_count.review_id
                    LEFT JOIN (
                        SELECT review_id, COUNT(*) AS comments
                        FROM Comments 
                        GROUP BY review_id
                    ) comment_count ON r.review_id = comment_count.review_id
                """

                if sort_by == ReviewSortOptions.created_at:
                    query += " ORDER BY r.created_at DESC"
                elif sort_by == ReviewSortOptions.most_comments:
                    query += " ORDER BY COALESCE(comment_count.comments, 0) DESC, r.created_at DESC"

                cur.execute(query)
                reviews = cur.fetchall()

                return {"count": len(reviews), "reviews": reviews}

    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")