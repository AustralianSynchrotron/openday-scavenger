import random
from typing import Annotated

from fastapi import Depends

from openday_scavenger.api.puzzles.dependencies import get_puzzle_name

PUZZLE_FAMILY = "shuffleanagram"

# Initial words for each puzzle
# for simplicity of debugging,
# the keys in this dict are just the same as the puzzle names
INITIAL_WORDS: dict[str, str] = {
    "probations": "PROBATIONS",
    "toerags": "TOERAGS",
    "reboots": "REBOOTS",
    "crumpets": "CRUMPETS",
}


async def get_subpuzzle_name(puzzle_name: Annotated[str, Depends(get_puzzle_name)]) -> str:
    """get_subpuzzle_name Return the puzzle name from the full puzzle name,
    e.g. shuffleanagram-probations -> probations
    Should be used with Depends

    Args:
        puzzle_name (str): The full puzzle name as returned by get_puzzle_name

    Returns:
        str: The subpuzzle name. This is the part of the puzzle name after the family name and the hyphen
    """
    return puzzle_name.partition(f"{PUZZLE_FAMILY}-")[-1]


async def get_initial_word(subpuzzle_name: Annotated[str, Depends(get_subpuzzle_name)]) -> str:
    """get_initial_word Get the initial word for the puzzle.
    Should be used with Depends

    Args:
        subpuzzle_name (str): The subpuzzle name

    Returns:
        str: The initial word for the puzzle
    """

    return INITIAL_WORDS[subpuzzle_name]


async def _shuffle_word(word_in: str) -> str:
    """shuffle_word Shuffle the word

    Args:
        word_in (str): The word to shuffle

    Returns:
        str: The shuffled word
    """
    # while loop because I got caught out by a test where the shuffled word was the same as the input word
    word_out = word_in
    attempts = 0
    while (word_out == word_in) and (attempts < 100):
        word_out = "".join(random.sample(word_in, len(word_in)))
        attempts += 1
        # I am aware that putting a loop guard in here is ridiculous,
        # but just in case we decide to be really really silly and have a puzzle like "aaaa"...

    return word_out


async def get_shuffled_word(initial_word: Annotated[str, Depends(get_initial_word)]) -> str:
    """shuffled_word Get the shuffled word for the puzzle.
    Should be used with Depends

    Args:
        initial_word (str): The initial word to shuffle

    Returns:
        str: The shuffled word
    """
    word = await _shuffle_word(initial_word)
    return word
