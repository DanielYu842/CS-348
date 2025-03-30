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
    audience_count INT CHECK (audience_count >= 0),
    info_ts_vector tsvector
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

CREATE TABLE IF NOT EXISTS Comments (
    comment_id SERIAL PRIMARY KEY,
    review_id INT NOT NULL REFERENCES Reviews(review_id) ON DELETE CASCADE,
    user_id INT NOT NULL REFERENCES Users(user_id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS Likes (
    like_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES Users(user_id) ON DELETE CASCADE,
    review_id INT REFERENCES Reviews(review_id) ON DELETE CASCADE,
    comment_id INT REFERENCES Comments(comment_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CHECK (
        (review_id IS NOT NULL AND comment_id IS NULL) OR 
        (review_id IS NULL AND comment_id IS NOT NULL)
    )
);

CREATE TABLE IF NOT EXISTS Watched (
    user_id INT NOT NULL REFERENCES Users(user_id) ON DELETE CASCADE,
    movie_id INT NOT NULL REFERENCES Movie(movie_id) ON DELETE CASCADE,
    watched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (user_id, movie_id)
);
"""

CREATE_INDICES_SQL = """
CREATE INDEX IF NOT EXISTS idx_movie_title_lower ON Movie(LOWER(title));
CREATE INDEX IF NOT EXISTS idx_movie_title ON Movie(title);
CREATE INDEX IF NOT EXISTS idx_movie_reviews_id ON Reviews(movie_id);

CREATE INDEX IF NOT EXISTS idx_likes_user_id ON Likes(user_id);
CREATE INDEX IF NOT EXISTS idx_moviegenre_movie_id ON MovieGenre(movie_id);
CREATE INDEX IF NOT EXISTS idx_moviegenre_genre_id ON Genre(genre_id);

CREATE INDEX IF NOT EXISTS idx_moviedirector_movie_id ON MovieDirector(movie_id);
CREATE INDEX IF NOT EXISTS idx_moviedirector_director_id ON Director(director_id);

CREATE INDEX IF NOT EXISTS idx_moviewriter_movie_id ON MovieWriter(movie_id);
CREATE INDEX IF NOT EXISTS idx_moviewriter_writer_id ON Writer(writer_id);

CREATE INDEX IF NOT EXISTS idx_movieactor_movie_id ON MovieActor(movie_id);
CREATE INDEX IF NOT EXISTS idx_movieactor_actor_id ON Actor(actor_id);

CREATE INDEX IF NOT EXISTS idx_moviestudio_movie_id ON MovieStudio(movie_id);
CREATE INDEX IF NOT EXISTS idx_moviestudio_studio_id ON Studio(studio_id);

CREATE INDEX IF NOT EXISTS idx_movie_title_lower ON Movie(LOWER(title));
CREATE UNIQUE INDEX IF NOT EXISTS idx_movie_title ON Movie(title);
"""
#useful for faster joins for returning full movie results

# create tsvector collumns on [info] collumn of [Movie] for better search
# also need a trigger to run to keep this new collum up to date with the info collumn
INFO_TS_VECTOR_TRIGGER = """
CREATE OR REPLACE FUNCTION update_info_vector() RETURNS TRIGGER AS $$
BEGIN
  NEW.info_ts_vector := to_tsvector('english', NEW.info);
  RETURN NEW;
END
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER movie_info_vector_update
BEFORE INSERT OR UPDATE ON Movie
FOR EACH ROW EXECUTE FUNCTION update_info_vector();
"""

CREATE_MATERIALIZED_VIEW = """
CREATE MATERIALIZED VIEW mv_top_10_reviewed_movies AS
WITH groupedReviews AS (
    SELECT movie_id, count(*) AS reviewCount
    FROM reviews
    GROUP BY movie_id
    ORDER BY reviewCount DESC
    LIMIT 10
)
SELECT
    m.movie_id,
    m.title,
    m.info,
    m.critics_consensus,
    m.rating,
    m.in_theaters_date,
    m.on_streaming_date,
    m.runtime_in_minutes,
    m.tomatometer_status,
    m.tomatometer_rating,
    m.tomatometer_count,
    m.audience_rating,
    m.audience_count,
    gr.reviewCount,
    ARRAY_AGG(DISTINCT g.name) FILTER (WHERE g.name IS NOT NULL) as genres,
    ARRAY_AGG(DISTINCT w.name) FILTER (WHERE w.name IS NOT NULL) as writers,
    ARRAY_AGG(DISTINCT a.name) FILTER (WHERE a.name IS NOT NULL) as actors,
    ARRAY_AGG(DISTINCT s.name) FILTER (WHERE s.name IS NOT NULL) as studios,
    ARRAY_AGG(DISTINCT d.name) FILTER (WHERE d.name IS NOT NULL) as directors
FROM Movie m
INNER JOIN groupedReviews gr ON gr.movie_id = m.movie_id
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
GROUP BY m.movie_id, gr.reviewCount;
"""

MATERIALIZED_VIEW_INDEX="""
CREATE INDEX idx_mv_top_10_reviewed_movies_count ON mv_top_10_reviewed_movies (reviewCount DESC);
"""

REFRESH_MATERIALIZED_VIEW="""
REFRESH MATERIALIZED VIEW mv_top_10_reviewed_movies;
"""