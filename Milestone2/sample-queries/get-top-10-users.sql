SELECT u.user_id, u.username, COUNT(l.like_id) AS total_likes  
FROM Users u  
JOIN Likes l ON u.user_id = l.user_id  
GROUP BY u.user_id  
ORDER BY total_likes DESC  
LIMIT 10;