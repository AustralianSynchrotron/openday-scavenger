import random

from fastapi import Request

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


async def get_subpuzzle_name(request: Request) -> str:
    """get_subpuzzle_name Return the puzzle name from the full puzzle name,
    e.g. shuffleanagram-probations -> probations
    Should be used with Depends"""
    puzzle_name = await get_puzzle_name(request)
    return puzzle_name.split("-")[-1]


async def get_initial_word(request: Request) -> str:
    """get_initial_word Get the initial word for the puzzle.
    Should be used with Depends"""

    subpuzzle_name = await get_subpuzzle_name(request)
    return INITIAL_WORDS.get(subpuzzle_name, "PROBATIONS")


async def shuffle_word(word_in: str) -> str:
    """shuffle_word Shuffle the word"""
    word_out = "".join(random.sample(word_in, len(word_in)))
    return word_out
