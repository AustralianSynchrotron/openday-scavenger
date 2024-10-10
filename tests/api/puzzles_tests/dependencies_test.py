from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture
from sqlalchemy.orm import Session

from openday_scavenger.api.puzzles.dependencies import (
    block_correctly_answered_puzzle,
    block_disabled_puzzles,
    get_puzzle_name,
    record_puzzle_access,
)
from openday_scavenger.api.puzzles.exceptions import (
    DisabledPuzzleError,
    PuzzleCompletedError,
    PuzzleNotFoundError,
    UnknownPuzzleError,
)
from openday_scavenger.api.puzzles.schemas import PuzzleCreate
from openday_scavenger.api.puzzles.service import compare_answer
from openday_scavenger.api.puzzles.service import create as create_puzzle
from openday_scavenger.api.visitors.exceptions import VisitorUIDInvalidError
from openday_scavenger.api.visitors.schemas import VisitorPoolCreate
from openday_scavenger.api.visitors.service import create as create_visitor
from openday_scavenger.api.visitors.service import create_visitor_pool, get_visitor_pool


@pytest.mark.asyncio
class TestPuzzlesDependencies:
    """Explicitely test dependencies, since most of the times
    they are overridden in normal endpoint tests
    """

    async def test_get_puzzle_name(self) -> None:
        """Assert that the puzzle name is correctly extracted from the request path"""
        request = Mock(url=Mock(path="/puzzles/demo"))
        assert await get_puzzle_name(request) == "demo"

    async def test_get_puzzle_name_invalid(self) -> None:
        """Assert that an exception is raised when the puzzle name is not found in the request path"""
        request = Mock(url=Mock(path="/foo/bar"))
        with pytest.raises(UnknownPuzzleError):
            await get_puzzle_name(request)

    async def test_block_disabled_puzzles(self, empty_db: Session) -> None:
        """Test that an existing, enabled puzzle is not blocked"""
        create_puzzle(empty_db, puzzle_in=PuzzleCreate(name="foo", answer="", active=True))
        await block_disabled_puzzles(empty_db, "foo")

    async def test_block_disabled_puzzles_disabled(self, empty_db: Session) -> None:
        """Test that an existing, disabled puzzle is blocked"""
        create_puzzle(empty_db, puzzle_in=PuzzleCreate(name="foo", answer="", active=False))
        with pytest.raises(DisabledPuzzleError):
            await block_disabled_puzzles(empty_db, "foo")

    async def test_block_disabled_puzzles_not_found(self, empty_db: Session) -> None:
        """Test that a non-existing puzzle is blocked"""
        with pytest.raises(UnknownPuzzleError):
            await block_disabled_puzzles(empty_db, "foo")

    async def test_block_correctly_answered_puzzle(self, empty_db: Session) -> None:
        """Test that a correctly answered puzzle is blocked"""

        _puzzle_name = "foo"
        _answer = "baz"

        # create a puzzle
        create_puzzle(
            empty_db,
            puzzle_in=PuzzleCreate(
                name=_puzzle_name,
                answer=_answer,
                active=True,
            ),
        )

        # create a visitor pool
        create_visitor_pool(
            empty_db,
            pool_in=VisitorPoolCreate(number_of_entries=1),
        )
        # and get it back
        visitor_pool = get_visitor_pool(empty_db)
        _visitor_uid = visitor_pool[0].uid

        # register the visitor
        create_visitor(empty_db, visitor_uid=_visitor_uid)

        # create a mock visitor auth
        visitor = Mock(uid=_visitor_uid, is_active=True)

        # record that user has answered the puzzle.
        # use the "compare answer" function to register the correct answer
        compare_answer(
            empty_db,
            puzzle_name=_puzzle_name,
            visitor_auth=visitor,
            answer=_answer,
        )

        # call dependency
        with pytest.raises(PuzzleCompletedError):
            await block_correctly_answered_puzzle(
                db=empty_db,
                visitor=visitor,
                puzzle_name=_puzzle_name,
            )

    async def test_record_puzzle_access(
        self,
        empty_db: Session,
        mocker: MockerFixture,
    ) -> None:
        """Test recording access to an existing, active puzzle"""
        from openday_scavenger.api.puzzles import dependencies as puzzle_deps

        _puzzle_name = "foo"
        _answer = "baz"

        # create a puzzle
        create_puzzle(
            empty_db,
            puzzle_in=PuzzleCreate(
                name=_puzzle_name,
                answer=_answer,
                active=True,
            ),
        )

        # create a visitor pool
        create_visitor_pool(
            empty_db,
            pool_in=VisitorPoolCreate(number_of_entries=1),
        )
        # and get it back
        visitor_pool = get_visitor_pool(empty_db)
        _visitor_uid = visitor_pool[0].uid

        # register the visitor
        create_visitor(empty_db, visitor_uid=_visitor_uid)

        # create a mock visitor auth
        visitor = Mock(uid=_visitor_uid, is_active=True)

        # call dependency
        spy = mocker.spy(puzzle_deps, "record_access")
        await record_puzzle_access(
            db=empty_db,
            visitor=visitor,
            puzzle_name=_puzzle_name,
        )
        spy.assert_called()

    @pytest.mark.parametrize(
        ["func_raises", "dependency_raises"],
        [
            (VisitorUIDInvalidError, VisitorUIDInvalidError),
            (PuzzleNotFoundError, UnknownPuzzleError),
        ],
    )
    async def test_record_puzzle_access_unknown(
        self,
        empty_db: Session,
        mocker: MockerFixture,
        func_raises: Exception,
        dependency_raises: Exception,
    ) -> None:
        """Test that failing recording access raises correct exception"""
        mocker.patch(
            "openday_scavenger.api.puzzles.dependencies.record_access",
            side_effect=func_raises,
        )
        with pytest.raises(dependency_raises):  # type: ignore  # possibly https://github.com/microsoft/pyright/discussions/3988
            await record_puzzle_access(
                db=empty_db,
                visitor=Mock(uid="foo", is_active=True),
                puzzle_name="bar",
            )
