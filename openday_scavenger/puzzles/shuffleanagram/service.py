import random
from pathlib import PurePosixPath

from fastapi import Request
from fastapi.logger import logger

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


def get_full_puzzle_name(request: Request) -> str:
    """get_full_puzzle_name Extract the full puzzle name from the request URL:
    it's the part of the path that starts with the PUZZLE_FAMILY
    Should be used with Depends"""
    try:
        full_puzzle_name = [
            _p for _p in PurePosixPath(request.url.path).parts if _p.startswith(PUZZLE_FAMILY)
        ]
        if not full_puzzle_name:
            raise ValueError("no puzzle name found")  # we should *not* get here
        full_puzzle_name = full_puzzle_name[0]

    except Exception as e:
        logger.error(f"error getting puzzle name from {request.url.path}: {e}; ")
        full_puzzle_name = PUZZLE_FAMILY

    return full_puzzle_name


def get_puzzle_name(request: Request) -> str:
    """get_puzzle_name Return the puzzle name from the full puzzle name,
    e.g. shuffleanagram-probations -> probations
    Should be used with Depends"""
    full_puzzle_name = get_full_puzzle_name(request)
    return full_puzzle_name.split("-")[-1]


def get_initial_word(request: Request) -> str:
    """get_initial_word Get the initial word for the puzzle.
    Should be used with Depends"""
    puzzle_name = get_puzzle_name(request)
    return INITIAL_WORDS.get(puzzle_name, "PROBATIONS")


def shuffle_word(word_in: str) -> str:
    """shuffle_word Shuffle the word"""
    word_out = "".join(random.sample(word_in, len(word_in)))
    return word_out
