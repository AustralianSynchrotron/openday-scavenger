import pytest

from openday_scavenger.puzzles.shuffleanagram.service import (
    INITIAL_WORDS,
    _shuffle_word,
    get_initial_word,
    get_shuffled_word,
    get_subpuzzle_name,
)

# I'm using the fixture known_puzzle_and_subpuzzle_names to parametrize the tests
# so that any test added to the router will be automatically tested.
# Each time that known_puzzle_and_subpuzzle_names is used, it's as if I were using
# @pytest.mark.parametrize(["puzzle_name", "subpuzzle_name"], [...])

# To make it easier to remember that using the fixture is the same as parametrizing,
# I'm putting _parametrized at the end of the test name


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

        Args:
            puzzle_name (str): The full name of the puzzle.
            expected (str): The expected subpuzzle name.

        Asserts:
            The subpuzzle name is as expected.
        """
        subpuzzle_name = await get_subpuzzle_name(puzzle_name)
        assert subpuzzle_name == expected

    async def test_get_subpuzzle_name_parametrized(
        self, known_puzzle_and_subpuzzle_names: tuple[str, str]
    ) -> None:
        """
        Test the get_subpuzzle_name function.

        This test verifies that the get_subpuzzle_name function returns the correct subpuzzle name.
        Parametrized so that it tests all the puzzles of this type that were added to the router.

        Args:
            known_puzzle_and_subpuzzle_names (tuple[str, str]): A tuple containing
                the puzzle name and the expected subpuzzle
        Asserts:
            The subpuzzle name is correct.
        """
        puzzle_name, expected = known_puzzle_and_subpuzzle_names
        subpuzzle_name = await get_subpuzzle_name(puzzle_name)
        assert subpuzzle_name == expected

    async def test_puzzle_added_to_router_correctly_parametrized(
        self, known_puzzle_and_subpuzzle_names: tuple[str, str]
    ) -> None:
        """
        Test the puzzle names added to the router.
        Check that all puzzles added to the router have a subpuzzle name,
        that the subpuzzle name is a key in the dict of initial words,
        and that the corresponding initial word is the same as the subpuzzle name.

        Args:
            known_puzzle_and_subpuzzle_names (tuple[str, str]): A tuple containing
                the puzzle name and the expected subpuzzle

        Asserts:
            The subpuzzle name is truthy
            The subpuzzle name is in the dict of initial words
            The corresponding initial word is the same as the subpuzzle name

        """
        puzzle_name, _subpuzzle_name = known_puzzle_and_subpuzzle_names
        subpuzzle_name = await get_subpuzzle_name(puzzle_name)
        assert subpuzzle_name
        assert subpuzzle_name in INITIAL_WORDS
        assert subpuzzle_name == _subpuzzle_name
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
