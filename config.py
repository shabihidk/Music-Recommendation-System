import os
import secrets

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "dbname=musicdb user=postgres password=Aishafarid786 host=localhost port=5432"
)

JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    secrets.token_hex(32)
)