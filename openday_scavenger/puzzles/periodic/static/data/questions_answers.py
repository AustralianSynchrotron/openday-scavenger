import json
import random
from pathlib import Path

with open(Path(__file__).resolve().parent / "element_list.json") as f:
    elements = json.load(f)


def generate_options(answer: str, count: int = 5):
    """Generate random options including the answer element"""

    # Ensure the answer is in the options
    options = [answer]

    # Remove the answer from the list of possible options
    remaining_elements = [e for e in elements if e != answer]

    # Randomly select additional options
    additional_options = random.sample(remaining_elements, count - 1)
    options.extend(additional_options)

    return options


# constants
GENERAL_ANSWER = "Au"
XAS_ANSWER = "Fe"
MEX_ANSWER = "Cu"

questions_answers = {
    "general": {
        "questions": [
            "General question 1",
            "General question 2",
            "General question 3",
        ],
        "answer": GENERAL_ANSWER,
        "options": generate_options(GENERAL_ANSWER),
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
        "answer": XAS_ANSWER,
        "options": generate_options(XAS_ANSWER),
    },
    "mex": {
        "questions": [
            "mex question 1",
            "mex question 2",
            "mex question 3",
        ],
        "answer": MEX_ANSWER,
        "options": generate_options(MEX_ANSWER),
    },
}
