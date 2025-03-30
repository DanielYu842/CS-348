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

CREATE INDEX idx_mv_top_10_reviewed_movies_count ON mv_top_10_reviewed_movies (reviewCount DESC);

REFRESH MATERIALIZED VIEW mv_top_10_reviewed_movies;
