INSERT INTO Movie (
    title, info, critics_consensus, rating, in_theaters_date, on_streaming_date, 
    runtime_in_minutes, tomatometer_status, tomatometer_rating, tomatometer_count, 
    audience_rating, audience_count
)  
VALUES (
    'Iron Man', 
    'A billionaire builds a high-tech suit.', 
    'A thrilling origin story with humor and action.', 
    'PG-13', 
    '2008-05-02', 
    '2008-09-30', 
    126, 
    'Certified Fresh', 
    94.0, 
    300, 
    91.5, 
    1000000
)  
RETURNING movie_id;
