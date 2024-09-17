from os import environ

# These need to be set before any application imports otherwise the
# database will be setup with the wrong parameters
################################################
environ["DATABASE_SCHEME"] = "sqlite"
environ["DATABASE_NAME"] = ":memory:"
environ["DATABASE_HOST"] = ""
# environ["DATABASE_PORT"] = ""
# environ["DATABASE_USER"] = ""
# environ["DATABASE_PASSWORD"] = ""
environ["COOKIE_KEY"] = "SYNOD_SESSION"
environ["COOKIE_MAX_AGE"] = "86400"  # in seconds: 24 hours = 86400 seconds
environ["SESSIONS_ENABLED"] = "True"
environ["TEST_ENDPOINT_ENABLED"] = "True"
################################################

from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from openday_scavenger.api.db import Base, create_tables, engine, get_db
from openday_scavenger.main import app


@pytest.fixture(scope="function")
def empty_db() -> Generator[Session, None, None]:
    create_tables()
    session = next(get_db())

    # Ensure the database is empty before each test
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()

    yield session

    # Close the session and drop all tables
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def mock_client():
    with TestClient(app) as client:
        yield client
