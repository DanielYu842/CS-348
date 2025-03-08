SELECT * 
FROM Reviews
JOIN (
    SELECT user_id, username, email 
    FROM Users
) AS Users ON Reviews.user_id = Users.user_id
WHERE movie_id = 1;
