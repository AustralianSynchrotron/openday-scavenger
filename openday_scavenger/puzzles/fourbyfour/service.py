import json
import random
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel, Field

from openday_scavenger.api.visitors.dependencies import get_auth_visitor
from openday_scavenger.api.visitors.schemas import VisitorAuth

from .exceptions import GameOverException, PuzzleSolvedException

SOLUTION = "car_models:mnop;farm_animals:efgh;fruit:ijkl;i.t._companies:abcd"  # not the real solution, we'll get that from the db. Also the words will change.


@lru_cache
def get_solution_from_db() -> str:
    # ask the database for the solution. Cached so it should only happen infrequently
    # database call here
    return SOLUTION


def parse_solution(solution: str) -> dict[str, set[str]]:
    """Parse the solution string into a dictionary of category ID to a set of word ids"""
    categories = {}
    for category in solution.split(";"):
        category_id, word_ids = category.split(":")
        categories[category_id] = set(word_ids)
    return categories


def get_parsed_solution() -> dict[str, set[str]]:
    return parse_solution(get_solution_from_db())


@lru_cache
def get_words_from_file() -> list[dict[str, str]]:
    with open(Path(__file__).resolve().parent / "static" / "words.json") as f:
        return json.load(f)["items"]


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
        _word_ids_in_sol = [_id for _ids in _sol.values() for _id in _ids]
        _words_in_sol = [_w for _w in get_words_from_file() if _w["id"] in _word_ids_in_sol]
        words = [Word.model_validate(_w) for _w in _words_in_sol]

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
            raise ValueError("Not enough words selected. But UI should prevent this")

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
            raise GameOverException("GAME OVER")  # how do we implement this...?
        # still raise so we can show a message to the user
        raise ValueError("Selection is incorrect")
        # TODO: # implement "one away"

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
            _sol += "".join(sorted([word.id for word in category.words]))
            solution.append(_sol)
        return ";".join(solution)


status_registry: dict[str | None, "PuzzleStatus"] = defaultdict(PuzzleStatus.new)


def get_status_registry() -> dict[str | None, "PuzzleStatus"]:
    return status_registry


async def get_status(
    visitor: Annotated[VisitorAuth, Depends(get_auth_visitor)],
    status_registry: Annotated[dict[str | None, PuzzleStatus], Depends(get_status_registry)],
) -> PuzzleStatus:
    return status_registry[visitor.uid]


async def reset_status(
    visitor: Annotated[VisitorAuth, Depends(get_auth_visitor)],
    status_registry: Annotated[dict[str | None, PuzzleStatus], Depends(get_status_registry)],
) -> PuzzleStatus:
    status_registry[visitor.uid] = PuzzleStatus.new()
    return status_registry[visitor.uid]


async def delete_status(
    visitor: Annotated[VisitorAuth, Depends(get_auth_visitor)],
    status_registry: Annotated[dict[str | None, PuzzleStatus], Depends(get_status_registry)],
) -> None:
    status_registry.pop(visitor.uid, None)
