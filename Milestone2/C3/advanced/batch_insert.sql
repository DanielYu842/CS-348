BEGIN;

INSERT INTO Movie (
    title,
    info,
    critics_consensus,
    rating,
    in_theaters_date,
    on_streaming_date,
    runtime_in_minutes,
    tomatometer_status,
    tomatometer_rating,
    tomatometer_count,
    audience_rating,
    audience_count
)
VALUES (
    'Cosmic Drift',                           
    'A young explorer drifts through space.',    
    'Visually stunning adventure.',               
    'PG',                                      
    '2025-03-01',                               
    '2025-09-01',                            
    95,                                      
    'Fresh',                                    
    85,                                        
    150,                                         
    90,                                          
    5000                                         
)
RETURNING movie_id; 

INSERT INTO Genre (name) VALUES ('Adventure')
ON CONFLICT (name) DO NOTHING;

INSERT INTO Actor (name) VALUES ('Leo Comet')
ON CONFLICT (name) DO NOTHING;

INSERT INTO Director (name) VALUES ('Stella Nova')
ON CONFLICT (name) DO NOTHING;

INSERT INTO Writer (name) VALUES ('Stella Nova'), ('Max Orbit')
ON CONFLICT (name) DO NOTHING;

INSERT INTO MovieGenre (movie_id, genre_id) VALUES
(701, 5), 
(701, 8), 
(701, 11) 
ON CONFLICT (movie_id, genre_id) DO NOTHING;

INSERT INTO MovieActor (movie_id, actor_id) VALUES
(701, 25),
(701, 99)
ON CONFLICT (movie_id, actor_id) DO NOTHING;

INSERT INTO MovieDirector (movie_id, director_id) VALUES
(701, 55)
ON CONFLICT (movie_id, director_id) DO NOTHING;

INSERT INTO MovieWriter (movie_id, writer_id) VALUES
(701, 61),
(701, 62)
ON CONFLICT (movie_id, writer_id) DO NOTHING;

INSERT INTO MovieStudio (movie_id, studio_id) VALUES
(701, 12)
ON CONFLICT (movie_id, studio_id) DO NOTHING;

COMMIT;

