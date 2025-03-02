INSERT INTO Users (username, email, password_hash, created_at, updated_at)                        
VALUES ('john_doe', 'john.doe@example.com', 'dflgkj34lkj', NOW(), NOW())
RETURNING user_id;