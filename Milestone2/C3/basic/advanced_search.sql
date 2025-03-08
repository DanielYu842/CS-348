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
AND EXISTS (
    SELECT 1 
    FROM MovieGenre mg_inner 
    JOIN Genre g_inner ON mg_inner.genre_id = g_inner.genre_id 
    WHERE mg_inner.movie_id = m.movie_id 
    AND g_inner.name ILIKE '%Drama%'
)
    
AND EXISTS (
    SELECT 1 
    FROM MovieGenre mg_inner 
    JOIN Genre g_inner ON mg_inner.genre_id = g_inner.genre_id 
    WHERE mg_inner.movie_id = m.movie_id 
    AND g_inner.name ILIKE '%Action & Adventure%'
)
    
AND EXISTS (
    SELECT 1 
    FROM MovieActor ma_inner 
    JOIN Actor a_inner ON ma_inner.actor_id = a_inner.actor_id 
    WHERE ma_inner.movie_id = m.movie_id 
    AND a_inner.name ILIKE '%Tom Hanks%'
)
    
AND EXISTS (
    SELECT 1 
    FROM MovieStudio ms_inner 
    JOIN Studio s_inner ON ms_inner.studio_id = s_inner.studio_id 
    WHERE ms_inner.movie_id = m.movie_id 
    AND s_inner.name ILIKE '%Sony Pictures%'
)
    
GROUP BY m.movie_id, m.title, m.info, m.critics_consensus, 
        m.rating, m.in_theaters_date, m.on_streaming_date,
        m.runtime_in_minutes, m.tomatometer_status,
        m.tomatometer_rating, m.tomatometer_count,
        m.audience_rating, m.audience_count
ORDER BY m.title 
LIMIT 50;