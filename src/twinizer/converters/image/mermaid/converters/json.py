"""
json.py
"""

"""
JSON converter for Mermaid diagrams.

This module provides functionality to convert JSON data to Mermaid diagrams.
"""

import json
from typing import Any, Dict, List, Optional, Union

from ..diagrams.class_diagram import generate_class_diagram
from ..diagrams.er import generate_er_diagram
from ..diagrams.flowchart import generate_flowchart
from ..diagrams.gantt import generate_gantt_chart
from ..diagrams.journey import generate_journey_diagram
from ..diagrams.pie import generate_pie_chart
from ..diagrams.sequence import generate_sequence_diagram
from ..diagrams.state import generate_state_diagram


def from_json(
    json_data: Union[str, Dict], diagram_type: str = "auto", theme: str = "default"
) -> str:
    """
    Generate a Mermaid diagram from JSON data.

    Args:
        json_data: JSON string or dictionary containing diagram data
        diagram_type: Type of diagram to generate ('auto', 'flowchart', 'class', 'sequence',
                     'er', 'gantt', 'pie', 'state', 'journey')
        theme: Theme for the diagram ('default', 'dark', 'forest', 'neutral')

    Returns:
        Mermaid diagram as a string
    """
    # Parse JSON if string
    if isinstance(json_data, str):
        try:
            data = json.loads(json_data)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON string")
    else:
        data = json_data

    # Auto-detect diagram type if set to 'auto'
    if diagram_type == "auto":
        diagram_type = _detect_diagram_type(data)

    # Generate diagram based on type
    return _generate_diagram(data, diagram_type, theme)


def _detect_diagram_type(data: Dict) -> str:
    """
    Auto-detect the diagram type from JSON structure.

    Args:
        data: Dictionary containing diagram data

    Returns:
        Detected diagram type

    Raises:
        ValueError: If diagram type cannot be detected
    """
    if "nodes" in data and "edges" in data:
        return "flowchart"
    elif "classes" in data:
        return "class"
    elif "actors" in data and "messages" in data:
        return "sequence"
    elif "entities" in data and "relationships" in data:
        return "er"
    elif "sections" in data and any(
        "tasks" in section for section in data.get("sections", [])
    ):
        return "gantt"
    elif (
        "data" in data
        and isinstance(data["data"], list)
        and all("label" in item and "value" in item for item in data["data"])
    ):
        return "pie"
    elif "states" in data and "transitions" in data:
        return "state"
    elif "journeys" in data:
        return "journey"
    else:
        raise ValueError("Could not auto-detect diagram type from JSON structure")


def _generate_diagram(data: Dict, diagram_type: str, theme: str) -> str:
    """
    Generate a specific diagram type from data.

    Args:
        data: Dictionary containing diagram data
        diagram_type: Type of diagram to generate
        theme: Theme for the diagram

    Returns:
        Mermaid diagram as a string

    Raises:
        ValueError: If diagram type is not supported
    """
    # Validate required fields for the diagram type
    _validate_diagram_data(data, diagram_type)

    # Generate diagram based on type
    if diagram_type == "flowchart":
        return generate_flowchart(
            nodes=data["nodes"],
            edges=data["edges"],
            direction=data.get("direction", "TD"),
            title=data.get("title"),
            styles=data.get("styles"),
            theme=theme,
        )
    elif diagram_type == "class":
        return generate_class_diagram(
            classes=data["classes"],
            title=data.get("title"),
            namespace=data.get("namespace"),
            theme=theme,
        )
    elif diagram_type == "sequence":
        return generate_sequence_diagram(
            actors=data["actors"],
            messages=data["messages"],
            title=data.get("title"),
            autonumber=data.get("autonumber", False),
            theme=theme,
        )
    elif diagram_type == "er":
        return generate_er_diagram(
            entities=data["entities"],
            relationships=data["relationships"],
            title=data.get("title"),
            theme=theme,
        )
    elif diagram_type == "gantt":
        return generate_gantt_chart(
            sections=data["sections"],
            title=data.get("title"),
            date_format=data.get("date_format", "YYYY-MM-DD"),
            excludes=data.get("excludes"),
            includes=data.get("includes"),
            theme=theme,
        )
    elif diagram_type == "pie":
        return generate_pie_chart(
            data=data["data"],
            title=data.get("title"),
            show_percentages=data.get("show_percentages", True),
            color_scheme=data.get("color_scheme", "default"),
            theme=theme,
        )
    elif diagram_type == "state":
        return generate_state_diagram(
            states=data["states"],
            transitions=data["transitions"],
            title=data.get("title"),
            direction=data.get("direction", "LR"),
            start_state=data.get("start_state"),
            end_states=data.get("end_states"),
            theme=theme,
        )
    elif diagram_type == "journey":
        return generate_journey_diagram(
            journeys=data["journeys"], title=data.get("title"), theme=theme
        )
    else:
        raise ValueError(f"Unsupported diagram type: {diagram_type}")


def _validate_diagram_data(data: Dict, diagram_type: str) -> None:
    """
    Validate that the data contains all required fields for the specified diagram type.

    Args:
        data: Dictionary containing diagram data
        diagram_type: Type of diagram to validate

    Raises:
        ValueError: If required fields are missing
    """
    required_fields = {
        "flowchart": ["nodes", "edges"],
        "class": ["classes"],
        "sequence": ["actors", "messages"],
        "er": ["entities", "relationships"],
        "gantt": ["sections"],
        "pie": ["data"],
        "state": ["states", "transitions"],
        "journey": ["journeys"],
    }

    if diagram_type not in required_fields:
        raise ValueError(f"Unsupported diagram type: {diagram_type}")

    for field in required_fields[diagram_type]:
        if field not in data:
            raise ValueError(f"Missing required field for {diagram_type}: {field}")


def to_json(mermaid_code: str) -> Dict:
    """
    Convert a Mermaid diagram to JSON data (reverse operation).

    Note: This is a partial implementation and may not work for all diagram types.

    Args:
        mermaid_code: Mermaid diagram code

    Returns:
        JSON-compatible dictionary representation of the diagram
    """
    # This is a placeholder for future implementation
    # Parsing Mermaid syntax to JSON is complex and not fully implemented
    raise NotImplementedError("Converting Mermaid to JSON is not yet implemented")
