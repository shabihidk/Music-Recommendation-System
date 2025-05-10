import os
import secrets

# SQLAlchemy-compatible DATABASE_URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:Aishafarid786@localhost:5432/musicdb"
)

# Optional: If db.py needs a different format for psycopg2, you can define it separately
PSYCOPG2_DATABASE_URL = os.getenv(
    "PSYCOPG2_DATABASE_URL",
    "dbname=musicdb user=postgres password=Aishafarid786 host=localhost port=5432"
)

# JWT secret key for secure token generation
JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    secrets.token_hex(32)
)