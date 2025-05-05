"""
er.py
"""

"""
Entity-Relationship diagram generator for Mermaid.

This module provides functionality to generate ER diagrams
with entities, attributes, and relationships.
"""

from typing import Any, Dict, List, Optional, Union

from ..base import BaseDiagramGenerator
from ..constants import ER_CARDINALITIES
from ..utils import escape_text


class ERDiagramGenerator(BaseDiagramGenerator):
    """
    Generator for Mermaid Entity-Relationship diagrams.
    """

    def generate(
        self,
        entities: List[Dict],
        relationships: List[Dict],
        title: Optional[str] = None,
    ) -> str:
        """
        Generate a Mermaid ER diagram.

        Args:
            entities: List of entity dictionaries with 'name' and 'attributes' keys
            relationships: List of relationship dictionaries with 'entity1', 'entity2',
                          'relationship', and optional 'cardinality' keys
            title: Optional title for the diagram

        Returns:
            Mermaid ER diagram as a string
        """
        content_lines = []

        # Add entities with attributes
        for entity in entities:
            entity_lines = self._format_entity(entity)
            content_lines.extend([f"    {line}" for line in entity_lines])

        # Add relationships
        for relationship in relationships:
            rel_line = self._format_relationship(relationship)
            content_lines.append(f"    {rel_line}")

        # Format the diagram
        return self._format_diagram("erDiagram", content_lines, title)

    def _format_entity(self, entity: Dict) -> List[str]:
        """
        Format an entity for an ER diagram.

        Args:
            entity: Entity dictionary with 'name' and 'attributes' keys

        Returns:
            List of formatted entity lines
        """
        entity_lines = []
        entity_name = escape_text(entity["name"])

        # Start entity definition
        entity_lines.append(f"{entity_name} {{")

        # Add attributes
        for attr in entity.get("attributes", []):
            attr_line = self._format_attribute(attr)
            entity_lines.append(f"    {attr_line}")

        # Close entity definition
        entity_lines.append("}")

        return entity_lines

    def _format_attribute(self, attr: Dict) -> str:
        """
        Format an attribute for an ER diagram.

        Args:
            attr: Attribute dictionary with 'name' and optional 'type',
                'primary_key', and 'foreign_key' keys

        Returns:
            Formatted attribute line
        """
        name = escape_text(attr["name"])
        type_hint = attr.get("type", "string")
        pk = attr.get("primary_key", False)
        fk = attr.get("foreign_key", False)

        # Add appropriate markers for primary and foreign keys
        if pk:
            return f"{type_hint} {name} PK"
        elif fk:
            return f"{type_hint} {name} FK"
        else:
            return f"{type_hint} {name}"

    def _format_relationship(self, relationship: Dict) -> str:
        """
        Format a relationship for an ER diagram.

        Args:
            relationship: Relationship dictionary with 'entity1', 'entity2',
                         'relationship', and optional 'cardinality' keys

        Returns:
            Formatted relationship line
        """
        entity1 = escape_text(relationship["entity1"])
        entity2 = escape_text(relationship["entity2"])
        rel_label = escape_text(relationship["relationship"])

        # Validate and default the cardinality
        cardinality = relationship.get("cardinality", "1--1")
        if cardinality not in ER_CARDINALITIES:
            cardinality = "1--1"  # Default to one-to-one if invalid

        return f"{entity1} {cardinality} {entity2} : {rel_label}"


def generate_er_diagram(
    entities: List[Dict],
    relationships: List[Dict],
    title: Optional[str] = None,
    theme: str = "default",
) -> str:
    """
    Generate a Mermaid ER diagram.

    Args:
        entities: List of entity dictionaries with 'name' and 'attributes' keys
        relationships: List of relationship dictionaries with 'entity1', 'entity2',
                      'relationship', and optional 'cardinality' keys
        title: Optional title for the diagram
        theme: Theme for the diagram ('default', 'dark', 'forest', 'neutral')

    Returns:
        Mermaid ER diagram as a string
    """
    generator = ERDiagramGenerator(theme)
    return generator.generate(entities, relationships, title)
