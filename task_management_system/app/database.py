from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

# Engine — connects to PostgreSQL using the DATABASE_URL from .env
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,   # reconnects automatically if a connection drops
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency that provides a DB session per request and closes it after."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Creates all tables in the database. Called once on app startup."""
    Base.metadata.create_all(bind=engine)
