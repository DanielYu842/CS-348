CREATE_REPUTATION_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS UserReputation (
    user_id INT PRIMARY KEY REFERENCES Users(user_id) ON DELETE CASCADE,
    reputation_score INT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

'''
point system:
- creating a review: 10 points
- creating a comment: 5 points
- receiving a like on a review: 2 points
'''

CREATE_REPUTATION_TRIGGERS_SQL = """
CREATE OR REPLACE FUNCTION update_user_reputation()
RETURNS TRIGGER AS $$
BEGIN

    IF TG_TABLE_NAME = 'reviews' AND TG_OP = 'INSERT' THEN
        INSERT INTO UserReputation (user_id, reputation_score)
        VALUES (NEW.user_id, 10) 
        ON CONFLICT (user_id) 
        DO UPDATE SET 
            reputation_score = UserReputation.reputation_score + 10,
            last_updated = CURRENT_TIMESTAMP;
    END IF;

    IF TG_TABLE_NAME = 'comments' AND TG_OP = 'INSERT' THEN
        INSERT INTO UserReputation (user_id, reputation_score)
        VALUES (NEW.user_id, 5) 
        ON CONFLICT (user_id) 
        DO UPDATE SET 
            reputation_score = UserReputation.reputation_score + 5,
            last_updated = CURRENT_TIMESTAMP;
    END IF;

    IF TG_TABLE_NAME = 'likes' AND TG_OP = 'INSERT' AND NEW.review_id IS NOT NULL THEN
        UPDATE UserReputation
        SET 
            reputation_score = reputation_score + 2,  
            last_updated = CURRENT_TIMESTAMP
        WHERE user_id = (
            SELECT user_id 
            FROM Reviews 
            WHERE review_id = NEW.review_id
        );
    END IF;


    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_reputation_on_review ON Reviews;
CREATE TRIGGER update_reputation_on_review
    AFTER INSERT ON Reviews
    FOR EACH ROW
    EXECUTE FUNCTION update_user_reputation();

DROP TRIGGER IF EXISTS update_reputation_on_comment ON Comments;
CREATE TRIGGER update_reputation_on_comment
    AFTER INSERT ON Comments
    FOR EACH ROW
    EXECUTE FUNCTION update_user_reputation();

DROP TRIGGER IF EXISTS update_reputation_on_like ON Likes;
CREATE TRIGGER update_reputation_on_like
    AFTER INSERT ON Likes
    FOR EACH ROW
    EXECUTE FUNCTION update_user_reputation();
"""

GET_USER_REPUTATION_SQL = """
SELECT 
    u.username,
    ur.reputation_score,
    ur.last_updated
FROM UserReputation ur
JOIN Users u ON ur.user_id = u.user_id
ORDER BY ur.reputation_score DESC
LIMIT %s;
"""

GET_USER_REPUTATION_BY_ID_SQL = """
SELECT 
    u.username,
    ur.reputation_score,
    ur.last_updated
FROM UserReputation ur
JOIN Users u ON ur.user_id = u.user_id
WHERE ur.user_id = %s;
""" 