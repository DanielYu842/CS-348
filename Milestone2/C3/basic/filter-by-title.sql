SELECT movie_id, title, rating, in_theaters_date, on_streaming_date, runtime_in_minutes         
FROM Movie     
WHERE LOWER(title) LIKE LOWER('%P%')                                                                       
ORDER BY title ASC;    