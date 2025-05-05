"""
utils.py
"""

"""
Utility functions for Mermaid diagram generation.

This module provides utility functions for Mermaid diagram generation,
such as ID sanitization and string formatting.
"""

import re
from typing import Any, Dict, List, Optional, Union


def sanitize_id(id_str: str) -> str:
    """
    Sanitize an ID for use in Mermaid diagrams.

    Args:
        id_str: ID string to sanitize

    Returns:
        Sanitized ID string
    """
    # Replace spaces and special characters with underscores
    sanitized = re.sub(r"[^a-zA-Z0-9]", "_", str(id_str))

    # Ensure the ID starts with a letter
    if sanitized and not sanitized[0].isalpha():
        sanitized = "id_" + sanitized

    return sanitized


def format_style_string(styles: Dict[str, str]) -> str:
    """
    Format a dictionary of styles into a Mermaid style string.

    Args:
        styles: Dictionary of style properties and values

    Returns:
        Formatted style string
    """
    style_parts = []
    for prop, value in styles.items():
        # Convert camelCase to kebab-case for CSS properties
        prop = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", prop).lower()
        style_parts.append(f"{prop}:{value}")

    return ",".join(style_parts)


def escape_text(text: str) -> str:
    """
    Escape special characters in text for Mermaid diagrams.

    Args:
        text: Text to escape

    Returns:
        Escaped text
    """
    # Replace characters that might interfere with Mermaid syntax
    replacements = {
        ":": "&#58;",
        ";": "&#59;",
        "#": "&#35;",
        "{": "&#123;",
        "}": "&#125;",
        "(": "&#40;",
        ")": "&#41;",
        "|": "&#124;",
    }

    for char, code in replacements.items():
        text = text.replace(char, code)

    return text


def add_theme_directive(theme: str) -> str:
    """
    Generate a theme initialization directive for Mermaid diagrams.

    Args:
        theme: Theme name

    Returns:
        Theme initialization directive or empty string for default theme
    """
    if theme != "default":
        return f"%%{{ init: {{'theme': '{theme}'}} }}%%"
    return ""


def indent_lines(text: str, indent: int = 4) -> str:
    """
    Indent each line of text with a specified number of spaces.

    Args:
        text: Text to indent
        indent: Number of spaces to indent

    Returns:
        Indented text
    """
    indent_str = " " * indent
    return indent_str + text.replace("\n", f"\n{indent_str}")
