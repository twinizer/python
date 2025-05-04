"""
KiCad schematic parser module.

This module provides functionality to parse and analyze KiCad schematic (.sch, .kicad_sch) files.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any

from rich.console import Console
from rich.table import Table
from rich.tree import Tree

console = Console()


class KiCadSchematicParser:
    """
    Parser for KiCad schematic files.

    Supports both legacy .sch format and newer S-expression based .kicad_sch format.
    """

    def __init__(self, schematic_path: str):
        """
        Initialize the parser with a schematic file path.

        Args:
            schematic_path: Path to the KiCad schematic file
        """
        self.schematic_path = schematic_path
        self.components = []
        self.nets = []
        self.hierarchy = []
        self.is_new_format = schematic_path.endswith('.kicad_sch')

    def parse(self) -> Dict[str, Any]:
        """
        Parse the schematic file and extract components, nets, and hierarchy.

        Returns:
            Dictionary with parsed schematic data
        """
        if not os.path.exists(self.schematic_path):
            raise FileNotFoundError(f"Schematic file not found: {self.schematic_path}")

        if self.is_new_format:
            return self._parse_new_format()
        else:
            return self._parse_legacy_format()

    def _parse_new_format(self) -> Dict[str, Any]:
        """
        Parse the new S-expression based .kicad_sch format.

        Returns:
            Dictionary with parsed schematic data
        """
        with open(self.schematic_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # In a real implementation, we would use a proper S-expression parser
        # For simplicity, we'll use regex to extract components
        component_matches = re.finditer(
            r'\(symbol\s+\(lib_id\s+"([^"]+)"\)[^)]*\(at\s+([^\)]+)\)[^)]*\(property\s+"Reference"\s+"([^"]+)"[^)]*\(property\s+"Value"\s+"([^"]+)"',
            content)

        for match in component_matches:
            lib_id, position, reference, value = match.groups()
            x, y = map(float, position.split()[:2])

            component = {
                'reference': reference,
                'value': value,
                'lib_id': lib_id,
                'position': (x, y)
            }
            self.components.append(component)

        # Extract nets
        net_matches = re.finditer(r'\(net\s+\(code\s+(\d+)\)\s+\(name\s+"([^"]+)"\)\)', content)
        for match in net_matches:
            net_code, net_name = match.groups()
            self.nets.append({
                'code': int(net_code),
                'name': net_name
            })

        return {
            'components': self.components,
            'nets': self.nets,
            'hierarchy': self.hierarchy,
            'format': 'kicad_sch'
        }

    def _parse_legacy_format(self) -> Dict[str, Any]:
        """
        Parse the legacy .sch format.

        Returns:
            Dictionary with parsed schematic data
        """
        with open(self.schematic_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Look for component definitions
            if line.startswith('$Comp'):
                component = {}
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('$EndComp'):
                    comp_line = lines[i].strip()

                    if comp_line.startswith('L'):
                        # Library reference and component name
                        parts = comp_line.split()
                        if len(parts) >= 3:
                            component['lib_id'] = parts[1]
                            component['reference'] = parts[2]

                    elif comp_line.startswith('U'):
                        # Unit number and timestamp
                        pass

                    elif comp_line.startswith('P'):
                        # Position
                        parts = comp_line.split()
                        if len(parts) >= 3:
                            component['position'] = (float(parts[1]), float(parts[2]))

                    elif comp_line.startswith('F'):
                        # Field
                        parts = comp_line.split(None, 2)
                        if len(parts) >= 3:
                            field_num = int(parts[0][1:])
                            if field_num == 0:  # Reference
                                component['reference'] = parts[2].strip('"')
                            elif field_num == 1:  # Value
                                component['value'] = parts[2].strip('"')
                            elif field_num == 2:  # Footprint
                                component['footprint'] = parts[2].strip('"')

                    i += 1

                if 'reference' in component and 'position' in component:
                    self.components.append(component)

            # Look for nets
            elif line.startswith('Wire Wire Line'):
                # Legacy format doesn't have explicit net definitions,
                # but connections between components
                pass

            # Look for sheet definitions (hierarchy)
            elif line.startswith('$Sheet'):
                sheet = {}
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('$EndSheet'):
                    sheet_line = lines[i].strip()

                    if sheet_line.startswith('S'):
                        # Sheet position and size
                        parts = sheet_line.split()
                        if len(parts) >= 5:
                            sheet['position'] = (float(parts[1]), float(parts[2]))
                            sheet['size'] = (float(parts[3]), float(parts[4]))

                    elif sheet_line.startswith('F0'):
                        # Sheet name
                        parts = sheet_line.split(None, 1)
                        if len(parts) >= 2:
                            sheet['name'] = parts[1].strip('"')

                    elif sheet_line.startswith('F1'):
                        # Sheet filename
                        parts = sheet_line.split(None, 1)
                        if len(parts) >= 2:
                            sheet['file'] = parts[1].strip('"')

                    i += 1

                if 'name' in sheet and 'file' in sheet:
                    self.hierarchy.append(sheet)

            i += 1

        return {
            'components': self.components,
            'nets': self.nets,
            'hierarchy': self.hierarchy,
            'format': 'legacy_sch'
        }

    def generate_component_list(self) -> Table:
        """
        Generate a table of components in the schematic.

        Returns:
            Rich Table object with component information
        """
        if not self.components:
            self.parse()

        table = Table("Reference", "Value", "Library", "Position")

        for component in sorted(self.components, key=lambda c: c.get('reference', '')):
            ref = component.get('reference', 'Unknown')
            value = component.get('value', 'Unknown')
            lib_id = component.get('lib_id', 'Unknown')
            position = component.get('position', (0, 0))

            table.add_row(
                ref,
                value,
                lib_id,
                f"({position[0]}, {position[1]})"
            )

        return table

    def generate_hierarchy_tree(self) -> Tree:
        """
        Generate a tree representation of the schematic hierarchy.

        Returns:
            Rich Tree object with hierarchy information
        """
        if not self.hierarchy and os.path.exists(self.schematic_path):
            self.parse()

        tree = Tree(os.path.basename(self.schematic_path))

        for sheet in self.hierarchy:
            name = sheet.get('name', 'Unknown')
            file = sheet.get('file', 'Unknown')

            sheet_node = tree.add(f"[blue]{name}[/blue] ({file})")

            # In a real implementation, we would recurse into sub-sheets
            # by parsing their files as well

        return tree

    def get_component_types(self) -> Dict[str, int]:
        """
        Get a count of component types in the schematic.

        Returns:
            Dictionary mapping component values to counts
        """
        if not self.components:
            self.parse()

        component_types = {}
        for component in self.components:
            value = component.get('value', 'Unknown')
            component_types[value] = component_types.get(value, 0) + 1

        return component_types

    def get_net_count(self) -> int:
        """
        Get the number of nets in the schematic.

        Returns:
            Number of nets
        """
        if not self.nets:
            self.parse()

        return len(self.nets)


# Create an alias for backward compatibility
SchematicParser = KiCadSchematicParser


def analyze_kicad_schematic(schematic_path: str) -> Dict[str, Any]:
    """
    Analyze a KiCad schematic file.

    Args:
        schematic_path: Path to the KiCad schematic file

    Returns:
        Dictionary with schematic analysis results
    """
    parser = KiCadSchematicParser(schematic_path)
    schematic_data = parser.parse()

    console.print(f"[green]Analyzing schematic:[/green] {schematic_path}")

    # Generate component table
    component_table = parser.generate_component_list()

    # Generate hierarchy tree
    hierarchy_tree = parser.generate_hierarchy_tree()

    # Count components by type
    component_types = parser.get_component_types()

    # Display component types
    console.print("\n[bold]Component Types:[/bold]")
    type_table = Table("Type", "Count")
    for value, count in sorted(component_types.items(), key=lambda x: x[1], reverse=True):
        type_table.add_row(value, str(count))
    console.print(type_table)

    # Display hierarchy
    if parser.hierarchy:
        console.print("\n[bold]Schematic Hierarchy:[/bold]")
        console.print(hierarchy_tree)

    # Display summary
    console.print(
        f"\n[bold]Summary:[/bold] {len(parser.components)} components, {len(parser.nets)} nets, {len(parser.hierarchy)} sheets")

    return {
        'schematic_data': schematic_data,
        'component_table': component_table,
        'hierarchy_tree': hierarchy_tree,
        'component_types': component_types,
        'total_components': len(schematic_data['components']),
        'total_nets': len(schematic_data['nets'])
    }