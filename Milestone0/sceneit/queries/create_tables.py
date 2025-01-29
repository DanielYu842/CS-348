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

-- TODO: add rest of tables
"""
