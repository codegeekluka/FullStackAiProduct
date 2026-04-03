# config.py
import os

from dotenv import load_dotenv
from sqlalchemy.engine.url import URL, make_url

# Load variables from .env file
# Assumes .env is in the same folder as config.py
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# Environment variables
DATABASE_USER = os.getenv("DB_USER", "postgres")
DATABASE_PASSWORD = os.getenv("DB_PASSWORD", "password")
DATABASE_HOST = os.getenv("DB_HOST", "localhost")
DATABASE_PORT = os.getenv("DB_PORT", "5432")
DATABASE_NAME = os.getenv("DB_NAME", "mydatabase")


def _is_local_host(host: str | None) -> bool:
    if not host:
        return True
    h = host.lower()
    return h in ("localhost", "127.0.0.1")


def _finalize_database_url(url: str) -> str:
    """Ensure sslmode=require for remote Postgres (fixes Render SSL drops)."""
    u = make_url(url)
    if _is_local_host(u.host):
        return u.render_as_string(hide_password=False)
    q = dict(u.query)
    if "sslmode" not in q:
        u = u.update_query_dict({"sslmode": "require"})
    return u.render_as_string(hide_password=False)


# Render provides DATABASE_URL; prefer it when set.
_raw_url = os.getenv("DATABASE_URL")
if _raw_url:
    if _raw_url.startswith("postgres://"):
        _raw_url = _raw_url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif _raw_url.startswith("postgresql://") and "+psycopg2" not in _raw_url:
        _raw_url = _raw_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    DATABASE_URL = _finalize_database_url(_raw_url)
else:
    _built = f"postgresql+psycopg2://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
    DATABASE_URL = _finalize_database_url(_built)

# psycopg2 connect_args: SSL for remote + TCP keepalives (reduces idle SSL disconnects)
_u = make_url(DATABASE_URL)
DB_CONNECT_ARGS: dict = {
    "connect_timeout": 10,
    "application_name": "recipe_app_api",
    "keepalives": 1,
    "keepalives_idle": 30,
    "keepalives_interval": 10,
    "keepalives_count": 5,
}
if not _is_local_host(_u.host):
    DB_CONNECT_ARGS["sslmode"] = "require"
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
