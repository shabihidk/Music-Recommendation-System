import os
import secrets

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:xyz6@localhost:5432/musicdb"
)

SECRET_KEY = secrets.token_hex(32)
SQLALCHEMY_DATABASE_URI = DATABASE_URL
SQLALCHEMY_TRACK_MODIFICATIONS = False
JWT_SECRET_KEY = secrets.token_hex(32)