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

# the answer is in the database. These hard-coded answers must be matched with the database
# openday_scavenger/puzzles/periodic/static/sql/initiate.sql
GENERAL_ANSWER = Elements.Au.value
XAS_ANSWER = Elements.Fe.value
MEX_ANSWER = Elements.Cu.value


# the key is the suffix of the puzzle (path)
# e.g. the path /puzzles/element_xas/ will use the questions and options for the "xas" key
beamline_questions = {
    "general": {
        "questions": questions_answers[GENERAL_ANSWER],
        "options_less": generate_options([GENERAL_ANSWER], COUNT_LESS),
        "options_more": generate_options(
            generate_options([GENERAL_ANSWER], COUNT_LESS), COUNT_MORE
        ),
    },
    "xas": {
        "questions": questions_answers[XAS_ANSWER],
        "options_less": generate_options([XAS_ANSWER], COUNT_LESS),
        "options_more": generate_options(generate_options([XAS_ANSWER], COUNT_LESS), COUNT_MORE),
    },
    "mex": {
        "questions": questions_answers[MEX_ANSWER],
        "options_less": generate_options([MEX_ANSWER], COUNT_LESS),
        "options_more": generate_options(generate_options([MEX_ANSWER], COUNT_LESS), COUNT_MORE),
    },
}
