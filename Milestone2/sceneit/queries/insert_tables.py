INSERT_REVIEW_SQL = """
INSERT INTO Reviews (review_id, movie_id, user_id, title, content, rating, created_at, updated_at)
VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
RETURNING review_id;
"""

NUM_REVIEWS_SQL = "SELECT COUNT(*) FROM Reviews"

INSERT_USER_SQL = """
INSERT INTO Users (user_id, username, email, password_hash, created_at, updated_at)
VALUES (%s, %s, %s, %s, NOW(), NOW())
RETURNING user_id;
"""

NUM_USERS_SQL = "SELECT COUNT(*) FROM Users"