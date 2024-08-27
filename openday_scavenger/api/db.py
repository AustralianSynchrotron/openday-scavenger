from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from typing_extensions import Any

#from ..config import get_settings

__all__ = ("create_tables", "get_db")

#config = get_settings()
#engine = create_engine(str(config.DATABASE_URI))  # turn off thread checking for now

engine = create_engine("sqlite:///../scavenger_hunt.db", echo=True, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Abstract Base"""


def create_tables():
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, Any, None]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
