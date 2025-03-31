from utils.db import get_db_connection
# Gets all reviews and comments written by a user.
# Comments table is not made yet
def review_ids_from_user(user_id: int):
    conn = get_db_connection()
    cur = conn.cursor()

    # Query to get all review IDs associated with the user
    user_reviews_query = "SELECT review_id FROM reviews where user_id = %s order by reviews.created_at desc"
    cur.execute(user_reviews_query, (user_id,))
    review_ids = cur.fetchall()  # Fetch all review IDs
    # print('REVIEW IDS', review_ids)
    cur.close()
    conn.close()

    # Return a list of review_ids
    return [review_id[0] for review_id in review_ids]  # Extract the first item from each tuple
