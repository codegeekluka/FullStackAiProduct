# config.py
import os

from dotenv import load_dotenv
from sqlalchemy.engine.url import URL

# Load variables from .env file
# Assumes .env is in the same folder as config.py
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# Environment variables
DATABASE_USER = os.getenv("DB_USER", "postgres")
DATABASE_PASSWORD = os.getenv("DB_PASSWORD", "password")
DATABASE_HOST = os.getenv("DB_HOST", "localhost")
DATABASE_PORT = os.getenv("DB_PORT", "5432")
DATABASE_NAME = os.getenv("DB_NAME", "mydatabase")

# Render provides DATABASE_URL; prefer it when set (includes SSL params).
_raw_url = os.getenv("DATABASE_URL")
if _raw_url:
    if _raw_url.startswith("postgres://"):
        _raw_url = _raw_url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif _raw_url.startswith("postgresql://") and "+psycopg2" not in _raw_url:
        _raw_url = _raw_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    DATABASE_URL = _raw_url
else:
    DATABASE_URL = f"postgresql+psycopg2://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
    # Remote Postgres (e.g. Render) requires SSL; missing sslmode causes dropped connections.
    if DATABASE_HOST not in ("localhost", "127.0.0.1"):
        sep = "&" if "?" in DATABASE_URL else "?"
        if "sslmode" not in DATABASE_URL:
            DATABASE_URL = f"{DATABASE_URL}{sep}sslmode=require"
# Construct the database URL
# DONT USE THIS
"""DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=DATABASE_USER,
    password=DATABASE_PASSWORD,
    host=DATABASE_HOST,
    port=DATABASE_PORT,
    database=DATABASE_NAME,
)"""
