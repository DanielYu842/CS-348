import psycopg2.extras 
from typing import List


def batch_handle_related(
    cur: psycopg2.extensions.cursor, 
    movie_id: int, 
    items: List[str], 
    entity_table: str, 
    entity_pk_col: str, 
    entity_name_col: str, 
    linking_table: str, 
    linking_fk_col: str):
    """
    This function only makes 4 DB queries instead of N queries. It handles batch insertion of related entities and their links to a movie.

    What it does: 
    1. Finds existing entities.
    2. Batch inserts missing entities.
    3. Batch inserts links between movie and entities.
    """
    if not items:
        return

    unique_items = list(set(items))
    if not unique_items:
        return
        
    print(f"Batch handling {len(unique_items)} unique {entity_table} items...") 

    # 1. Get existing IDs for the unique items
    query_existing = f"""
        SELECT {entity_pk_col}, {entity_name_col} 
        FROM {entity_table} 
        WHERE {entity_name_col} = ANY(%s) 
    """
    cur.execute(query_existing, (unique_items,))
    name_to_id = {row[entity_name_col]: row[entity_pk_col] for row in cur.fetchall()}
    existing_names = set(name_to_id.keys())
    print(f"Found {len(existing_names)} existing {entity_table} items.") 

    # 2. Identify and batch insert missing items
    items_to_insert = [(name,) for name in unique_items if name not in existing_names]
    
    if items_to_insert:
        print(f"Inserting {len(items_to_insert)} new {entity_table} items...") 
        insert_query = f"""
            INSERT INTO {entity_table} ({entity_name_col}) VALUES %s
            ON CONFLICT ({entity_name_col}) DO NOTHING 
        """
        psycopg2.extras.execute_values(
            cur, 
            insert_query, 
            items_to_insert, 
            template='(%s)', 
            page_size=100
        )
        
        # 2a. Re-query to get IDs of all items (existing + newly inserted)
        cur.execute(query_existing, (unique_items,))
        name_to_id = {row[entity_name_col]: row[entity_pk_col] for row in cur.fetchall()}
    
    # 3. Batch insert into the linking table
    links_to_insert = []
    for name in unique_items:
        if name in name_to_id:
             links_to_insert.append((movie_id, name_to_id[name]))
        else:
             print(f"Warning: Could not find ID for {entity_table} item '{name}' after attempting insert.")

    if links_to_insert:
        print(f"Inserting {len(links_to_insert)} links into {linking_table}...") 
        link_insert_query = f"""
            INSERT INTO {linking_table} (movie_id, {linking_fk_col}) VALUES %s 
            ON CONFLICT (movie_id, {linking_fk_col}) DO NOTHING 
        """
        psycopg2.extras.execute_values(
            cur, 
            link_insert_query, 
            links_to_insert, 
            template='(%s, %s)', 
            page_size=100
        )
    print(f"Finished batch handling {entity_table}.") 