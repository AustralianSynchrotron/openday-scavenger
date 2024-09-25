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
    Should be used with Depends"""
    return puzzle_name.split("-")[-1]


async def get_initial_word(subpuzzle_name: Annotated[str, Depends(get_subpuzzle_name)]) -> str:
    """get_initial_word Get the initial word for the puzzle.
    Should be used with Depends"""

    return INITIAL_WORDS.get(subpuzzle_name, "PROBATIONS")


async def shuffle_word(word_in: str) -> str:
    """shuffle_word Shuffle the word"""
    word_out = "".join(random.sample(word_in, len(word_in)))
    return word_out
