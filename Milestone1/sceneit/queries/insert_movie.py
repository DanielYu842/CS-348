INSERT_MOVIE_SQL = """
INSERT INTO Movie (title, info, critics_consensus, rating, in_theaters_date, 
                    on_streaming_date, runtime_in_minutes, tomatometer_status, 
                    tomatometer_rating, tomatometer_count, audience_rating, audience_count)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
RETURNING movie_id;
"""

NUM_MOVIES_SQL = "SELECT COUNT(*) FROM Movie;"