import json
import random
from pathlib import Path

from .questions_answers import Elements, questions_answers

with open(Path(__file__).resolve().parent / "element_list.json") as f:
    elements = json.load(f)


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


# Constants
COUNT_LESS = 5
COUNT_MORE = 10

# the answer is in the database.
# These hard-coded the key must be the same as the suffix of the puzzle (path)
# and answers must be matched with the database
# openday_scavenger/puzzles/periodic/static/sql/initiate.sql
beamline_answers = {
    "general": Elements.Au.value,
    "xas": Elements.Fe.value,
    "mex": Elements.Cu.value,
    "ads": Elements.Ni.value,
    "bsx": Elements.N.value,
    "mct": Elements.Ca.value,
    "mx": Elements.C.value,
    "pd": Elements.Si.value,
}


# the key is the suffix of the puzzle (path)
# e.g. the path /puzzles/element_xas/ will use the questions and options for the "xas" key
beamline_questions = {}
for suffix, answer in beamline_answers.items():
    beamline_questions[suffix] = {
        "questions": questions_answers[answer],
        "options_less": generate_options([answer], COUNT_LESS),
        "options_more": generate_options(generate_options([answer], COUNT_LESS), COUNT_MORE),
    }
