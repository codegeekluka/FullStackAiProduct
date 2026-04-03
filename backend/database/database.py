import pgvector.sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from backend.database.config import DATABASE_URL

Base = declarative_base()
# Render Postgres has a low connection limit; huge pools cause SSL drops and 500s.
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_timeout=30,
    echo=False,
    connect_args={
        "connect_timeout": 10,
        "application_name": "recipe_app_api",
    },
)
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,  # Don't auto-flush on every query
    expire_on_commit=False  # Don't expire objects after commit
)


# dependency with connection timeout handling
def get_db():
    db = None
    try:
        db = SessionLocal()
        yield db
    except Exception as e:
        if db:
            db.rollback()
        raise e
    finally:
        if db:
            db.close()
