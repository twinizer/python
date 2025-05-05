"""
flowchart.py
"""

"""
Flowchart diagram generator for Mermaid.

This module provides functionality to generate flowchart diagrams
with nodes, edges, and styling options.
"""

import re
from typing import Any, Dict, List, Optional, Union

from ..base import BaseDiagramGenerator
from ..constants import EDGE_STYLES, NODE_SHAPES
from ..utils import escape_text, format_style_string, sanitize_id


class FlowchartGenerator(BaseDiagramGenerator):
    """
    Generator for Mermaid flowchart diagrams.
    """

    def generate(
        self,
        nodes: List[Dict],
        edges: List[Dict],
        direction: str = "TD",
        title: Optional[str] = None,
        styles: Optional[List[Dict]] = None,
    ) -> str:
        """
        Generate a Mermaid flowchart diagram.

        Args:
            nodes: List of node dictionaries with 'id' and 'label' keys
            edges: List of edge dictionaries with 'from', 'to', and optional 'label' keys
            direction: Direction of the flowchart (TD, LR, RL, BT)
            title: Optional title for the diagram
            styles: Optional list of style dictionaries

        Returns:
            Mermaid flowchart as a string
        """
        # Validate direction
        valid_directions = ["TB", "TD", "BT", "RL", "LR"]
        if direction not in valid_directions:
            raise ValueError(
                f"Invalid direction: {direction}. Valid directions: {', '.join(valid_directions)}"
            )

        # Initialize content lines
        content_lines = []

        # Add nodes
        for node in nodes:
            node_line = self._format_node(node)
            content_lines.append(f"    {node_line}")

            # Add click handler if specified
            if "link" in node:
                node_id = sanitize_id(node["id"])
                content_lines.append(f"    click {node_id} href \"{node['link']}\"")

        # Add edges
        for edge in edges:
            edge_line = self._format_edge(edge)
            content_lines.append(f"    {edge_line}")

        # Add styles if provided
        if styles:
            for style in styles:
                style_line = self._format_style(style)
                if style_line:
                    content_lines.append(f"    {style_line}")

        # Format the diagram with the appropriate direction
        return self._format_diagram(f"flowchart {direction}", content_lines, title)

    def _format_node(self, node: Dict) -> str:
        """
        Format a node for a flowchart diagram.

        Args:
            node: Node dictionary with 'id' and 'label' keys

        Returns:
            Formatted node line
        """
        node_id = sanitize_id(node["id"])
        node_label = escape_text(node.get("label", node_id))
        shape = node.get("shape", "rounded")

        # Get shape decorators
        shape_info = NODE_SHAPES.get(shape, NODE_SHAPES["rounded"])
        prefix, suffix = shape_info["prefix"], shape_info["suffix"]

        # Return formatted node line
        return f"{node_id}{prefix}{node_label}{suffix}"

    def _format_edge(self, edge: Dict) -> str:
        """
        Format an edge for a flowchart diagram.

        Args:
            edge: Edge dictionary with 'from', 'to', and optional 'label' keys

        Returns:
            Formatted edge line
        """
        from_id = sanitize_id(edge["from"])
        to_id = sanitize_id(edge["to"])
        label = escape_text(edge.get("label", ""))
        style_name = edge.get("style", "solid")

        # Get edge style
        edge_style = EDGE_STYLES.get(style_name, EDGE_STYLES["solid"])

        # Format edge with optional label
        if label:
            return f"{from_id} {edge_style}|{label}| {to_id}"
        else:
            return f"{from_id} {edge_style} {to_id}"

    def _format_style(self, style: Dict) -> str:
        """
        Format a style for a flowchart diagram.

        Args:
            style: Style dictionary with 'target', 'style', and optional 'applies_to' keys

        Returns:
            Formatted style line(s)
        """
        if "target" not in style or "style" not in style:
            return ""

        target = style["target"]

        # Handle style string or dictionary
        if isinstance(style["style"], dict):
            css = format_style_string(style["style"])
        else:
            css = style["style"]

        # Create class definition
        class_def = f"classDef {target} {css}"

        # Apply style to targets if specified
        if "applies_to" in style and style["applies_to"]:
            targets = ",".join([sanitize_id(t) for t in style["applies_to"]])
            return f"{class_def}\nclass {targets} {target}"

        return class_def


def generate_flowchart(
    nodes: List[Dict],
    edges: List[Dict],
    direction: str = "TD",
    title: Optional[str] = None,
    styles: Optional[List[Dict]] = None,
    theme: str = "default",
) -> str:
    """
    Generate a Mermaid flowchart diagram.

    Args:
        nodes: List of node dictionaries with 'id' and 'label' keys
        edges: List of edge dictionaries with 'from', 'to', and optional 'label' keys
        direction: Direction of the flowchart (TD, LR, RL, BT)
        title: Optional title for the diagram
        styles: Optional list of style dictionaries
        theme: Theme for the diagram ('default', 'dark', 'forest', 'neutral')

    Returns:
        Mermaid flowchart as a string
    """
    generator = FlowchartGenerator(theme)
    return generator.generate(nodes, edges, direction, title, styles)
