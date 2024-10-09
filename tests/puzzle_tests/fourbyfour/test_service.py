from typing import TYPE_CHECKING
from unittest.mock import Mock

import pytest
from pytest_mock.plugin import MockerFixture

from openday_scavenger.api.visitors.service import get_all as get_all_visitors
from openday_scavenger.puzzles.fourbyfour import service
from openday_scavenger.puzzles.fourbyfour.exceptions import (
    GameOverException,
    PuzzleSolvedException,
)
from openday_scavenger.puzzles.fourbyfour.service import (
    PuzzleStatus,
    get_parsed_solution,
    get_solution_from_db,
    get_status,
    get_status_none,
    reset_status,
    set_status,
)

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

PUZZLE_NAME = "fourbyfour"


class TestFourByFour:
    def test_constructor(
        self,
        mocker: MockerFixture,
    ) -> None:
        spies = [
            mocker.spy(service, "get_parsed_solution"),
            mocker.spy(service, "parse_solution"),
            mocker.spy(service, "get_solution_from_db"),
        ]
        _ = PuzzleStatus.new()

        for spy in spies:
            spy.assert_called_once()

    def test_get_word(
        self,
        new_puzzle: PuzzleStatus,
    ) -> None:
        _word = new_puzzle.words[0]
        word = new_puzzle.get_word(_word.id)
        assert id(word) == id(_word)

    def test_get_word_not_found(
        self,
        new_puzzle: PuzzleStatus,
    ) -> None:
        with pytest.raises(ValueError):
            new_puzzle.get_word("not_a_word")

    def test_get_category(
        self,
        new_puzzle: PuzzleStatus,
    ) -> None:
        _category = new_puzzle.categories[0]
        category = new_puzzle.get_category(_category.id)
        assert id(category) == id(_category)

    def test_get_category_not_found(
        self,
        new_puzzle: PuzzleStatus,
    ) -> None:
        with pytest.raises(ValueError):
            new_puzzle.get_category("not_a_category")

    def test_toggle_word_selection(
        self,
        new_puzzle: PuzzleStatus,
    ) -> None:
        _word = new_puzzle.words[0]
        new_puzzle.toggle_word_selection(_word.id)
        assert new_puzzle.get_word(_word.id).is_selected
        new_puzzle.toggle_word_selection(_word.id)
        assert not new_puzzle.get_word(_word.id).is_selected

    def test_toggle_word_selection_too_many(
        self,
        new_puzzle: PuzzleStatus,
    ) -> None:
        # select the first few words (up to selectable_at_once)
        for word in new_puzzle.words[: new_puzzle.selectable_at_once]:
            new_puzzle.toggle_word_selection(word.id)

        # try to select one more, should raise
        with pytest.raises(ValueError):
            new_puzzle.toggle_word_selection(new_puzzle.words[-1].id)

    def test_n_selected_words(
        self,
        new_puzzle: PuzzleStatus,
    ) -> None:
        assert new_puzzle.n_selected_words == 0
        new_puzzle.toggle_word_selection(new_puzzle.words[0].id)
        assert new_puzzle.n_selected_words == 1

    def test_deselect_all_words(
        self,
        new_puzzle: PuzzleStatus,
    ) -> None:
        for word in new_puzzle.words[: new_puzzle.selectable_at_once]:
            new_puzzle.toggle_word_selection(word.id)
        assert new_puzzle.n_selected_words == new_puzzle.selectable_at_once
        new_puzzle.deselect_all_words()
        assert new_puzzle.n_selected_words == 0

    def test_shuffle_words(
        self,
        new_puzzle: PuzzleStatus,
    ) -> None:
        word_ids = [word.id for word in new_puzzle.words]
        new_puzzle.shuffle_words()
        shuffled_word_ids = [word.id for word in new_puzzle.words]
        assert word_ids != shuffled_word_ids

    def test_can_submit(
        self,
        new_puzzle: PuzzleStatus,
    ) -> None:
        assert not new_puzzle.can_submit
        for word in new_puzzle.words[: new_puzzle.selectable_at_once]:
            new_puzzle.toggle_word_selection(word.id)
        assert new_puzzle.can_submit

    def test_submit_selection(
        self,
        new_puzzle: PuzzleStatus,
    ) -> None:
        parsed_solution = get_parsed_solution()
        for word_id in parsed_solution[new_puzzle.categories[0].id]:
            new_puzzle.toggle_word_selection(word_id)
        new_puzzle.submit_selection()
        assert new_puzzle.categories[0].is_solved

    def test_submit_selection_not_enough(
        self,
        new_puzzle: PuzzleStatus,
    ) -> None:
        with pytest.raises(ValueError):
            new_puzzle.submit_selection()

    def test_submit_selection_wrong(
        self,
        new_puzzle: PuzzleStatus,
    ) -> None:
        parsed_solution = get_parsed_solution()
        for category in new_puzzle.categories:
            word_id = next(iter(parsed_solution[category.id]))
            new_puzzle.toggle_word_selection(word_id)
        with pytest.raises(ValueError):
            new_puzzle.submit_selection()

    def test_submit_selection_game_over(
        self,
        new_puzzle: PuzzleStatus,
    ) -> None:
        parsed_solution = get_parsed_solution()
        for category in new_puzzle.categories:
            word_id = next(iter(parsed_solution[category.id]))
            new_puzzle.toggle_word_selection(word_id)
        while new_puzzle.mistakes_available > 1:
            with pytest.raises(ValueError):
                new_puzzle.submit_selection()
        with pytest.raises(GameOverException):
            new_puzzle.submit_selection()

    def test__repr__(
        self,
        new_puzzle: PuzzleStatus,
    ) -> None:
        parsed_solution = get_parsed_solution()
        out = repr(new_puzzle)
        assert "PuzzleStatus" in out
        assert "Categories" in out
        assert "Words" in out
        assert "Mistakes remaining" in out
        assert "oooo" in out

        # create one wrong selection and submit it
        for category in new_puzzle.categories:
            word_id = next(iter(parsed_solution[category.id]))
            new_puzzle.toggle_word_selection(word_id)
        with pytest.raises(ValueError):
            new_puzzle.submit_selection()
        assert "ooox" in repr(new_puzzle)
        new_puzzle.deselect_all_words()

        for word_id in parsed_solution[new_puzzle.categories[0].id]:
            new_puzzle.toggle_word_selection(word_id)
        new_puzzle.submit_selection()

        assert new_puzzle.categories[0].id in repr(new_puzzle)

    def test__repr__solved(
        self,
        new_puzzle: PuzzleStatus,
    ) -> None:
        parsed_solution = get_parsed_solution()
        for category in parsed_solution:
            for word_id in parsed_solution[category]:
                new_puzzle.toggle_word_selection(word_id)
            try:
                new_puzzle.submit_selection()
            except PuzzleSolvedException:
                # expected, at the end!
                assert all(category.is_solved for category in new_puzzle.categories)
        assert "Words" not in repr(new_puzzle)

    def test_export_solution(
        self,
        new_puzzle: PuzzleStatus,
    ) -> None:
        parsed_solution = get_parsed_solution()
        for category in parsed_solution:
            for word_id in parsed_solution[category]:
                new_puzzle.toggle_word_selection(word_id)
            try:
                new_puzzle.submit_selection()
            except PuzzleSolvedException:
                # expected, at the end!
                assert all(category.is_solved for category in new_puzzle.categories)

        assert new_puzzle.export_solution() == get_solution_from_db()

    @pytest.mark.asyncio
    async def test_get_status_noauth(
        self,
        mocker: MockerFixture,
    ) -> None:
        """
        Test getting a status for an unknown visitor.
        """
        _spy = mocker.spy(service, "get_status_none")
        _spy_db = mocker.spy(service, "get_puzzle_state")
        _spy_singleton = mocker.spy(service.status_of_visitor_none, "get")
        visitor = Mock(uid=None)
        db = Mock()

        ss = await get_status(
            visitor,
            db=db,
            puzzle_name="foo",
        )

        assert isinstance(ss, PuzzleStatus)
        _spy.assert_called()
        _spy_db.assert_not_called()
        _spy_singleton.assert_called()
        assert id(ss) == id(await get_status_none())

    @pytest.mark.asyncio
    async def test_reset_status_noauth(self, mocker: MockerFixture) -> None:
        _spy_singleton = mocker.spy(service.status_of_visitor_none, "get")
        visitor = Mock(uid=None)
        db = Mock()
        ss = await get_status(visitor, db=db, puzzle_name="foo")
        new_ss = await reset_status(visitor, db=db, puzzle_name="foo")
        assert new_ss is not ss
        _spy_singleton.assert_called()

    @pytest.mark.asyncio
    async def test_set_status_noauth(self, mocker: MockerFixture) -> None:
        _spies_singleton = [
            mocker.spy(service.status_of_visitor_none, "get"),
            mocker.spy(service.status_of_visitor_none, "set"),
        ]
        visitor = Mock(uid=None)
        db = Mock()
        ss = await get_status(visitor, db=db, puzzle_name="foo")
        # modify the status
        ss.toggle_word_selection(ss.words[0].id)
        still_ss = await set_status(ss, visitor, db=db, puzzle_name="foo")
        assert id(still_ss) == id(ss)
        for spy in _spies_singleton:
            spy.assert_called()

    @pytest.mark.asyncio
    async def test_get_set_reset_status_auth(
        self,
        mocker: MockerFixture,
        initialised_db: "Session",
    ) -> None:
        """
        Test getting, setting, a status for a visitor.
        Single test because we need to test these in order
        """

        # get a visitor
        visitors = get_all_visitors(db_session=initialised_db)
        if len(visitors) == 0:
            raise ValueError("No visitors in db")
        uid = visitors[0][0].uid
        visitor = Mock(uid=uid, is_authenticated=True)

        # test get_status
        _spies = [
            mocker.spy(service.PuzzleStatus, "new"),
            mocker.spy(service, "get_puzzle_state"),
            mocker.spy(service, "set_puzzle_state"),
        ]
        _spies_singleton = [
            mocker.spy(service.status_of_visitor_none, "get"),
            mocker.spy(service.status_of_visitor_none, "set"),
            mocker.spy(service, "get_status_none"),
            mocker.spy(service, "set_status_none"),
        ]

        ss = await get_status(
            visitor,
            db=initialised_db,
            puzzle_name=PUZZLE_NAME,
        )

        assert isinstance(ss, PuzzleStatus)

        # test set status
        # modify the status
        ss.toggle_word_selection(ss.words[0].id)
        mod_ss = await set_status(
            ss,
            visitor,
            db=initialised_db,
            puzzle_name=PUZZLE_NAME,
        )
        assert isinstance(mod_ss, PuzzleStatus)
        # not the same id of status because it's a new object after
        # going through the db
        assert id(mod_ss) != id(ss)

        # test reset status
        reset_ss = await reset_status(
            visitor,
            db=initialised_db,
            puzzle_name=PUZZLE_NAME,
        )
        assert isinstance(reset_ss, PuzzleStatus)
        assert id(reset_ss) != id(ss)

        for word in reset_ss.words:
            assert not word.is_selected

        for spy in _spies:
            spy.assert_called()

        for spy in _spies_singleton:
            spy.assert_not_called()
