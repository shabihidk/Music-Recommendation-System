import os
import secrets

# PostgreSQL database config
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "dbname=musicdb user=postgres password=Aishafarid786 host=localhost port=5432"
)

# JWT secret key for secure token generation
JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "fbd9f2e3d31a44bd9e998cfb5e18cbe3fbe6a3cb04c1e7a4a8d6e1ffb2a88db2"  # <-- replace this with your own generated key
)
