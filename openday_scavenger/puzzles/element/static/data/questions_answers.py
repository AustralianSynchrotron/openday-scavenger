from enum import Enum


# the value of the element symbol must match the symbol in the database
# as well as the symbol in the element_lookup.json
class Elements(Enum):
    Au = "Au"
    Fe = "Fe"
    Cu = "Cu"


questions_answers = {
    Elements.Au.value: [
        "This element's chemical symbol is derived from the Latin word 'Aurum.' What is it?",
        "Which precious metal is highly valued for its use in jewelry and electronics due to its conductivity and resistance to corrosion?",
        "This element has an atomic number of 79 and is known for its bright yellow color. What is it?",
        "Which element is often used to back currencies and historically served as the basis for the gold standard?",
        "This metal is malleable enough to be hammered into thin sheets and used for gilding. What is the element?",
        "Which element is considered a noble metal and is frequently awarded in Olympic medals for first place?",
        "This element is widely found in nature but often mixed with other materials, requiring a refining process. What is the symbol of this element?",
    ],
    Elements.Fe.value: [
        "This element is essential for the production of hemoglobin in the human body and is often associated with red blood cells. What is it?",
        'The symbol for this element comes from its Latin name, "ferrum". Which element is this?',
        "This element is found in Earth's core and contributes to the planet's magnetic field. What is it?",
        "In ancient times, this element was used to make weapons and tools, and it still forms the backbone of modern infrastructure. What is it?",
        "This element oxidizes in air, forming a red-brown layer commonly known as rust. What is it?",
        "This transition metal is attracted to magnets and often used to create strong magnetic fields. What is it?",
        "This element is commonly used in the construction of buildings and bridges due to its strength and durability. What is it?",
    ],
    Elements.Cu.value: [
        "This element is known for its excellent electrical conductivity and is commonly used in wiring. What is it?",
        "This reddish-brown metal has been used by humans for thousands of years to make coins, tools, and jewelry. What is it?",
        "Which element is an essential trace nutrient for human health, playing a role in red blood cell production and energy metabolism?",
        "This metal's ability to resist corrosion and its antimicrobial properties make it ideal for plumbing and medical equipment. What is it?",
        "Which element is a key component of bronze, an alloy traditionally used in sculptures and musical instruments?",
        "Known for its malleability and ductility, this metal is often used in electrical cables and electronics. What is it?",
        "This element is crucial in the process of creating brass, an alloy commonly used in musical instruments. Which element is it?",
    ],
}
