import os
import secrets

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:Aishafarid786@localhost:5432/musicdb"
)

# Flask app configuration
SECRET_KEY = secrets.token_hex(32)  # Generate a secure key
SQLALCHEMY_DATABASE_URI = DATABASE_URL
SQLALCHEMY_TRACK_MODIFICATIONS = False
JWT_SECRET_KEY = secrets.token_hex(32)  # Separate key for JWT