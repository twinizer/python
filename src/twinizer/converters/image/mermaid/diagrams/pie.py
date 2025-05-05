"""
pie.py
"""

"""
Pie chart generator for Mermaid.

This module provides functionality to generate pie charts
with data points and optional styling.
"""

from typing import Any, Dict, List, Optional, Union

from ..base import BaseDiagramGenerator
from ..constants import COLOR_SCHEMES
from ..utils import escape_text


class PieChartGenerator(BaseDiagramGenerator):
    """
    Generator for Mermaid pie charts.
    """

    def generate(
        self,
        data: List[Dict],
        title: Optional[str] = None,
        show_percentages: bool = True,
        color_scheme: str = "default",
    ) -> str:
        """
        Generate a Mermaid pie chart.

        Args:
            data: List of data dictionaries with 'label' and 'value' keys
            title: Optional title for the chart
            show_percentages: Whether to show percentages in the chart
            color_scheme: Color scheme to use

        Returns:
            Mermaid pie chart as a string
        """
        content_lines = []

        # Add show percentages option if set to false (true is default)
        if not show_percentages:
            content_lines.append("    showData")

        # Add color scheme if not default
        if color_scheme != "default" and color_scheme in COLOR_SCHEMES:
            colors = COLOR_SCHEMES[color_scheme]
            if colors:
                color_str = ", ".join([f'"{color}"' for color in colors])
                content_lines.append(f"    colorset [{color_str}]")

        # Add data entries
        for item in data:
            data_line = self._format_data_item(item)
            content_lines.append(f"    {data_line}")

        # Format the diagram
        return self._format_diagram("pie", content_lines, title)

    def _format_data_item(self, item: Dict) -> str:
        """
        Format a data item for a pie chart.

        Args:
            item: Data item dictionary with 'label' and 'value' keys

        Returns:
            Formatted data line
        """
        label = escape_text(item["label"])
        value = item["value"]

        return f'"{label}" : {value}'


def generate_pie_chart(
    data: List[Dict],
    title: Optional[str] = None,
    show_percentages: bool = True,
    color_scheme: str = "default",
    theme: str = "default",
) -> str:
    """
    Generate a Mermaid pie chart.

    Args:
        data: List of data dictionaries with 'label' and 'value' keys
        title: Optional title for the chart
        show_percentages: Whether to show percentages in the chart
        color_scheme: Color scheme to use
        theme: Theme for the diagram ('default', 'dark', 'forest', 'neutral')

    Returns:
        Mermaid pie chart as a string
    """
    generator = PieChartGenerator(theme)
    return generator.generate(data, title, show_percentages, color_scheme)
