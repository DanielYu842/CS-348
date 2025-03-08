from utils.db import get_db_connection
from utils.load_csv import load_csv_data
from static.vars import IS_PRODUCTION
from queries.insert_movie import INSERT_MOVIE_SQL, NUM_MOVIES_SQL
from queries.insert_tables import INSERT_REVIEW_SQL, INSERT_USER_SQL, NUM_REVIEWS_SQL, NUM_USERS_SQL
from objects.user import User
from objects.review import Review
from objects.movie import Movie
from psycopg2.extensions import cursor

SAMPLE_SIZE = 50

def insert_into_entity_table(cur: cursor, table_name, entity_name):
    cur.execute(f"""
        INSERT INTO {table_name} (name) 
        VALUES (%s) 
        ON CONFLICT (name) 
        DO UPDATE SET name = EXCLUDED.name 
        RETURNING {table_name.lower()}_id;
    """, (entity_name,))
    
    entity_id = cur.fetchone()[0]
    return entity_id

def insert_into_junction_table(cur: cursor, table_name, entity_table_name, movie_id, entity_id, ):
    cur.execute(f"""
        INSERT INTO {table_name} (movie_id, {entity_table_name.lower()}_id) 
        VALUES (%s, %s) 
        ON CONFLICT DO NOTHING;
    """, (movie_id, entity_id))


def populate_movie_junctions(movie: Movie, cur: cursor):
    movie_id = cur.fetchone()[0]

    relations = {
        "MovieGenre": (movie.genres, "Genre"),
        "MovieDirector": (movie.directors, "Director"),
        "MovieWriter": (movie.writers, "Writer"),
        "MovieActor": (movie.actors, "Actor"),
        "MovieStudio": (movie.studios, "Studio"),
    }

    for table_name, (entities, entity_table_name) in relations.items():
        for entity_name in entities:
            entity_id = insert_into_entity_table(cur, entity_table_name, entity_name)
            insert_into_junction_table(cur, table_name, entity_table_name, movie_id, entity_id, )

def hasUsersBeenPopulated(cur):
    cur.execute(NUM_USERS_SQL)

    count = cur.fetchone()[0]
    return True if count > 0 else False

def hasReviewsBeenPopulated(cur):
    cur.execute(NUM_REVIEWS_SQL)

    count = cur.fetchone()[0]
    return True if count > 0 else False

def insert_reviews(csv_filepath: str, sample_size: int = SAMPLE_SIZE):
    conn = get_db_connection()
    cur = conn.cursor()
    
    if hasReviewsBeenPopulated(cur):
       print("Reviews table already populated. Skipping insertion.")
       cur.close()
       conn.close()
       return 
    
    reviews = load_csv_data(csv_filepath)
    numReviews = len(reviews) if IS_PRODUCTION else min(sample_size, len(reviews))

    for reviewIndex in range(numReviews):
        review_attrs = reviews[reviewIndex]
        if Review.review_attrs_soft_check(review_attrs):
            review = Review(review_attrs)
            cur.execute(INSERT_REVIEW_SQL, (
                review.movie_id, review.user_id,
                review.title, review.content, review.rating))
    conn.commit()
    cur.close()
    conn.close()

def insert_users(csv_filepath: str, sample_size: int = SAMPLE_SIZE):
    conn = get_db_connection()
    cur = conn.cursor()

    if hasUsersBeenPopulated(cur):
       print("Users table already populated. Skipping insertion.")
       cur.close()
       conn.close()
       return 
    
    users = load_csv_data(csv_filepath)
    numUsers = len(users) if IS_PRODUCTION else min(len(users), sample_size)

    for userIndex in range(numUsers):
        user_attrs = users[userIndex]
        if User.user_attrs_soft_check(user_attrs):
            user = User(user_attrs)
            cur.execute(INSERT_USER_SQL, (
                user.username, user.email, user.password_hash
                ))
    conn.commit()
    cur.close()
    conn.close()


def hasMoviesBeenPopulated(cur):
    cur.execute(NUM_MOVIES_SQL)

    movie_count = cur.fetchone()[0]
    return True if movie_count > 0 else False

def insert_movies(csv_filepath: str, sample_size: int = SAMPLE_SIZE):
    conn = get_db_connection()
    cur = conn.cursor()
    print("Ready to insert movie table")
    if hasMoviesBeenPopulated(cur):
       print("Movies table already populated. Skipping insertion.")
       cur.close()
       conn.close()
       return
    
    movies = load_csv_data(csv_filepath)
    numMovies = len(movies) if IS_PRODUCTION else min(len(movies), sample_size)

    for movieIndex in range(numMovies):
        movie_attrs = movies[movieIndex]
        if Movie.movie_attrs_soft_check(movie_attrs):
            movie = Movie(movie_attrs)
            cur.execute(INSERT_MOVIE_SQL, (
              movie.movie_title, movie.movie_info, movie.critics_consensus,
              movie.rating, movie.in_theaters_date, movie.on_streaming_date,
              movie.runtime_in_minutes, movie.tomatometer_status,
              movie.tomatometer_rating, movie.tomatometer_count,
              movie.audience_rating, movie.audience_count,
            ))

            populate_movie_junctions(movie, cur)

    conn.commit()
    cur.close()
    conn.close()
