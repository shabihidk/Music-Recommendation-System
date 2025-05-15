"""Database configuration and connection handling."""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'SongBih'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'Aishafarid786'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432')
}

def get_connection():
    """Create and return a new database connection"""
    return psycopg2.connect(**DB_CONFIG)

def execute_query(query, params=None, fetch=True):
    """Execute a query and return results if needed"""
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params or ())
                if fetch:
                    return cur.fetchall()
                conn.commit()
                return True
    except Exception as e:
        print(f"Database error: {e}")
        return None

def execute_single_query(query, params=None):
    """Execute a query and return a single result"""
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params or ())
                return cur.fetchone()
    except Exception as e:
        print(f"Database error: {e}")
        return None 