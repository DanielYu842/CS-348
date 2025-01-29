from utils.db import get_db_connection
from utils.load_csv import load_csv_data
from static.vars import IS_PRODUCTION
from queries.insert_movie import INSERT_MOVIE_SQL
from objects.movie import Movie

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

    conn.commit()
    cur.close()
    conn.close()
