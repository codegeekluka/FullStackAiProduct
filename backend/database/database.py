import pgvector.sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from backend.database.config import DATABASE_URL

Base = declarative_base()
engine = create_engine(
    DATABASE_URL,
    pool_size=200,  # Increased for 1000+ concurrent users
    max_overflow=300,  # Allow up to 500 total connections
    pool_pre_ping=True,  # Validate connections before use
    pool_recycle=1800,  # Recycle connections every 30 minutes
    pool_timeout=30,  # Wait up to 30 seconds for a connection
    echo=False,  # Disable SQL logging for performance
    # Performance optimizations
    connect_args={
        "connect_timeout": 10,  # Database connection timeout
        "application_name": "recipe_app_api"
    }
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
