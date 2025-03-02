CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS Movie (
    movie_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    info TEXT,
    critics_consensus TEXT,
    rating VARCHAR(10) CHECK (rating IN ('G', 'PG', 'PG-13', 'R', 'NC-17', 'NR')),
    in_theaters_date DATE,
    on_streaming_date DATE,
    runtime_in_minutes INT CHECK (runtime_in_minutes > 0),
    tomatometer_status VARCHAR(20) CHECK (tomatometer_status IN ('Fresh', 'Rotten', 'Certified Fresh')),
    tomatometer_rating DECIMAL(5, 2) CHECK (tomatometer_rating BETWEEN 0 AND 100),
    tomatometer_count INT CHECK (tomatometer_count >= 0),
    audience_rating DECIMAL(5, 2) CHECK (audience_rating BETWEEN 0 AND 100),
    audience_count INT CHECK (audience_count >= 0)
);

CREATE TABLE IF NOT EXISTS Genre (
    genre_id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS Director (
    director_id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS Writer (
    writer_id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS Actor (
    actor_id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS Studio (
    studio_id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS MovieGenre (
    movie_id INT REFERENCES Movie(movie_id) ON DELETE CASCADE,
    genre_id INT REFERENCES Genre(genre_id) ON DELETE CASCADE,
    PRIMARY KEY (movie_id, genre_id)
);

CREATE TABLE IF NOT EXISTS MovieDirector (
    movie_id INT REFERENCES Movie(movie_id) ON DELETE CASCADE,
    director_id INT REFERENCES Director(director_id) ON DELETE CASCADE,
    PRIMARY KEY (movie_id, director_id)
);

CREATE TABLE IF NOT EXISTS MovieWriter (
    movie_id INT REFERENCES Movie(movie_id) ON DELETE CASCADE,
    writer_id INT REFERENCES Writer(writer_id) ON DELETE CASCADE,
    PRIMARY KEY (movie_id, writer_id)
);

CREATE TABLE IF NOT EXISTS MovieActor (
    movie_id INT REFERENCES Movie(movie_id) ON DELETE CASCADE,
    actor_id INT REFERENCES Actor(actor_id) ON DELETE CASCADE,
    PRIMARY KEY (movie_id, actor_id)
);

CREATE TABLE IF NOT EXISTS MovieStudio (
    movie_id INT REFERENCES Movie(movie_id) ON DELETE CASCADE,
    studio_id INT REFERENCES Studio(studio_id) ON DELETE CASCADE,
    PRIMARY KEY (movie_id, studio_id)
);

CREATE TABLE IF NOT EXISTS Users (
  user_id SERIAL PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at VARCHAR(255) NOT NULL,
  updated_at VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS Reviews (
    review_id SERIAL PRIMARY KEY,
    movie_id INT NOT NULL REFERENCES Movie(movie_id),
    user_id INT NOT NULL REFERENCES Users(user_id),
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    rating DECIMAL(4,2) NOT NULL CHECK (rating BETWEEN 0 AND 100),
    created_at VARCHAR(255) NOT NULL,
    updated_at VARCHAR(255) NOT NULL
);
"""
