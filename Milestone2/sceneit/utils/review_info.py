from utils.db import get_db_connection
import psycopg2


def get_review_info(review_id: int):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # Query to get review details
    query = """
        SELECT r.*, u.username, u.email
        FROM reviews r
        JOIN users u ON r.user_id = u.user_id
        WHERE r.review_id = %s
    """
    cur.execute(query, (review_id,))
    review_info = cur.fetchone()

    # # Optionally, fetch likes for this review
    # likes_query = """
    #     SELECT COUNT(*) as like_count
    #     FROM likes
    #     WHERE review_id = %s
    # """
    # cur.execute(likes_query, (review_id,))
    # likes_count = cur.fetchone()['like_count']

    # review_info['likes_count'] = likes_count  # Add likes count to the review info

    cur.close()
    conn.close()

    return review_info
