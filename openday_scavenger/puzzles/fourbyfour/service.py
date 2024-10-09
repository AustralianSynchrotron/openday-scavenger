import random
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from openday_scavenger.api.db import get_db
from openday_scavenger.api.puzzles.dependencies import get_puzzle_name
from openday_scavenger.api.puzzles.service import get_puzzle_state, set_puzzle_state
from openday_scavenger.api.visitors.dependencies import get_auth_visitor
from openday_scavenger.api.visitors.schemas import VisitorAuth

from .exceptions import GameOverException, PuzzleSolvedException

# solution must have categories in alphabetical order
# and words in alphabetical order within each category
SOLUTION = "car_models:beetle,bronco,mustang,panda;farm_animals:chicken,cow,horse,pig;fruit:apple,banana,grape,orange;i.t._companies:alphabet,meta,microsoft,nvidia"  # not the real solution, we'll get that from the db. Also the words will change.


@lru_cache
def get_solution_from_db() -> str:
    # ask the database for the solution. Cached so it should only happen infrequently
    # database call here
    return SOLUTION


def parse_solution(solution: str) -> dict[str, set[str]]:
    """Parse the solution string
    into a dictionary of category ID to a set of word ids"""
    categories = {}
    for category in solution.split(";"):
        category_id, word_ids = category.split(":")
        categories[category_id] = set(word_ids.split(","))
    return categories


def get_parsed_solution() -> dict[str, set[str]]:
    return parse_solution(get_solution_from_db())


class Word(BaseModel):
    id: Annotated[str, Field("max_length=1")]
    word: str
    is_selected: bool = False

    def toggle_selected(self) -> None:
        self.is_selected = not self.is_selected


class Category(BaseModel):
    id: str
    words: list[Word] = []
    is_solved: bool = False

    @property
    def name(self) -> str:
        return self.id.replace("_", " ").title()

    def add_words(self, word: Word) -> None:
        self.words.append(word)

    def mark_as_solved(self) -> None:
        self.is_solved = True


class PuzzleStatus(BaseModel):
    categories: Annotated[list[Category], Field(min_length=4, max_length=4)]
    words: Annotated[list[Word], Field(max_length=16)]
    mistakes_available: int = 4
    selectable_at_once: int = 4

    @classmethod
    def new(cls) -> "PuzzleStatus":
        # get and parse solution
        # solution is a dict of category ID to a set of word IDs
        _sol = get_parsed_solution()
        categories = [Category(id=category_id) for category_id in _sol.keys()]

        # create the words
        words = [Word(id=_w, word=_w) for _, _ww in _sol.items() for _w in _ww]

        # shuffle the words
        random.shuffle(words)
        return cls(categories=categories, words=words)

    @property
    def solution(self) -> dict[str, set[str]]:
        return get_parsed_solution()

    @property
    def n_selected_words(self) -> int:
        return len([word for word in self.words if word.is_selected])

    @property
    def can_submit(self) -> bool:
        return self.n_selected_words == self.selectable_at_once

    def get_word(self, word_id: str) -> Word:
        for word in self.words:
            if word.id == word_id:
                return word
        raise ValueError("Word not found")

    def get_category(self, category_id: str) -> Category:
        for category in self.categories:
            if category.id == category_id:
                return category
        raise ValueError("Category not found")

    def get_selected_words(self) -> list[Word]:
        return [word for word in self.words if word.is_selected]

    def toggle_word_selection(self, word_id: str) -> None:
        """Toggle a word's status between selected and not selected.
        Make sure that the number of selected words does not exceed the
        selectable_at_once limit.

        Start by getting the current word.
        If the word is selected, deselect it, return.
        If the word is not selected, check if we're allowed to select it
        (i.e. the number of currently selected words is less than the limit)
        """
        word = self.get_word(word_id)
        # we can always deselect a word
        if word.is_selected:
            word.toggle_selected()
            return
        # if we're selecting, check if we're allowed to
        if self.n_selected_words < self.selectable_at_once:
            word.toggle_selected()
        else:
            raise ValueError("Cannot select more words")  # forbidden

    def deselect_all_words(self) -> None:
        for word in self.words:
            word.is_selected = False

    def shuffle_words(self) -> None:
        random.shuffle(self.words)

    def submit_selection(self) -> None:
        """When user submits a selection of 4 words, check against the solution
        if the selected words are all in the same category"""
        # double check we were allowed to submit (if UI validation fails)
        if not self.can_submit:
            raise ValueError("Not enough words selected. " "But UI should prevent this")

        selected_words = self.get_selected_words()
        selected_words_ids = set(word.id for word in selected_words)
        for category_id, word_ids in self.solution.items():
            if word_ids == selected_words_ids:
                # the set of selected words matches a solution!
                # let's mark the category as solved and move the words into it
                category = self.get_category(category_id)
                category.mark_as_solved()
                for word in selected_words:
                    category.add_words(word)
                    self.words.remove(word)
                if all(category.is_solved for category in self.categories):
                    raise PuzzleSolvedException("Well done! You solved the puzzle!")
                return
        # if we reach this point, the selection was incorrect.
        # was this the last mistake?
        self.mistakes_available -= 1
        if self.mistakes_available == 0:
            # raise game over, so we can handle it differently in the views
            raise GameOverException("GAME OVER")
        # still raise so we can show a message to the user
        raise ValueError("Selection is incorrect")
        # TODO: # implement "one away?" hint

    def __repr__(self) -> str:
        msg = "PuzzleStatus:\n"
        # categories
        msg += "Categories:\n"
        for category in self.categories:
            if category.is_solved:
                msg += f"  {category.id}.{category.name}\n"
                msg += "   " + ", ".join(word.word for word in category.words) + "\n"
        # words not yet in categories
        if self.words:
            msg += "Words:\n"
            for ii, word in enumerate(self.words):
                if ii % 4 == 0:
                    msg += "  "
                msg += f"({word.id}){word.word.upper() if word.is_selected else word.word}\t\t"
                if ii % 4 == 3:
                    msg += "\n"
        # mistakes available
        msg += "Mistakes remaining: "
        msg += "o" * self.mistakes_available
        msg += "x" * (4 - self.mistakes_available)
        msg += "\n"

        return msg

    def export_solution(self) -> str:
        solution = []
        # categories are listed in the same order as they were created from the solution
        for category in self.categories:
            _sol = f"{category.id}:"
            _sol += ",".join(sorted([word.id for word in category.words]))
            solution.append(_sol)
        return ";".join(solution)


# The puzzle stores state in the database.
# The mechanism to store state in the database is provided by common code
# in the api.puzzles.service module.
# It does not work if sessions are disabled.
# If sessions are disabed, the user has uid None.
# In this case, the puzzle will not be able to store state in the database.
# Implement a simple singleton pattern to store the status of the None visitor
class PuzzleStatusSingleton:
    def __init__(self):
        self.status = PuzzleStatus.new()

    def get(self):
        return self.status

    def set(self, status: PuzzleStatus):
        self.status = status


status_of_visitor_none = PuzzleStatusSingleton()


async def get_status_none() -> PuzzleStatus:
    return status_of_visitor_none.get()


async def set_status_none(status: PuzzleStatus) -> PuzzleStatus:
    status_of_visitor_none.set(status)
    return status_of_visitor_none.get()


async def get_status(
    visitor: Annotated[VisitorAuth, Depends(get_auth_visitor)],
    db: Annotated["Session", Depends(get_db)],
    puzzle_name: Annotated[str, Depends(get_puzzle_name)],
) -> PuzzleStatus:
    # get the status from the database
    if visitor.uid is None:
        return await get_status_none()

    state_from_db = get_puzzle_state(
        db,
        puzzle_name=puzzle_name,
        visitor_auth=visitor,
    )
    # get_puzzle_state will raise if the visitor is unknown or the puzzle is unknown.
    # but will return falsy if the visitor has not yet interacted with the puzzle.

    # If it's the first interaction, and we got a falsy, create a new status
    # and register it
    if not state_from_db:
        status = PuzzleStatus.new()
        state_to_db = status.model_dump()
        set_puzzle_state(
            db,
            puzzle_name=puzzle_name,
            visitor_auth=visitor,
            state=state_to_db,
        )
        state_from_db = get_puzzle_state(
            db,
            puzzle_name=puzzle_name,
            visitor_auth=visitor,
        )

    # restore status (pydantic model) from the database state (dict)
    status = PuzzleStatus.model_validate(state_from_db)

    return status


async def set_status(
    status: PuzzleStatus,
    visitor: Annotated[VisitorAuth, Depends(get_auth_visitor)],
    db: Annotated["Session", Depends(get_db)],
    puzzle_name: Annotated[str, Depends(get_puzzle_name)],
) -> PuzzleStatus:
    # handle the case where the visitor is None because sessions are disabled
    # and common code does not handle it
    if visitor.uid is None:
        # since we're working on a reference of the status,
        # we should just be able to return the input
        return await set_status_none(status)

    set_puzzle_state(
        db,
        puzzle_name=puzzle_name,
        visitor_auth=visitor,
        state=status.model_dump(),
    )
    return await get_status(visitor=visitor, db=db, puzzle_name=puzzle_name)


async def reset_status(
    visitor: Annotated[VisitorAuth, Depends(get_auth_visitor)],
    db: Annotated["Session", Depends(get_db)],
    puzzle_name: Annotated[str, Depends(get_puzzle_name)],
) -> PuzzleStatus:
    # write an empty status to the database
    status = PuzzleStatus.new()

    if visitor.uid is None:
        # sessions are disabled, can't store state in the database,
        # so store it in the singleton
        return await set_status_none(status)

    set_puzzle_state(
        db,
        puzzle_name=puzzle_name,
        visitor_auth=visitor,
        state=status.model_dump(),
    )
    return await get_status(visitor=visitor, db=db, puzzle_name=puzzle_name)
