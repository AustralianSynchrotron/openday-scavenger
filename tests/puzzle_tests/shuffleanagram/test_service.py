import pytest

from openday_scavenger.puzzles.shuffleanagram.service import (
    INITIAL_WORDS,
    PUZZLE_FAMILY,
    _shuffle_word,
    get_initial_word,
    get_shuffled_word,
    get_subpuzzle_name,
)


def get_shuffleanagram_puzzle_names_added_to_router() -> list[str]:
    from pathlib import Path

    from starlette.routing import Route

    from openday_scavenger.puzzles import router as puzzle_router

    puzzle_names = []
    for route in puzzle_router.routes:
        assert isinstance(route, Route)  # for linter
        if route.path.startswith(f"/{PUZZLE_FAMILY}"):
            puzzle_names.append(Path(route.path).parts[1])
    return puzzle_names


SHUFFLEANAGRAM_ADDED_PUZZLES = get_shuffleanagram_puzzle_names_added_to_router()


@pytest.mark.asyncio
class TestShuffleAnagram:
    @pytest.mark.parametrize(
        ["puzzle_name", "expected"],
        [
            ("shuffleanagram-foo", "foo"),
            ("shuffleanagram-bar", "bar"),
            ("shuffleanagram-foo-bar", "foo-bar"),
        ],
    )
    async def test_get_subpuzzle_name(self, puzzle_name: str, expected: str) -> None:
        """
        Test the get_subpuzzle_name function.

        This test verifies that the get_subpuzzle_name function returns the correct subpuzzle name.

        Asserts:
            The subpuzzle name is correct.
        """

        subpuzzle_name = await get_subpuzzle_name(puzzle_name)
        assert subpuzzle_name == expected

    @pytest.mark.parametrize("puzzle_name", SHUFFLEANAGRAM_ADDED_PUZZLES)
    async def test_puzzles_added_to_router_correctly(self, puzzle_name: str) -> None:
        """
        Test the puzzle names added to the router.

        This test verifies that:
        - if a puzzle is added to the router, it has a subpuzzle name
        - its subpuzzle name is a key in the dict of initial words
        - the corresponding initial word is the same as the subpuzzle name

        the puzzle names added to the router are correct.

        Asserts:
            The puzzle name is in the list of added puzzles.
        """
        subpuzzle_name = await get_subpuzzle_name(puzzle_name)
        assert subpuzzle_name
        assert subpuzzle_name in INITIAL_WORDS
        _initial_word = await get_initial_word(subpuzzle_name)
        assert _initial_word.lower() == subpuzzle_name.lower()

    @pytest.mark.parametrize(
        "word_in",
        [
            "potato",
            "banana",
            "supercalifrageslisticexpialidocious",
            "antidisestablishmentarianism",
        ]
        + [k for k in INITIAL_WORDS],
    )
    async def test_get_shuffled_word(self, word_in: str) -> None:
        """
        Test the shuffle_word function.

        This test verifies that the shuffle_word function shuffles the input word correctly.

        Args:
            word_in (str): The word to shuffle.

        Asserts:
            The shuffled word is not the same as the input word.
            The shuffled word is a permutation of the input word.
        """

        word_out = await get_shuffled_word(word_in)
        assert word_out != word_in
        assert sorted(word_out) == sorted(word_in)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "word_in",
        [
            "aaaaaa",
            "bbbbbb",
        ],
    )
    async def test__shuffle_word_silly(self, word_in: str) -> None:
        """
        Test the _shuffle_word function.

        This test verifies that the _shuffle_word function eventually returns even if we pass an input word that is all the same character.

        Args:
            word_in (str): The word to shuffle. Must be all same letters for this test to make sense.

        Asserts:
            The shuffled word is the same as the input word.
        """
        assert (
            len(set(word_in)) == 1
        ), "This test only makes sense for words with all the same characters"
        word_out = await _shuffle_word(word_in)
        assert word_out == word_in
