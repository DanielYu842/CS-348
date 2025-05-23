from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from typing import Optional, List
from queries.create_tables import CREATE_TABLES_SQL, CREATE_INDICES_SQL, INFO_TS_VECTOR_TRIGGER, CREATE_MATERIALIZED_VIEW, MATERIALIZED_VIEW_INDEX, REFRESH_MATERIALIZED_VIEW
from queries.reputation import (
    CREATE_REPUTATION_TABLE_SQL,
    CREATE_REPUTATION_TRIGGERS_SQL,
    GET_USER_REPUTATION_SQL,
    GET_USER_REPUTATION_BY_ID_SQL
)
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
from utils.review_info import get_review_info
from utils.user_profile import review_ids_from_user
from utils.batch import batch_handle_related
from enum import Enum

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

update_tables = True


app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

MATERIALIZED_VIEW_NAME = "mv_top_10_reviewed_movies"

scheduler = AsyncIOScheduler()

def sync_refresh_materialized_view():
    """
    Uses get_db_connection to connect and refresh the materialized view.
    APScheduler will run this in a thread pool.
    """
    print(f"[{datetime.now()}] Background Task: Attempting to refresh '{MATERIALIZED_VIEW_NAME}'...")
    try:
        with get_db_connection() as conn:
            conn.autocommit = True

            with conn.cursor() as cur:
                print(f"[{datetime.now()}] Executing: REFRESH MATERIALIZED VIEW {MATERIALIZED_VIEW_NAME};")
                cur.execute(f"REFRESH MATERIALIZED VIEW {MATERIALIZED_VIEW_NAME};")
            print(f"[{datetime.now()}] Background Task: Successfully refreshed '{MATERIALIZED_VIEW_NAME}'.")
    except psycopg2.Error as e:
        print(f"[{datetime.now()}] Background Task Error: Database error during refresh: {e}")
    except Exception as e:
        print(f"[{datetime.now()}] Background Task Error: An unexpected error occurred: {e}")

@app.on_event("startup")
async def startup_event():
    print("Starting scheduler...")
    scheduler.add_job(
        sync_refresh_materialized_view,
        IntervalTrigger(hours=1),
        id="mv_refresh_job",
        replace_existing=True
    )
    scheduler.start()
    print("Scheduler started.")

@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down scheduler...")
    scheduler.shutdown()
    print("Scheduler shut down.")


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

class UserCreate(BaseModel):
    username: str
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

@app.get("/users/{user_id}/liked_movies/{movie_id}", status_code=200)
def check_if_movie_liked(user_id: int, movie_id: int):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                 # Check user exists (optional)
                cur.execute("SELECT 1 FROM Users WHERE user_id = %s", (user_id,))
                if cur.fetchone() is None:
                    raise HTTPException(status_code=404, detail="User not found")
                # Check movie exists (optional)
                cur.execute("SELECT 1 FROM Movie WHERE movie_id = %s", (movie_id,))
                if cur.fetchone() is None:
                    raise HTTPException(status_code=404, detail="Movie not found")

                cur.execute("""
                    SELECT EXISTS (
                        SELECT 1 FROM Liked_Movie
                        WHERE user_id = %s AND movie_id = %s
                    );
                """, (user_id, movie_id))
                is_liked = cur.fetchone()[0] 
                return {"is_liked": is_liked}
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


class LikedMovieInfo(BaseModel):
    movie_id: int
    title: str
    liked_at: datetime 


@app.get("/user_profile/{user_id}/liked_movies", response_model=List[LikedMovieInfo])
def get_user_liked_movies(user_id: int):
    """
    Retrieves a list of movies liked by the specified user.
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                # Check if user exists (optional but good practice)
                cur.execute("SELECT 1 FROM Users WHERE user_id = %s", (user_id,))
                if cur.fetchone() is None:
                    raise HTTPException(status_code=404, detail="User not found")

                query = """
                    SELECT
                        m.movie_id,
                        m.title,
                        lm.liked_at
                    FROM Liked_Movie lm
                    JOIN Movie m ON lm.movie_id = m.movie_id
                    WHERE lm.user_id = %s
                    ORDER BY lm.liked_at DESC; -- Show most recently liked first
                """
                cur.execute(query, (user_id,))
                liked_movies = cur.fetchall()
                return liked_movies # Returns list of dicts matching LikedMovieInfo

    except psycopg2.Error as e:
        print(f"Database error fetching liked movies for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Database error retrieving liked movies.")
    except Exception as e:
        print(f"Unexpected error fetching liked movies for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")


@app.delete("/unlike_movie", status_code=200)
def remove_liked_movie(user_id: int, movie_id: int):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                 # Check user exists (optional, foreign key handles it but good for explicit error)
                cur.execute("SELECT 1 FROM Users WHERE user_id = %s", (user_id,))
                if cur.fetchone() is None:
                    raise HTTPException(status_code=404, detail="User not found")
                # Check movie exists (optional)
                cur.execute("SELECT 1 FROM Movie WHERE movie_id = %s", (movie_id,))
                if cur.fetchone() is None:
                    raise HTTPException(status_code=404, detail="Movie not found")

                cur.execute("""
                    DELETE FROM Liked_Movie
                    WHERE user_id = %s AND movie_id = %s;
                """, (user_id, movie_id))

                if cur.rowcount == 0:
                    # Could mean it wasn't liked, or user/movie doesn't exist (handled above)
                    # Return success regardless, idempotency is fine here
                    return {"message": "Like removed or movie was not liked"}
                conn.commit()
                return {"message": "Movie removed from liked list"}
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.post("/like_movie", status_code=201)
def add_liked_movie(user_id: int, movie_id: int):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Check user exists
                cur.execute("SELECT 1 FROM Users WHERE user_id = %s", (user_id,))
                if cur.fetchone() is None:
                    raise HTTPException(status_code=404, detail="User not found")
                # Check movie exists
                cur.execute("SELECT 1 FROM Movie WHERE movie_id = %s", (movie_id,))
                if cur.fetchone() is None:
                    raise HTTPException(status_code=404, detail="Movie not found")

                cur.execute("""
                    INSERT INTO Liked_Movie (user_id, movie_id, liked_at)
                    VALUES (%s, %s, NOW())
                    ON CONFLICT (user_id, movie_id) DO NOTHING;
                """, (user_id, movie_id))

                if cur.rowcount == 0:
                    # It's not really an error if it already exists, return success
                    return {"message": "Movie already liked by user or like added successfully"}
                conn.commit()
                return {"message": "Movie added to liked list"}
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
@app.post("/watch")
def add_watched_movie(user_id: int, movie_id: int):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO Watched (user_id, movie_id)
                    VALUES (%s, %s)
                    ON CONFLICT (user_id, movie_id) DO NOTHING;
                """, (user_id, movie_id))
                
                if cur.rowcount == 0:
                    return {"message": "Movie already watched by user"}

                return {"message": "Movie added to watched list"}

    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    

class SetupType(str, Enum):
    local = "local"
    prod = "prod"

@app.post("/seed")
def setup_database(setup_type: SetupType):
    conn = get_db_connection()
    cur = conn.cursor()

    sample_size = 50
    if setup_type == SetupType.prod:
        sample_size = 1000
    
    if update_tables:
        print("Dropping all tables")
        cur.execute("DROP TABLE IF EXISTS Liked_Movie CASCADE; Drop table if exists Movie cascade; Drop table if exists Watched cascade; Drop table if exists Users cascade; Drop table if exists reviews cascade; Drop table if exists Likes cascade; Drop table if exists UserReputation cascade;")
    cur.execute(CREATE_TABLES_SQL)
    cur.execute(CREATE_INDICES_SQL)
    cur.execute(INFO_TS_VECTOR_TRIGGER)
    cur.execute(CREATE_REPUTATION_TABLE_SQL)
    cur.execute(CREATE_REPUTATION_TRIGGERS_SQL)
    cur.execute(CREATE_MATERIALIZED_VIEW)
    cur.execute(MATERIALIZED_VIEW_INDEX)
    conn.commit()
    print("inserting movie")
    insert_movies(MOVIES_CSV_PATH, sample_size)
    print("inserting users")
    for i in range(ord('a'), ord('z')+1):
        uname = chr(i) + "@cmail.com"
        pw = uname
        user = UserCreate(username = chr(i), email=uname,password= pw)
        create_user(user)
    print("inserting reviews")
    insert_reviews(REVIEWS_CSV_PATH, sample_size)
    create_review(ReviewCreate(movie_id=1,user_id=1,title="nad Movie!",content="I hate the cinematography and the story.",rating=5.5))
    create_review(ReviewCreate(movie_id=2,user_id=1,title="what the heck!",content="wow, bing.",rating=35.5))
    create_review(ReviewCreate(movie_id=3,user_id=1,title="Great Movie!",content="I really enjoyed the cinematography and the story.",rating=85.5))
    create_review(ReviewCreate(movie_id=4,user_id=1,title="it's ok",content="I real the story.",rating=33.5))

    print("inserting likes")
    repeats = []
    for _ in range(200):
        id = random.randint(1, 10)
        rid = random.randint(1, 49)
        data =LikeCreate(
            user_id=id,  # user_id from 1 to 10
            review_id=rid,  # review_id from 1 to 10
            comment_id=None  # comment_id is set to None
        )
        if (id,rid) in repeats: continue
        repeats.append((id,rid))
        like_item(data)
    print("adding comments")
    for i in range(100):
        reply_to_rid = random.randint(1,10)
        Comment = CommentCreate(review_id = reply_to_rid, user_id = random.randint(1,10), content = 'this is a comment')
        create_comment(Comment)
    print("liking comments")
    repeats = []
    for _ in range(100):
        id = random.randint(1, 10)
        cid = random.randint(1, 10)
        data = LikeCreate(
            user_id=id,  # user_id from 1 to 10
            review_id=None,  
            comment_id=cid
        )
        if (id,cid) in repeats: continue
        repeats.append((id,cid))
        like_item(data)
    
    print("inserting liked")
    add_liked_movie(2, 1)
    add_liked_movie(3, 1)
    add_liked_movie(2, 2)
    add_liked_movie(2, 3)
    add_liked_movie(1, 2)
    add_liked_movie(1, 3)
    add_liked_movie(3, 2)
    add_liked_movie(3, 3)
    add_liked_movie(3, 4)
    add_liked_movie(3, 5)
    # add_liked_movie(3, 6)
    add_liked_movie(4,1)
    add_liked_movie(5,1)
    # add_watched_movie(3,7)

    cur.execute(REFRESH_MATERIALIZED_VIEW)
    conn.commit()


    cur.close()
    conn.close()

    return {"message": "Database setup successful"}
class SimilarUser(BaseModel):
    user_id: int
    username: str
    mutual_count: int

@app.get("/user_profile/{user_id}/similar_likes", response_model=List[SimilarUser])
def get_top_similar_users_by_likes(user_id: int):
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT 1 FROM Users WHERE user_id = %s", (user_id,))
                if cur.fetchone() is None:
                    raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")

                query = """
                    WITH UserLikedCounts AS (
                        SELECT
                            user_id,
                            COUNT(movie_id) AS liked_count
                        FROM Liked_Movie
                        GROUP BY user_id
                    )
                    SELECT
                        other_user.user_id,
                        other_user.username,
                        COUNT(lm1.movie_id) AS mutual_count
                    FROM Liked_Movie lm1
                    JOIN Liked_Movie lm2 ON lm1.movie_id = lm2.movie_id
                                         AND lm1.user_id <> lm2.user_id
                    JOIN Users other_user ON lm2.user_id = other_user.user_id
                    JOIN UserLikedCounts target_count ON lm1.user_id = target_count.user_id
                    JOIN UserLikedCounts other_count ON lm2.user_id = other_count.user_id
                    WHERE
                        lm1.user_id = %s
                        AND other_count.liked_count <= (2 * target_count.liked_count)
                        AND target_count.liked_count <= (2 * other_count.liked_count)
                    GROUP BY
                        other_user.user_id,
                        other_user.username
                    ORDER BY
                        mutual_count DESC,
                        other_user.user_id ASC
                    LIMIT 3;
                """
                cur.execute(query, (user_id,))
                similar_users = cur.fetchall()

                return similar_users

    except psycopg2.Error as e:
        print(f"Database error in get_top_similar_users_by_likes: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching similar users.")
    except Exception as e:
        print(f"Unexpected error in get_top_similar_users_by_likes: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")

class UserLogin(BaseModel):
    email: EmailStr
    password: str

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

@app.get("/user_profile/{user_id}/most_mutual")
def get_most_mutual_watched_user(user_id: int):
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    WITH user_watched_count AS (
                        SELECT user_id, COUNT(movie_id) AS watched_count
                        FROM watched
                        GROUP BY user_id
                    ),
                    mutual_watched AS (
                        SELECT 
                            u2.user_id, 
                            COUNT(*) AS mutual_count
                        FROM watched w1
                        JOIN watched w2 ON w1.movie_id = w2.movie_id 
                                        AND w1.user_id <> w2.user_id
                        JOIN user_watched_count u1 ON w1.user_id = u1.user_id
                        JOIN user_watched_count u2 ON w2.user_id = u2.user_id
                        WHERE w1.user_id = %s and u2.watched_count <= 2 * u1.watched_count
                        GROUP BY u2.user_id
                    )
                    SELECT user_id, mutual_count
                    FROM mutual_watched
                    ORDER BY mutual_count DESC
                    LIMIT 1
                """, (user_id,))

                user = cur.fetchone()

                if user is None:
                    raise HTTPException(status_code=404, detail="No mutual users found")

                return user

    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/reviews/search")
def search_comments_by_movie_id(movie_id: int):
    # Query to get review IDs for a given movie
    query = """
        SELECT review_id FROM Reviews
        WHERE movie_id = %s
        ORDER BY Reviews.created_at DESC
    """
    
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(query, (movie_id,))
                rows = cur.fetchall()
                
                if not rows:
                    return {"count": 0, "reviews": []}

                # Fetch detailed review info for each review_id
                review_infos = [get_review_info(row["review_id"]) for row in rows]

                return {
                    "count": len(review_infos),
                    "reviews": review_infos
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
    rating: Optional[str] = None,
    limit: int = Query(50, ge=1),
    offset: int = Query(0, ge=0)
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
                LIMIT %s OFFSET %s
                """
                
                params.append(limit)
                params.append(offset)
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
    conn = None
    try:
        conn = get_db_connection() 
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # insert main movie record
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
            
            result = cur.fetchone()
            if not result:
                 raise HTTPException(status_code=500, detail="Failed to create movie record and retrieve ID.")
            movie_id = result['movie_id']

            print(f"Created base movie record with ID: {movie_id}")

            # batch insert all the related entities
            batch_handle_related(cur, movie_id, movie.genres,    
                                 'Genre', 'genre_id', 'name', 
                                 'MovieGenre', 'genre_id')
                                 
            batch_handle_related(cur, movie_id, movie.writers,   
                                 'Writer', 'writer_id', 'name', 
                                 'MovieWriter', 'writer_id')
                                 
            batch_handle_related(cur, movie_id, movie.actors,    
                                 'Actor', 'actor_id', 'name', 
                                 'MovieActor', 'actor_id')
                                 
            batch_handle_related(cur, movie_id, movie.studios,   
                                 'Studio', 'studio_id', 'name', 
                                 'MovieStudio', 'studio_id')
                                 
            batch_handle_related(cur, movie_id, movie.directors, 
                                 'Director', 'director_id', 'name', 
                                 'MovieDirector', 'director_id')

            # commit tx
            print("Committing transaction...")
            conn.commit()

            # Return the created movie with all relationships
            return get_movie(movie_id)

    except (Exception, psycopg2.Error) as e:
        print(f"Database error occurred: {e}")
        if conn:
            # rollback tx on error explicitly
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

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
                query = """
                    SELECT *
                    FROM mv_top_10_reviewed_movies
                    ORDER BY reviewCount DESC;
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

@app.get("/users/reputation")
def get_user_reputation():
    limit = 10
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(GET_USER_REPUTATION_SQL, (limit,))
                results = cur.fetchall()
                return {
                    "count": len(results),
                    "results": results
                }
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
@app.get("/users/{user_id}")
def get_user_details(user_id: int):
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT user_id, username, email, created_at
                    FROM Users
                    WHERE user_id = %s
                """, (user_id,))
                user = cur.fetchone()
                if not user:
                    raise HTTPException(status_code=404, detail="User not found")
                return user
    except psycopg2.Error as e:
        print(f"Database error fetching user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error fetching user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
    
@app.get("/user_profile/{user_id}/reputation")
def get_user_reputation_info(user_id: int): # Renamed function for clarity
    try:
        with get_db_connection() as conn:
            # Use RealDictCursor to get column names
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:

                query = """
                SELECT reputation_score, last_updated
                FROM UserReputation
                WHERE user_id = %s
                """
                cur.execute(query, (user_id,))
                result = cur.fetchone()

                if not result:
                    # Return a 404 specifically for not found reputation
                    # Or return default values if preferred
                    # return {"reputation_score": 0, "last_updated": None} # Example default
                    raise HTTPException(status_code=404, detail="User reputation not found.")

                # The RealDictCursor already returns a dict with correct keys
                return result # Directly return the dictionary { "reputation_score": ..., "last_updated": ...}

    except psycopg2.Error as e:
        print(f"Database error fetching reputation for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Database error fetching reputation: {str(e)}")
    except Exception as e:
        print(f"Unexpected error fetching reputation for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")