from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from typing_extensions import Any

from openday_scavenger.config import get_settings

__all__ = ["create_tables", "get_db"]

config = get_settings()

# Create the main database engine using the auto-generated database uri
# Since sqlite only allows access from a single thread, set the special connect arg accordingly
engine = create_engine(
    str(config.DATABASE_URI),
    echo=True,
    connect_args={"check_same_thread": config.DATABASE_SCHEME != "sqlite"},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Abstract Base"""


def create_tables():
    """Create all the tables from the models on the database"""
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, Any, None]:
    """Create a database session and yield it so it can be used as a dependency"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
