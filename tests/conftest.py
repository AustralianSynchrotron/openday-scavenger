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
from pytest_mock.plugin import MockerFixture
from sqlalchemy.orm import Session

from openday_scavenger.api.db import Base, create_tables, engine, get_db
from openday_scavenger.main import app


@pytest.fixture(scope="function")
def empty_db() -> Generator[Session, None, None]:
    """
    Fixture to provide an empty database session for each test function.

    This fixture creates the database tables, provides a session for the test,
    and then drops all tables after the test is complete to ensure the tables
    are empty for the next test.

    Yields:
        session (Session): An SQLAlchemy session object for database operations.

    Cleanup:
        Closes the session and drops all tables after the test.
    """

    create_tables()
    session = next(get_db())

    yield session

    # Close the session and drop all tables
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def mock_client(mocker: MockerFixture, empty_db: Session):
    """
    Fixture to provide a test client for each test function.

    This fixture creates a TestClient instance for the FastAPI app,
    which can be used to simulate HTTP requests in tests.

    Args:
        mocker (MockerFixture): The pytest-mock fixture used to patch dependencies.
        empty_db (Session): The database fixture.

    Yields:
        client (TestClient): A test client for the FastAPI app.
    """

    def _get_empty_db():
        return empty_db

    # Needed to ensure the same database is used for service calls and routes.
    mocker.patch.dict(app.dependency_overrides, {get_db: _get_empty_db})
    with TestClient(app) as client:
        yield client
