from utils.db import get_db_connection
from utils.load_csv import load_csv_data
from static.vars import IS_PRODUCTION
from queries.insert_movie import INSERT_MOVIE_SQL
from objects.movie import Movie
from psycopg2.extensions import cursor

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



def insert_movies(csv_filepath: str):
    conn = get_db_connection()
    cur = conn.cursor()
    
    movies = load_csv_data(csv_filepath)
    numMovies = len(movies) if IS_PRODUCTION else 3

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
