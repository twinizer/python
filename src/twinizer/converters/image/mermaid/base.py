"""
base.py
"""

"""
Base generator class for Mermaid diagrams.

This module provides the base generator class for Mermaid diagrams
with common functionality shared across different diagram types.
"""

from typing import Any, Dict, List, Optional, Union

from .constants import THEMES
from .utils import add_theme_directive


class BaseDiagramGenerator:
    """
    Base class for all Mermaid diagram generators.

    This class provides common functionality shared across different diagram types,
    such as theme management and basic diagram structure.
    """

    def __init__(self, theme: str = "default"):
        """
        Initialize the base diagram generator.

        Args:
            theme: Theme name for the diagrams ('default', 'dark', 'forest', 'neutral', etc.)
        """
        if theme not in THEMES:
            raise ValueError(
                f"Unsupported theme: {theme}. Available themes: {', '.join(THEMES)}"
            )

        self.theme = theme

    def _get_theme_directive(self) -> str:
        """
        Get the theme initialization directive.

        Returns:
            Theme initialization directive
        """
        return add_theme_directive(self.theme)

    def _add_title(
        self, mermaid_lines: List[str], title: Optional[str] = None, indent: int = 4
    ) -> None:
        """
        Add a title to the diagram if provided.

        Args:
            mermaid_lines: List of Mermaid syntax lines
            title: Optional title for the diagram
            indent: Number of spaces to indent
        """
        if title:
            mermaid_lines.append(f"{' ' * indent}title {title}")

    def _format_diagram(
        self,
        diagram_type: str,
        content_lines: List[str],
        title: Optional[str] = None,
        additional_directives: Optional[List[str]] = None,
    ) -> str:
        """
        Format a complete diagram with theme, type, and content.

        Args:
            diagram_type: Type of diagram (flowchart, classDiagram, etc.)
            content_lines: Lines of diagram content
            title: Optional title for the diagram
            additional_directives: Optional additional directives to include

        Returns:
            Complete Mermaid diagram as a string
        """
        mermaid_lines = []

        # Add theme directive if not default
        theme_directive = self._get_theme_directive()
        if theme_directive:
            mermaid_lines.append(theme_directive)

        # Add diagram type directive
        mermaid_lines.append(diagram_type)

        # Add title if provided
        self._add_title(mermaid_lines, title)

        # Add additional directives if provided
        if additional_directives:
            mermaid_lines.extend(additional_directives)

        # Add content
        mermaid_lines.extend(content_lines)

        return "\n".join(mermaid_lines)

    def validate_data(self, data: Dict[str, Any], required_fields: List[str]) -> None:
        """
        Validate that the data contains all required fields.

        Args:
            data: Data to validate
            required_fields: List of required field names

        Raises:
            ValueError: If a required field is missing
        """
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
