"""Script to populate the database with sample songs."""

import os
import sys
import psycopg2
from datetime import datetime, timedelta
import random
from psycopg2.extras import RealDictCursor

# Database configuration
DB_CONFIG = {
    'dbname': 'SongBih',
    'user': 'postgres',
    'password': 'Aishafarid786',
    'host': 'localhost',
    'port': '5432'
}

# Sample data
GENRES = ['Pop', 'Rock', 'Hip Hop', 'R&B', 'Jazz', 'Classical', 'Electronic', 'Folk']

SONGS = [
    # Format: (title, artist, genre)
    ("Shape of You", "Ed Sheeran", "Pop"),
    ("Bohemian Rhapsody", "Queen", "Rock"),
    ("Lose Yourself", "Eminem", "Hip Hop"),
    ("All of Me", "John Legend", "R&B"),
    ("Take Five", "Dave Brubeck", "Jazz"),
    ("Moonlight Sonata", "Ludwig van Beethoven", "Classical"),
    ("Strobe", "Deadmau5", "Electronic"),
    ("The Sound of Silence", "Simon & Garfunkel", "Folk"),
    ("Uptown Funk", "Mark Ronson ft. Bruno Mars", "Pop"),
    ("Sweet Child O' Mine", "Guns N' Roses", "Rock"),
    ("God's Plan", "Drake", "Hip Hop"),
    ("Thinking Out Loud", "Ed Sheeran", "Pop"),
    ("November Rain", "Guns N' Roses", "Rock"),
    ("In Da Club", "50 Cent", "Hip Hop"),
    ("Fly Me to the Moon", "Frank Sinatra", "Jazz"),
    ("Symphony No. 5", "Ludwig van Beethoven", "Classical"),
    ("Sandstorm", "Darude", "Electronic"),
    ("The Boxer", "Simon & Garfunkel", "Folk"),
    ("Rolling in the Deep", "Adele", "Pop"),
    ("Stairway to Heaven", "Led Zeppelin", "Rock")
]

def create_images_folder():
    """Create images folder if it doesn't exist"""
    images_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'images')
    if not os.path.exists(images_folder):
        os.makedirs(images_folder)
    return images_folder

def populate_database():
    """Populate the database with sample data"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Clear existing data
        cur.execute("TRUNCATE songs, users, playlists, playlist_songs, listening_history RESTART IDENTITY CASCADE;")
        
        # Insert songs
        for i, (title, artist, genre) in enumerate(SONGS, 1):
            # Random duration between 2-5 minutes in seconds
            duration = random.randint(120, 300)
            
            # Random release date in the last 60 years
            days_ago = random.randint(0, 365 * 60)
            release_date = datetime.now() - timedelta(days=days_ago)
            
            cur.execute("""
                INSERT INTO songs (title, artist, genre, image_path, duration, release_date)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                title,
                artist,
                genre,
                f"{i}.jpg",  # Image path will be 1.jpg, 2.jpg, etc.
                duration,
                release_date
            ))
        
        conn.commit()
        print(f"Successfully populated database with {len(SONGS)} songs!")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    # Create images folder
    images_folder = create_images_folder()
    print(f"Images folder created at: {images_folder}")
    
    # Populate database
    populate_database() 