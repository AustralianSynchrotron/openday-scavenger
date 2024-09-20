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

# the answer is in the database. These hard-coded answers must be matched with the database
# openday_scavenger/puzzles/periodic/static/sql/initiate.sql
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
            "This element's chemical symbol is derived from the Latin word 'Aurum.' What is it?",
            "Which precious metal is highly valued for its use in jewelry and electronics due to its conductivity and resistance to corrosion?",
            "This element has an atomic number of 79 and is known for its bright yellow color. What is it?",
            "Which element is often used to back currencies and historically served as the basis for the gold standard?",
            "This metal is malleable enough to be hammered into thin sheets and used for gilding. What is the element?",
            "Which element is considered a noble metal and is frequently awarded in Olympic medals for first place?",
            "This element is widely found in nature but often mixed with other materials, requiring a refining process. What is the symbol of this element?",
            "Which element is used in dentistry for fillings and crowns due to its biocompatibility and durability?",
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
            "This element is commonly used in the construction of buildings and bridges due to its strength and durability. What is it?",
            "This element is a key component in the production of steel, making it essential for construction and manufacturing industries. What is it?",
        ],
        "options_less": XAS_OPTIONS_LESS,
        "options_more": XAS_OPTIONS_MORE,
    },
    "mex": {
        "questions": [
            "This element is known for its excellent electrical conductivity and is commonly used in wiring. What is it?",
            "This reddish-brown metal has been used by humans for thousands of years to make coins, tools, and jewelry. What is it?",
            "Which element is an essential trace nutrient for human health, playing a role in red blood cell production and energy metabolism?",
            "This metal's ability to resist corrosion and its antimicrobial properties make it ideal for plumbing and medical equipment. What is it?",
            "Which element is a key component of bronze, an alloy traditionally used in sculptures and musical instruments?",
            "Known for its malleability and ductility, this metal is often used in electrical cables and electronics. What is it?",
            "This element is crucial in the process of creating brass, an alloy commonly used in musical instruments. Which element is it?",
            "This element is often used in architectural applications for roofing and cladding due to its weather-resistant properties. What is it?",
            "This element is a key component in the production of steel, making it essential for construction and manufacturing industries. What is it?",
        ],
        "options_less": MEX_OPTIONS_LESS,
        "options_more": MEX_OPTIONS_MORE,
    },
}
