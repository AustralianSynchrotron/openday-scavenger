import json
import random
from enum import Enum
from pathlib import Path

with open(Path(__file__).resolve().parent / "element_list.json") as f:
    elements = json.load(f)

with open(Path(__file__).resolve().parent / "questions.json") as f:
    questions = json.load(f)


def generate_options(answer: list[str], count: int = 5):
    """Generate random options including the answer element"""

    # Ensure the answer is in the options
    options = answer.copy()

    # Remove the answer from the list of possible options
    remaining_elements = [e for e in elements if e not in answer]

    # Randomly select additional options
    additional_options = random.sample(remaining_elements, count - len(answer))
    options.extend(additional_options)

    return options


class Elements(Enum):
    Au = "Au"
    Fe = "Fe"
    Cu = "Cu"


# Constants
COUNT_LESS = 5
COUNT_MORE = 10

# the answer is in the database. These hard-coded answers must be matched with the database
# openday_scavenger/puzzles/periodic/static/sql/initiate.sql
GENERAL_ANSWER = Elements.Au
GENERAL_OPTIONS_LESS = generate_options([GENERAL_ANSWER], COUNT_LESS)
GENERAL_OPTIONS_MORE = generate_options(GENERAL_OPTIONS_LESS, COUNT_MORE)

XAS_ANSWER = Elements.Fe
XAS_OPTIONS_LESS = generate_options([XAS_ANSWER], COUNT_LESS)
XAS_OPTIONS_MORE = generate_options(XAS_OPTIONS_LESS, COUNT_MORE)

MEX_ANSWER = Elements.Cu
MEX_OPTIONS_LESS = generate_options([MEX_ANSWER], COUNT_LESS)
MEX_OPTIONS_MORE = generate_options(MEX_OPTIONS_LESS, COUNT_MORE)


# the key is the suffix of the puzzle (path)
# e.g. the path /puzzles/element_xas/ will use the questions and options for the "xas" key
questions_answers = {
    "general": {
        "questions": questions[GENERAL_ANSWER.value],
        "options_less": GENERAL_OPTIONS_LESS,
        "options_more": GENERAL_OPTIONS_MORE,
    },
    "xas": {
        "questions": questions[XAS_ANSWER.value],
        "options_less": XAS_OPTIONS_LESS,
        "options_more": XAS_OPTIONS_MORE,
    },
    "mex": {
        "questions": questions[MEX_ANSWER.value],
        "options_less": MEX_OPTIONS_LESS,
        "options_more": MEX_OPTIONS_MORE,
    },
}
