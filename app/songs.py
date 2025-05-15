"""Song management and search functions."""

from app.database import execute_query, execute_single_query

def search_songs(query):
    """Search for songs based on query"""
    if not query:
        return []
    
    results = execute_query(
        "SELECT * FROM search_songs(%s)",
        (query,)
    )
    
    if not results:
        return []
    
    return [{
        'id': row['id'],
        'title': row['title'],
        'artist': row['artist'],
        'genre': row['genre'],
        'image': row['image_path']
    } for row in results]

def get_songs_paginated(page=1, genre='', sort='title', per_page=12):
    """Get paginated list of songs with optional filtering"""
    # Base query
    query = """
        SELECT 
            s.id, 
            s.title, 
            s.artist, 
            s.genre, 
            s.image_path,
            s.duration,
            s.created_at,
            COUNT(lh.id) as play_count
        FROM songs s
        LEFT JOIN listening_history lh ON s.id = lh.song_id
    """
    
    # Add filters
    params = []
    if genre:
        query += " WHERE s.genre ILIKE %s"
        params.append(f"%{genre}%")
    
    query += " GROUP BY s.id"
    
    # Add sorting
    sort_options = {
        'title': " ORDER BY s.title ASC",
        'artist': " ORDER BY s.artist ASC",
        'recent': " ORDER BY s.created_at DESC",
        'popular': " ORDER BY play_count DESC"
    }
    query += sort_options.get(sort, " ORDER BY s.title ASC")
    
    # Add pagination
    query += " LIMIT %s OFFSET %s"
    params.extend([per_page, (page - 1) * per_page])
    
    # Execute query
    results = execute_query(query, params)
    if not results:
        return {'songs': [], 'page': page, 'total_pages': 0, 'total_songs': 0}
    
    # Get total count
    count_query = "SELECT COUNT(*) FROM songs"
    if genre:
        count_query += " WHERE genre ILIKE %s"
        count_result = execute_single_query(count_query, [f"%{genre}%"])
    else:
        count_result = execute_single_query(count_query)
    
    total_songs = count_result['count'] if count_result else 0
    total_pages = -(-total_songs // per_page)  # Ceiling division
    
    # Format response
    songs = [{
        'id': row['id'],
        'title': row['title'],
        'artist': row['artist'],
        'genre': row['genre'],
        'image': row['image_path'],
        'duration': row['duration']
    } for row in results]
    
    return {
        'songs': songs,
        'page': page,
        'total_pages': total_pages,
        'total_songs': total_songs
    } 