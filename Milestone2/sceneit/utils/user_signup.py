from queries.insert_tables import INSERT_USER_SQL
from utils.db import get_db_connection
from objects.user import User

def pwd_hash(password: str):
    return password  # Replace with actual hashing function

def user_signup(email: str, username: str, password: str):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Check if the email or username already exists
    search_email_query = "SELECT COUNT(*) FROM Users WHERE email = %s"
    search_username_query = "SELECT COUNT(*) FROM Users WHERE username = %s"
    total_users_query = "SELECT COUNT(*) FROM Users"
    
    cur.execute(search_email_query, (email,))
    email_count = cur.fetchone()[0]
    
    cur.execute(search_username_query, (username,))
    username_count = cur.fetchone()[0]

    cur.execute(total_users_query)
    total = cur.fetchone()[0]
    
    if email_count > 0:
        cur.close()
        conn.close()
        return {"success": False, "message": "Email already exists."}
    
    if username_count > 0:
        cur.close()
        conn.close()
        return {"success": False, "message": "Username already exists."}
    
    # Insert the new user
    cur.execute(INSERT_USER_SQL, (total, username, email, pwd_hash(password)))
    conn.commit()
    
    cur.close()
    conn.close()
    
    return {"success": True, "message": "User registered successfully."}
