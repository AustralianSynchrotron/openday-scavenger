import base64
import json
from functools import lru_cache
from typing import Annotated

from pydantic import BaseModel, Field

SOLUTION = "1:abcd-2:efgh-3:ijkl-4:mnop"  # not the real solution, we'll get that from the db


@lru_cache
def get_solution_from_db() -> str:
    # ask the database for the solution. Cached so it should only happen infrequently
    # database call here
    return SOLUTION


def parse_solution(solution: str) -> dict[int, set[str]]:
    """Parse the solution string into a dictionary of category ID to a set of word ids"""
    categories = {}
    for category in solution.split("-"):
        category_id, word_ids = category.split(":")
        categories[int(category_id)] = set(word_ids)
    return categories


def get_parsed_solution() -> dict[int, set[str]]:
    return parse_solution(get_solution_from_db())


def encode_json_to_base64(json_obj):
    # Convert the JSON object to a JSON string
    json_str = json.dumps(json_obj)

    # Encode the JSON string to bytes
    json_bytes = json_str.encode("utf-8")

    # Encode the bytes to Base64
    base64_bytes = base64.b64encode(json_bytes)

    # Convert Base64 bytes to a string
    base64_str = base64_bytes.decode("utf-8")

    return base64_str


class Word(BaseModel):
    id: Annotated[str, Field("max_length=1")]
    word: str
    is_selected: bool = False

    def toggle_selected(self) -> None:
        self.is_selected = not self.is_selected


class Category(BaseModel):
    id: int
    name: str
    description: str = ""
    words: list[Word] = []
    is_solved: bool = False

    def add_words(self, word: Word) -> None:
        self.words.append(word)

    def mark_as_solved(self) -> None:
        self.is_solved = True


class PuzzleStatus(BaseModel):
    categories: Annotated[list[Category], Field(min_length=4, max_length=4)]
    words: Annotated[list[Word], Field(max_length=16)]
    mistakes_available: int = 4
    selectable_at_once: int = 4

    @property
    def solution(self) -> dict[int, set[str]]:
        return get_parsed_solution()

    @property
    def n_selected_words(self) -> int:
        return len([word for word in self.words if word.is_selected])

    @property
    def can_submit(self) -> bool:
        return self.n_selected_words == self.selectable_at_once

    def get_word(self, word_id: int) -> Word:
        for word in self.words:
            if word.id == word_id:
                return word
        raise ValueError("Word not found")

    def get_category(self, category_id: int) -> Category:
        for category in self.categories:
            if category.id == category_id:
                return category
        raise ValueError("Category not found")

    def get_selected_words(self) -> list[Word]:
        return [word for word in self.words if word.is_selected]

    def toggle_word_selection(self, word_id: int) -> None:
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
                return
        # if we reach this point, the selection was incorrect.
        # was this the last mistake?
        self.mistakes_available -= 1
        if self.mistakes_available == 0:
            raise ValueError("GAME OVER")  # how do we implement this...?
        # still raise so we can show a message to the user
        raise ValueError("Selection is incorrect")
        # TODO: # implement "one away"
