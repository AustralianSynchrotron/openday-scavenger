from enum import Enum


# the value of the element symbol must match the symbol in the database
# as well as the symbol in the element_lookup.json
class Elements(Enum):
    C = "C"
    N = "N"
    Si = "Si"
    Ca = "Ca"
    Fe = "Fe"
    Ni = "Ni"
    Cu = "Cu"
    Au = "Au"


questions_answers = {
    Elements.C.value: [
        "This element is the primary building block of organic life and forms the backbone of most biological molecules. What is it?",
        "This element is known for its allotropes, including diamond and graphite. What is it?",
        "What element is commonly found in fossil fuels and is a major contributor to greenhouse gas emissions when burned?",
        "This element is essential for photosynthesis in plants, as they convert carbon dioxide into glucose. What is it?",
        "This element is a fundamental component of organic molecules and is vital for the structure of proteins and nucleic acids. What is it?",
        "This element is used to produce steel when combined with iron. What is it?",
        "What element forms the basis of many important compounds, including hydrocarbons and carbonates?",
        "This element is found in the atmosphere primarily in the form of carbon dioxide. What is it?",
    ],
    Elements.N.value: [
        "This element makes up about 78% of the Earth's atmosphere and is essential for plant growth. What is it?",
        "What element is a key component of amino acids and proteins, playing a crucial role in biological systems?",
        "This non-metal is often used in fertilisers to promote healthy plant growth. What is it?",
        "Which element exists as a colourless, odourless gas at room temperature and is often used in the production of ammonia?",
        "This element is found in explosives like TNT and is known for its role in the nitrogen cycle. What is it?",
        "What element is used in the production of nitric acid, a key reagent in various chemical reactions?",
        "This element is essential for the synthesis of DNA and RNA in living organisms. What is it?",
        "Which element, when combined with hydrogen, forms a gas that is used to create a very cold environment in laboratories?",
    ],
    Elements.Si.value: [
        "What element is widely used in the electronics industry for making semiconductors?",
        "This element is the second most abundant in the Earth's crust and is a key component of sand. What is it?",
        "Which element is commonly found in computer chips and solar panels, playing a crucial role in modern technology?",
        "What element is used to produce glass and ceramics, contributing to their durability and thermal resistance?",
        "This element is essential for the production of silicones, which are used in a variety of applications from sealants to lubricants. What is it?",
        "Which element is represented by the symbol 'Si' and is a major component of many minerals, including quartz?",
        "What element forms the basis for various alloy compositions to improve mechanical properties in materials?",
        "This element plays a significant role in plant growth, particularly in the strengthening of cell walls. What is it?",
    ],
    Elements.Ca.value: [
        "This element is vital for bone health and is commonly found in dairy products. What is it?",
        "What element is used in the production of cement and is a key component of limestone?",
        "This alkaline earth metal is crucial for muscle function and nerve transmission. What is it?",
        "Which element reacts with water to produce hydrogen gas and a hydroxide solution?",
        "This element plays a significant role in blood clotting and is essential for the normal functioning of cells. What is it?",
        "What element, when combined with carbon, forms calcium carbide, which is used to produce acetylene gas?",
        "This element is often found in supplements aimed at improving bone density. What is it?",
        "Which element is commonly used in fireworks to produce a bright orange flame?",
    ],
    Elements.Fe.value: [
        "This element is essential for the production of haemoglobin in the human body and is often associated with red blood cells. What is it?",
        'The symbol for this element comes from its Latin name, "ferrum". Which element is this?',
        "This element is found in Earth's core and contributes to the planet's magnetic field. What is it?",
        "In ancient times, this element was used to make weapons and tools, and it still forms the backbone of modern infrastructure. What is it?",
        "This element oxidises in air, forming a red-brown layer commonly known as rust. What is it?",
        "This transition metal is attracted to magnets and often used to create strong magnetic fields. What is it?",
        "This element is commonly used in the construction of buildings and bridges due to its strength and durability. What is it?",
    ],
    Elements.Ni.value: [
        "This element is commonly used in rechargeable batteries, especially in Nickel-Cadmium (NiCd) batteries. What is it?",
        "Which metal is known for its resistance to corrosion and is frequently used in the production of stainless steel alloys?",
        "This element has a silvery-white appearance and is widely used for electroplating to protect other metals from corrosion. What is it?",
        "What element, often found in coins, is known for being magnetic at room temperature?",
        "Which element is used in producing strong, heat-resistant superalloys for jet engines and turbines?",
        "This element is vital in the creation of guitar strings and has a role in musical instrument production. What is it?",
        "What element, combined with iron and other metals, is used to produce materials that are hard and can withstand extreme conditions?",
        "This metal is essential in the production of catalysts used in hydrogenation processes in the chemical industry. What is it?",
    ],
    Elements.Cu.value: [
        "This element is known for its excellent electrical conductivity and is commonly used in wiring. What is it?",
        "This reddish-brown metal has been used by humans for thousands of years to make coins, tools, and jewellery. What is it?",
        "Which element is an essential trace nutrient for human health, playing a role in red blood cell production and energy metabolism?",
        "This metal's ability to resist corrosion and its antimicrobial properties make it ideal for plumbing and medical equipment. What is it?",
        "Which element is a key component of bronze, an alloy traditionally used in sculptures and musical instruments?",
        "Known for its malleability and ductility, this metal is often used in electrical cables and electronics. What is it?",
        "This element is crucial in the process of creating brass, an alloy commonly used in musical instruments. Which element is it?",
    ],
    Elements.Au.value: [
        "This element's chemical symbol is derived from the Latin word 'Aurum.' What is it?",
        "Which precious metal is highly valued for its use in jewellery and electronics due to its conductivity and resistance to corrosion?",
        "This element is known for its distinctive bright yellow hue and is often associated with wealth and luxury. What is it?",
        "Which element is often used to back currencies and historically served as the basis for the gold standard?",
        "This metal is malleable enough to be hammered into thin sheets and used for gilding. What is the element?",
        "Which element is considered a noble metal and is frequently awarded in Olympic medals for first place?",
        "This element is widely found in nature but often mixed with other materials, requiring a refining process. What is the symbol of this element?",
    ],
}
