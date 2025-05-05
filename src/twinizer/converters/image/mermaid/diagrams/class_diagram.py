"""
class_diagram.py
"""

"""
Class diagram generator for Mermaid.

This module provides functionality to generate class diagrams
with classes, attributes, methods, and relationships.
"""

import re
from typing import Any, Dict, List, Optional, Union

from ..base import BaseDiagramGenerator
from ..utils import escape_text


class ClassDiagramGenerator(BaseDiagramGenerator):
    """
    Generator for Mermaid class diagrams.
    """

    # Relationship symbols
    RELATIONSHIP_TYPES = {
        "inheritance": "<|--",
        "composition": "*--",
        "aggregation": "o--",
        "association": "-->",
        "dependency": "..>",
        "realization": "<|..",
        "link": "--",
    }

    def generate(
        self,
        classes: List[Dict],
        title: Optional[str] = None,
        namespace: Optional[str] = None,
    ) -> str:
        """
        Generate a Mermaid class diagram.

        Args:
            classes: List of class dictionaries with 'name', 'attributes', 'methods',
                    and optional 'relationships' keys
            title: Optional title for the diagram
            namespace: Optional namespace for the diagram

        Returns:
            Mermaid class diagram as a string
        """
        content_lines = []

        # Set indentation based on namespace
        if namespace:
            content_lines.append(f"    namespace {namespace} {{")
            base_indent = "    "
        else:
            base_indent = ""

        # Add classes with attributes and methods
        for cls in classes:
            class_lines = self._format_class(cls, base_indent)
            content_lines.extend(class_lines)

        # Add relationships
        for cls in classes:
            class_name = cls["name"]
            for rel in cls.get("relationships", []):
                rel_line = self._format_relationship(class_name, rel, base_indent)
                content_lines.append(rel_line)

        # Close namespace if provided
        if namespace:
            content_lines.append("    }")

        # Format the diagram
        return self._format_diagram("classDiagram", content_lines, title)

    def _format_class(self, cls: Dict, base_indent: str = "") -> List[str]:
        """
        Format a class for a class diagram.

        Args:
            cls: Class dictionary with 'name', 'attributes', and 'methods' keys
            base_indent: Base indentation for the class

        Returns:
            List of formatted class lines
        """
        class_lines = []
        class_name = escape_text(cls["name"])

        # Add class definition
        if "annotation" in cls:
            class_lines.append(
                f"{base_indent}    class {class_name} {cls['annotation']}"
            )
        else:
            class_lines.append(f"{base_indent}    class {class_name}")

        # Start class body
        class_lines.append(f"{base_indent}    {class_name} {{")

        # Add attributes
        for attr in cls.get("attributes", []):
            attr_line = self._format_attribute(attr)
            class_lines.append(f"{base_indent}        {attr_line}")

        # Add methods
        for method in cls.get("methods", []):
            method_line = self._format_method(method)
            class_lines.append(f"{base_indent}        {method_line}")

        # Close class body
        class_lines.append(f"{base_indent}    }}")

        return class_lines

    def _format_attribute(self, attr: Dict) -> str:
        """
        Format an attribute for a class diagram.

        Args:
            attr: Attribute dictionary with 'name' and optional 'type' and 'visibility' keys

        Returns:
            Formatted attribute line
        """
        visibility = attr.get("visibility", "+")
        name = escape_text(attr["name"])
        type_hint = attr.get("type", "")

        if type_hint:
            return f"{visibility}{name}: {type_hint}"
        else:
            return f"{visibility}{name}"

    def _format_method(self, method: Dict) -> str:
        """
        Format a method for a class diagram.

        Args:
            method: Method dictionary with 'name' and optional 'params', 'return', and 'visibility' keys

        Returns:
            Formatted method line
        """
        visibility = method.get("visibility", "+")
        name = escape_text(method["name"])
        params = method.get("params", "")
        return_type = method.get("return", "")

        if return_type:
            return f"{visibility}{name}({params}): {return_type}"
        else:
            return f"{visibility}{name}({params})"

    def _format_relationship(
        self, class_name: str, rel: Dict, base_indent: str = ""
    ) -> str:
        """
        Format a relationship for a class diagram.

        Args:
            class_name: Name of the source class
            rel: Relationship dictionary with 'type', 'target', and optional 'label' keys
            base_indent: Base indentation for the relationship

        Returns:
            Formatted relationship line
        """
        rel_type = rel["type"]
        target = escape_text(rel["target"])
        label = escape_text(rel.get("label", ""))

        # Get relationship symbol
        rel_symbol = self.RELATIONSHIP_TYPES.get(rel_type, "--")

        # Determine relationship direction
        if rel_type in ["inheritance", "realization"]:
            relationship = f"{base_indent}    {target} {rel_symbol} {class_name}"
        elif rel_type in ["composition", "aggregation"]:
            relationship = f"{base_indent}    {target} {rel_symbol} {class_name}"
        else:
            relationship = f"{base_indent}    {class_name} {rel_symbol} {target}"

        # Add label if provided
        if label:
            relationship += f" : {label}"

        return relationship


def generate_class_diagram(
    classes: List[Dict],
    title: Optional[str] = None,
    namespace: Optional[str] = None,
    theme: str = "default",
) -> str:
    """
    Generate a Mermaid class diagram.

    Args:
        classes: List of class dictionaries with 'name', 'attributes', 'methods',
                and optional 'relationships' keys
        title: Optional title for the diagram
        namespace: Optional namespace for the diagram
        theme: Theme for the diagram ('default', 'dark', 'forest', 'neutral')

    Returns:
        Mermaid class diagram as a string
    """
    generator = ClassDiagramGenerator(theme)
    return generator.generate(classes, title, namespace)
