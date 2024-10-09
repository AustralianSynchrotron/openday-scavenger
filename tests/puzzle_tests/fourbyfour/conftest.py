from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from openday_scavenger.api.db import Base, create_tables, engine, get_db
from openday_scavenger.api.puzzles.schemas import PuzzleCreate
from openday_scavenger.api.puzzles.service import create as create_puzzle
from openday_scavenger.api.puzzles.service import get_all as get_all_puzzles
from openday_scavenger.api.visitors.dependencies import auth_required
from openday_scavenger.api.visitors.schemas import VisitorPoolCreate
from openday_scavenger.api.visitors.service import create as create_visitor
from openday_scavenger.api.visitors.service import create_visitor_pool, get_visitor_pool
from openday_scavenger.api.visitors.service import get_all as get_all_visitors
from openday_scavenger.main import app
from openday_scavenger.puzzles.fourbyfour.service import SOLUTION, PuzzleStatus

PUZZLE_NAME = "fourbyfour"


@pytest.fixture(scope="module")
def initialised_db() -> Generator[Session, None, None]:
    """
    Fixture to provide a database session populated with puzzles.

    This fixture creates the database tables, provides a session for the test,
    initialises the database with puzzles,
    and then drops all tables after the test is complete.

    Yields:
        session (Session): An SQLAlchemy session object for database operations.

    Cleanup:
        Closes the session and drops all tables after the test.
    """

    create_tables()
    session = next(get_db())

    _ = create_puzzle(
        db_session=session,
        puzzle_in=PuzzleCreate(
            name=PUZZLE_NAME,
            answer=SOLUTION,  # not the actual answer
            active=True,
        ),
    )
    # not sure why, but without the following line, the endpoint test fails:
    # every time I try to poke an endpoint related to a puzzle I just created,
    # I get a 404 response with "puzzle not found in database" message.
    _ = get_all_puzzles(db_session=session)

    _ = create_visitor_pool(
        db_session=session,
        pool_in=VisitorPoolCreate(number_of_entries=10),
    )
    _ = get_all_visitors(db_session=session)

    visitors = get_visitor_pool(db_session=session)

    for visitor in visitors:
        _ = create_visitor(db_session=session, visitor_uid=visitor.uid)
    _ = get_all_visitors(db_session=session)

    yield session

    # Close the session and drop all tables
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def mock_init_client(initialised_db: Session) -> Generator[TestClient, None, None]:
    """
    Fixture to provide a test client for each test function.

    This fixture creates a TestClient instance for the FastAPI app,
    which can be used to simulate HTTP requests in tests.

    Args:
        mocker (MockerFixture): The pytest-mock fixture used to patch dependencies.
        initialised_db (Session): The database fixture.

    Yields:
        client (TestClient): A test client for the FastAPI app.
    """

    def _get_initialised_db():
        return initialised_db

    async def _fake_auth_required():
        pass

    # Needed to ensure the same database is used for service calls and routes.
    app.dependency_overrides[get_db] = _get_initialised_db
    app.dependency_overrides[auth_required] = _fake_auth_required

    with TestClient(app) as client:
        yield client

    app.dependency_overrides = {}


@pytest.fixture(scope="function")
def new_puzzle() -> PuzzleStatus:
    return PuzzleStatus.new()
