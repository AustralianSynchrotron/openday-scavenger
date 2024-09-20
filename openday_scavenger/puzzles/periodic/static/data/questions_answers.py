import json
import random
from pathlib import Path

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

GENERAL_ANSWER = "Au"
GENERAL_OPTIONS_LESS = generate_options([GENERAL_ANSWER], COUNT_LESS)
GENERAL_OPTIONS_MORE = generate_options(GENERAL_OPTIONS_LESS, COUNT_MORE)

XAS_ANSWER = "Fe"
XAS_OPTIONS_LESS = generate_options([XAS_ANSWER], COUNT_LESS)
XAS_OPTIONS_MORE = generate_options(XAS_OPTIONS_LESS, COUNT_MORE)

MEX_ANSWER = "Cu"
MEX_OPTIONS_LESS = generate_options([MEX_ANSWER], COUNT_LESS)
MEX_OPTIONS_MORE = generate_options(MEX_OPTIONS_LESS, COUNT_MORE)


# the key is the suffix of the puzzle (path)
# e.g. the path /puzzles/element_xas/ will use the questions and options for the "xas" key
questions_answers = {
    "general": {
        "questions": [
            "General question 1",
            "General question 2",
            "General question 3",
        ],
        "options_less": GENERAL_OPTIONS_LESS,
        "options_more": GENERAL_OPTIONS_MORE,
    },
    "xas": {
        "questions": [
            "This element is essential for the production of hemoglobin in the human body and is often associated with red blood cells. What is it?",
            'The symbol for this element comes from its Latin name, "ferrum". Which element is this?',
            "This element is found in Earth's core and contributes to the planet's magnetic field. What is it?",
            "In ancient times, this element was used to make weapons and tools, and it still forms the backbone of modern infrastructure. What is it?",
            "This element oxidizes in air, forming a red-brown layer commonly known as rust. What is it?",
            "This transition metal is attracted to magnets and often used to create strong magnetic fields. What is it?",
        ],
        "options_less": XAS_OPTIONS_LESS,
        "options_more": XAS_OPTIONS_MORE,
    },
    "mex": {
        "questions": [
            "mex question 1",
            "mex question 2",
            "mex question 3",
        ],
        "options_less": MEX_OPTIONS_LESS,
        "options_more": MEX_OPTIONS_MORE,
    },
}
