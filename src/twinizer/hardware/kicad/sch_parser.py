"""
KiCad schematic parser module.

This module provides functionality to parse and analyze KiCad schematic (.sch, .kicad_sch) files.
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from rich.console import Console
from rich.table import Table
from rich.tree import Tree

console = Console()


class KiCadSchematicParser:
    """
    Parser for KiCad schematic files.

    Supports both legacy .sch format and newer S-expression based .kicad_sch format.
    """

    def __init__(self, schematic_path: str, load_dependencies: bool = True):
        """
        Initialize the parser with a schematic file path.

        Args:
            schematic_path: Path to the KiCad schematic file
            load_dependencies: Whether to automatically load dependencies (libraries, hierarchical sheets)
        """
        self.schematic_path = schematic_path
        self.schematic_dir = os.path.dirname(os.path.abspath(schematic_path))
        self.components = []
        self.nets = []
        self.hierarchy = []
        self.libraries = {}
        self.loaded_files = (
            set()
        )  # Keep track of loaded files to avoid circular dependencies
        self.is_new_format = schematic_path.endswith(".kicad_sch")
        self.load_dependencies = load_dependencies

    def _find_library_files(self) -> List[str]:
        """
        Find library files in the schematic directory and parent directories.

        Returns:
            List of paths to library files
        """
        library_files = []

        # Check for cache library in the same directory
        base_name = os.path.splitext(os.path.basename(self.schematic_path))[0]
        cache_lib = os.path.join(self.schematic_dir, f"{base_name}-cache.lib")
        if os.path.exists(cache_lib):
            library_files.append(cache_lib)

        # Check for rescue library
        rescue_lib = os.path.join(self.schematic_dir, f"{base_name}-rescue.lib")
        if os.path.exists(rescue_lib):
            library_files.append(rescue_lib)

        # Check for project library
        project_lib = os.path.join(self.schematic_dir, f"{base_name}.lib")
        if os.path.exists(project_lib):
            library_files.append(project_lib)

        # Check for sym-lib-table to find other libraries
        sym_lib_table = os.path.join(self.schematic_dir, "sym-lib-table")
        if os.path.exists(sym_lib_table):
            with open(sym_lib_table, "r", encoding="utf-8") as f:
                content = f.read()
                # Extract library paths from sym-lib-table
                lib_matches = re.finditer(
                    r"\(lib\s+\(name\s+([^)]+)\)\s+\(type\s+([^)]+)\)\s+\(uri\s+([^)]+)\)",
                    content,
                )
                for match in lib_matches:
                    lib_name, lib_type, lib_uri = match.groups()
                    if lib_type == "Legacy":
                        # Handle relative paths
                        if lib_uri.startswith("${KIPRJMOD}"):
                            lib_uri = lib_uri.replace("${KIPRJMOD}", self.schematic_dir)
                        if os.path.exists(lib_uri):
                            library_files.append(lib_uri)

        return library_files

    def _load_library(self, library_path: str) -> Dict[str, Any]:
        """
        Load a KiCad library file and extract component definitions.

        Args:
            library_path: Path to the library file

        Returns:
            Dictionary mapping component names to their definitions
        """
        if library_path in self.loaded_files:
            return {}  # Already loaded

        self.loaded_files.add(library_path)
        library_components = {}

        try:
            with open(library_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Extract component definitions
            comp_matches = re.finditer(r"DEF\s+([^\s]+)\s+([^\s]+)\s+", content)
            for match in comp_matches:
                comp_name, comp_prefix = match.groups()
                # Find the end of this component definition
                start_pos = match.start()
                end_pos = content.find("ENDDEF", start_pos)
                if end_pos > start_pos:
                    comp_def = content[start_pos : end_pos + 6]  # Include ENDDEF
                    library_components[comp_name] = {
                        "name": comp_name,
                        "prefix": comp_prefix,
                        "definition": comp_def,
                    }

            console.print(
                f"[green]Loaded library:[/green] {library_path} ({len(library_components)} components)"
            )
            return library_components

        except Exception as e:
            console.print(
                f"[yellow]Warning: Failed to load library {library_path}:[/yellow] {str(e)}"
            )
            return {}

    def _find_hierarchical_sheets(self) -> List[str]:
        """
        Find hierarchical sheet files referenced in the schematic.

        Returns:
            List of paths to hierarchical sheet files
        """
        sheet_files = []

        try:
            with open(self.schematic_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Find sheet references in legacy format
            if not self.is_new_format:
                sheet_matches = re.finditer(r'F1\s+"([^"]+)"', content)
                for match in sheet_matches:
                    sheet_path = match.group(1)
                    # Handle relative paths
                    if not os.path.isabs(sheet_path):
                        sheet_path = os.path.join(self.schematic_dir, sheet_path)
                    if os.path.exists(sheet_path):
                        sheet_files.append(sheet_path)
            else:
                # Find sheet references in new format
                sheet_matches = re.finditer(
                    r'\(sheet\s+.*?\(property\s+"Sheet file"\s+"([^"]+)"',
                    content,
                    re.DOTALL,
                )
                for match in sheet_matches:
                    sheet_path = match.group(1)
                    # Handle relative paths
                    if not os.path.isabs(sheet_path):
                        sheet_path = os.path.join(self.schematic_dir, sheet_path)
                    if os.path.exists(sheet_path):
                        sheet_files.append(sheet_path)

        except Exception as e:
            console.print(
                f"[yellow]Warning: Failed to find hierarchical sheets:[/yellow] {str(e)}"
            )

        return sheet_files

    def _load_dependencies(self):
        """
        Load all dependencies for the schematic.
        """
        if not self.load_dependencies:
            return

        # Load libraries
        library_files = self._find_library_files()
        for lib_file in library_files:
            lib_components = self._load_library(lib_file)
            self.libraries.update(lib_components)

        # Load hierarchical sheets
        sheet_files = self._find_hierarchical_sheets()
        for sheet_file in sheet_files:
            if (
                sheet_file not in self.loaded_files
                and sheet_file != self.schematic_path
            ):
                self.loaded_files.add(sheet_file)
                sheet_parser = KiCadSchematicParser(sheet_file, load_dependencies=True)
                sheet_data = sheet_parser.parse()

                # Add components and nets from the sheet
                self.components.extend(sheet_data.get("components", []))
                self.nets.extend(sheet_data.get("nets", []))

                # Add the sheet to hierarchy
                sheet_name = os.path.basename(sheet_file)
                self.hierarchy.append(
                    {
                        "name": sheet_name,
                        "file": sheet_file,
                        "components": len(sheet_data.get("components", [])),
                        "nets": len(sheet_data.get("nets", [])),
                    }
                )

    def parse(self) -> Dict:
        """
        Parse the KiCad schematic file.

        Returns:
            Dictionary with parsed schematic data
        """
        try:
            with open(self.schematic_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            console.print(f"[red]Error reading schematic file:[/red] {e}")
            return {"components": [], "nets": [], "hierarchy": [], "format": "unknown"}

        lines = content.split("\n")
        i = 0

        # Dictionary to track pins by their coordinates
        pin_positions = {}
        # Dictionary to track components by their reference
        components_by_ref = {}

        while i < len(lines):
            line = lines[i].strip()

            # Parse components
            if line == "$Comp":
                component = {}
                i += 1

                while i < len(lines) and lines[i].strip() != "$EndComp":
                    comp_line = lines[i].strip()

                    if comp_line.startswith("L "):
                        parts = comp_line.split()
                        if len(parts) >= 3:
                            component["lib_id"] = parts[1]
                            component["reference"] = parts[2]

                    elif comp_line.startswith("U "):
                        # Unit number, not critical for our purposes
                        pass

                    elif comp_line.startswith("P "):
                        parts = comp_line.split()
                        try:
                            if len(parts) >= 3:
                                x = float(parts[1]) if parts[1].strip() else 0.0
                                y = float(parts[2]) if parts[2].strip() else 0.0
                                component["position"] = (x, y)
                        except ValueError:
                            # Handle invalid position values
                            component["position"] = (0.0, 0.0)

                    elif comp_line.startswith("F "):
                        parts = comp_line.split()
                        if len(parts) >= 3:
                            field_num = parts[1]
                            field_value = parts[2].strip('"')

                            if field_num == "0":
                                component["reference"] = field_value
                            elif field_num == "1":
                                component["value"] = field_value
                            elif field_num == "2":
                                component["footprint"] = field_value
                            elif field_num == "3":
                                component["datasheet"] = field_value

                    i += 1

                if "reference" in component:
                    self.components.append(component)
                    components_by_ref[component["reference"]] = component

                    # Initialize pins for this component
                    component["pins"] = []

            # Parse wire connections (nets)
            elif line.startswith("Wire Wire Line"):
                i += 1
                if i < len(lines):
                    wire_line = lines[i].strip()
                    parts = wire_line.split()

                    try:
                        if len(parts) >= 4:
                            x1 = float(parts[0]) if parts[0].strip() else 0.0
                            y1 = float(parts[1]) if parts[1].strip() else 0.0
                            x2 = float(parts[2]) if parts[2].strip() else 0.0
                            y2 = float(parts[3]) if parts[3].strip() else 0.0

                            # Create a net for this wire
                            net_code = len(self.nets) + 1
                            net = {
                                "code": net_code,
                                "name": f"Net-{net_code}",
                                "connections": [],
                                "start": (x1, y1),
                                "end": (x2, y2),
                            }
                            self.nets.append(net)

                            # Store the wire endpoints for later connection detection
                            key1 = f"{x1},{y1}"
                            key2 = f"{x2},{y2}"

                            if key1 not in pin_positions:
                                pin_positions[key1] = []
                            pin_positions[key1].append(net)

                            if key2 not in pin_positions:
                                pin_positions[key2] = []
                            pin_positions[key2].append(net)
                    except ValueError:
                        # Handle invalid wire coordinates
                        pass

            # Parse connections (labels)
            elif line.startswith("Connection"):
                parts = line.split()
                if len(parts) >= 4:
                    try:
                        x = float(parts[2]) if parts[2].strip() else 0.0
                        y = float(parts[3]) if parts[3].strip() else 0.0

                        # Find the component closest to this connection point
                        closest_comp = None
                        min_distance = float("inf")

                        for comp in self.components:
                            if "position" in comp:
                                comp_x, comp_y = comp["position"]
                                distance = (
                                    (x - comp_x) ** 2 + (y - comp_y) ** 2
                                ) ** 0.5

                                if distance < min_distance:
                                    min_distance = distance
                                    closest_comp = comp

                        if closest_comp and min_distance < 1000:  # Arbitrary threshold
                            key = f"{x},{y}"
                            if key in pin_positions:
                                for net in pin_positions[key]:
                                    if (
                                        closest_comp["reference"]
                                        not in net["connections"]
                                    ):
                                        net["connections"].append(
                                            closest_comp["reference"]
                                        )
                    except ValueError:
                        pass

            i += 1

        # Post-processing: detect connections between components based on wire endpoints
        # This is a simplified approach - in a real implementation, we would need to analyze
        # the schematic more thoroughly to determine actual component pin connections
        for comp in self.components:
            if "position" in comp:
                comp_x, comp_y = comp["position"]

                # Check if any wire endpoints are close to this component
                for key, nets in pin_positions.items():
                    x, y = map(float, key.split(","))
                    distance = ((x - comp_x) ** 2 + (y - comp_y) ** 2) ** 0.5

                    if distance < 1000:  # Arbitrary threshold
                        for net in nets:
                            if comp["reference"] not in net["connections"]:
                                net["connections"].append(comp["reference"])

        # Clean up nets with less than 2 connections
        self.nets = [net for net in self.nets if len(net["connections"]) >= 2]

        return {
            "components": self.components,
            "nets": self.nets,
            "hierarchy": self.hierarchy,
            "format": "legacy_sch",
        }

    def _parse_new_format(self) -> Dict[str, Any]:
        """
        Parse the new S-expression based .kicad_sch format.

        Returns:
            Dictionary with parsed schematic data
        """
        with open(self.schematic_path, "r", encoding="utf-8") as f:
            content = f.read()

        # In a real implementation, we would use a proper S-expression parser
        # For simplicity, we'll use regex to extract components
        component_matches = re.finditer(
            r'\(symbol\s+\(lib_id\s+"([^"]+)"\)[^)]*\(at\s+([^\)]+)\)[^)]*\(property\s+"Reference"\s+"([^"]+)"[^)]*\(property\s+"Value"\s+"([^"]+)"',
            content,
        )

        for match in component_matches:
            lib_id, position, reference, value = match.groups()
            try:
                pos_parts = position.split()[:2]
                x, y = map(float, pos_parts) if len(pos_parts) >= 2 else (0.0, 0.0)
            except (ValueError, IndexError):
                # Handle invalid position values
                x, y = 0.0, 0.0

            component = {
                "reference": reference,
                "value": value,
                "lib_id": lib_id,
                "position": (x, y),
            }
            self.components.append(component)

        # Extract nets
        net_matches = re.finditer(
            r'\(net\s+\(code\s+(\d+)\)\s+\(name\s+"([^"]+)"\)\)', content
        )
        for match in net_matches:
            net_code, net_name = match.groups()
            try:
                code = int(net_code) if net_code.strip() else 0
            except ValueError:
                # Handle invalid net code values
                code = 0

            self.nets.append({"code": code, "name": net_name})

        return {
            "components": self.components,
            "nets": self.nets,
            "hierarchy": self.hierarchy,
            "format": "kicad_sch",
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

        for component in sorted(self.components, key=lambda c: c.get("reference", "")):
            ref = component.get("reference", "Unknown")
            value = component.get("value", "Unknown")
            lib_id = component.get("lib_id", "Unknown")
            position = component.get("position", (0, 0))

            table.add_row(ref, value, lib_id, f"({position[0]}, {position[1]})")

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
            name = sheet.get("name", "Unknown")
            file = sheet.get("file", "Unknown")

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
            value = component.get("value", "Unknown")
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
    for value, count in sorted(
        component_types.items(), key=lambda x: x[1], reverse=True
    ):
        type_table.add_row(value, str(count))
    console.print(type_table)

    # Display hierarchy
    if parser.hierarchy:
        console.print("\n[bold]Schematic Hierarchy:[/bold]")
        console.print(hierarchy_tree)

    # Display summary
    console.print(
        f"\n[bold]Summary:[/bold] {len(parser.components)} components, {len(parser.nets)} nets, {len(parser.hierarchy)} sheets"
    )

    return {
        "schematic_data": schematic_data,
        "component_table": component_table,
        "hierarchy_tree": hierarchy_tree,
        "component_types": component_types,
        "total_components": len(schematic_data["components"]),
        "total_nets": len(schematic_data["nets"]),
    }
