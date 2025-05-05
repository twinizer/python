"""
constants.py
"""

"""
Constants for Mermaid diagram generation.

This module contains the constant definitions for node shapes, edge styles,
arrow types, and color schemes used in various Mermaid diagrams.
"""

# Flowchart node shapes with their prefix and suffix for syntax
NODE_SHAPES = {
    "rounded": {"prefix": "[", "suffix": "]"},
    "box": {"prefix": "[", "suffix": "]"},
    "circle": {"prefix": "((", "suffix": "))"},
    "diamond": {"prefix": "{", "suffix": "}"},
    "hexagon": {"prefix": "{{", "suffix": "}}"},
    "stadium": {"prefix": "([", "suffix": "])"},
    "subroutine": {"prefix": "[[", "suffix": "]]"},
    "cylinder": {"prefix": "[(", "suffix": ")]"},
    "database": {"prefix": "[", "suffix": "]"},  # Styled with class
    "asymmetric": {"prefix": ">", "suffix": "]"},
    "rhombus": {"prefix": "{", "suffix": "}"},  # Styled with class
    "trapezoid": {"prefix": "[", "suffix": "]"},  # Styled with class
}

# Flowchart edge styles
EDGE_STYLES = {
    "solid": "-->",
    "dotted": "-.->",
    "thick": "==>",
    "invisible": "~~~",
    "chain": "-.->",
}

# Sequence diagram arrow styles
SEQUENCE_ARROWS = {
    "solid": "->",
    "dotted": "-->",
    "async": "->>",
    "open": "->",  # Styled with class
    "thick": "->",  # Styled with class
    "crossed": "->",  # Styled with class
    "x": "-x",
    "activate": "+->",
    "deactivate": "-+>",
}

# Chart color schemes
COLOR_SCHEMES = {
    "default": None,
    "pastel": [
        "#ffadad",
        "#ffd6a5",
        "#fdffb6",
        "#caffbf",
        "#9bf6ff",
        "#a0c4ff",
        "#bdb2ff",
        "#ffc6ff",
    ],
    "cool": ["#05445E", "#189AB4", "#75E6DA", "#D4F1F4"],
    "warm": ["#540804", "#8b0000", "#a52a2a", "#cd5c5c", "#fd7272"],
    "gradient": ["#00FEEF", "#07BFDF", "#0E80CF", "#1540BF", "#13107A"],
    "category10": [
        "#1f77b4",
        "#ff7f0e",
        "#2ca02c",
        "#d62728",
        "#9467bd",
        "#8c564b",
        "#e377c2",
        "#7f7f7f",
        "#bcbd22",
        "#17becf",
    ],
}

# Mermaid themes
THEMES = ["default", "dark", "forest", "neutral", "base", "night"]

# ER diagram relationship cardinalities
ER_CARDINALITIES = [
    "1--1",  # One to one
    "1--*",  # One to many
    "1--0",  # One to zero
    "*--1",  # Many to one
    "*--*",  # Many to many
    "*--0",  # Many to zero
    "0--1",  # Zero to one
    "0--*",  # Zero to many
    "0--0",  # Zero to zero
]

# State diagram styles
STATE_STYLES = {
    "normal": "",
    "choice": "<<choice>>",
    "fork": "<<fork>>",
    "join": "<<join>>",
    "start": "[*]",
    "end": "[*]",
}
