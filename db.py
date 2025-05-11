import psycopg2
from psycopg2 import pool
from config import DATABASE_URL

# Initialize connection pool
try:
    db_pool = psycopg2.pool.SimpleConnectionPool(1, 20, dsn=DATABASE_URL)
    if db_pool:
        print("Connection pool created successfully")
except Exception as e:
    print(f"Error creating connection pool: {e}")
    exit(1)

def get_db_connection():
    try:
        conn = db_pool.getconn()
        return conn
    except Exception as e:
        print(f"Error getting connection: {e}")
        return None

def release_db_connection(conn):
    try:
        if conn:
            db_pool.putconn(conn)
    except Exception as e:
        print(f"Error releasing connection: {e}")