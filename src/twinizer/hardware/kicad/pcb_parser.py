"""
KiCad PCB parser module.

This module provides functionality to parse and analyze KiCad PCB layout (.kicad_pcb) files.
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from rich.console import Console
from rich.table import Table

console = Console()


class KiCadPCBParser:
    """
    Parser for KiCad PCB layout files (.kicad_pcb).
    """

    def __init__(self, pcb_path: str):
        """
        Initialize the parser with a PCB file path.

        Args:
            pcb_path: Path to the KiCad PCB file
        """
        self.pcb_path = pcb_path
        self.modules = []
        self.tracks = []
        self.zones = []
        self.vias = []
        self.dimensions = (0, 0)

    def parse(self) -> Dict[str, Any]:
        """
        Parse the PCB file and extract modules, tracks, and zones.

        Returns:
            Dictionary with parsed PCB data
        """
        if not os.path.exists(self.pcb_path):
            raise FileNotFoundError(f"PCB file not found: {self.pcb_path}")

        with open(self.pcb_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract modules (footprints)
        self._extract_modules(content)

        # Extract tracks
        self._extract_tracks(content)

        # Extract vias
        self._extract_vias(content)

        # Extract zones
        self._extract_zones(content)

        # Extract board dimensions
        self._extract_board_dimensions(content)

        return {
            "modules": self.modules,
            "tracks": self.tracks,
            "vias": self.vias,
            "zones": self.zones,
            "dimensions": self.dimensions,
        }

    def _extract_modules(self, content: str) -> None:
        """
        Extract modules (footprints) from PCB content.

        Args:
            content: PCB file content
        """
        # In a real implementation, we would use a proper S-expression parser
        # For simplicity, we'll use regex to extract modules (footprints)
        module_pattern = r"\((module|footprint)\s+([^\s\)]+)[^)]*\(at\s+([^\)]+)\)[^)]*\(layer\s+([^\)]+)\)"
        module_matches = re.finditer(module_pattern, content)

        for match in module_matches:
            _, name, position, layer = match.groups()
            position_parts = position.split()
            x, y = float(position_parts[0]), float(position_parts[1])
            rotation = float(position_parts[2]) if len(position_parts) > 2 else 0.0

            # Extract reference and value from the matched module section
            module_content = content[
                match.start() : content.find(")", match.start(), match.start() + 10000)
            ]

            # Extract reference
            ref_match = re.search(r"\(fp_text\s+reference\s+([^\s\)]+)", module_content)
            reference = ref_match.group(1) if ref_match else "Unknown"

            # Extract value
            val_match = re.search(r"\(fp_text\s+value\s+([^\s\)]+)", module_content)
            value = val_match.group(1) if val_match else "Unknown"

            # Clean up reference and value (remove quotes)
            reference = reference.strip('"')
            value = value.strip('"')

            module = {
                "name": name,
                "reference": reference,
                "value": value,
                "position": (x, y),
                "rotation": rotation,
                "layer": layer,
            }
            self.modules.append(module)

    def _extract_tracks(self, content: str) -> None:
        """
        Extract tracks from PCB content.

        Args:
            content: PCB file content
        """
        # Extract tracks
        track_pattern = r"\(segment\s+\(start\s+([^\)]+)\)\s+\(end\s+([^\)]+)\)\s+\(width\s+([^\)]+)\)\s+\(layer\s+([^\)]+)\)"
        track_matches = re.finditer(track_pattern, content)

        for match in track_matches:
            start, end, width, layer = match.groups()
            start_x, start_y = map(float, start.split())
            end_x, end_y = map(float, end.split())

            track = {
                "start": (start_x, start_y),
                "end": (end_x, end_y),
                "width": float(width),
                "layer": layer,
            }
            self.tracks.append(track)

    def _extract_vias(self, content: str) -> None:
        """
        Extract vias from PCB content.

        Args:
            content: PCB file content
        """
        # Extract vias
        via_pattern = r"\(via\s+\(at\s+([^\)]+)\)\s+\(size\s+([^\)]+)\)"
        via_matches = re.finditer(via_pattern, content)

        for match in via_matches:
            position, size = match.groups()
            x, y = map(float, position.split())

            via = {"position": (x, y), "size": float(size)}
            self.vias.append(via)

    def _extract_zones(self, content: str) -> None:
        """
        Extract zones from PCB content.

        Args:
            content: PCB file content
        """
        # Extract zones (copper pours)
        zone_pattern = r"\(zone\s+[^)]*\(layer\s+([^\)]+)\)"
        zone_matches = re.finditer(zone_pattern, content)

        for match in zone_matches:
            layer = match.group(1)

            zone = {"layer": layer}
            self.zones.append(zone)

    def _extract_board_dimensions(self, content: str) -> None:
        """
        Extract board dimensions from PCB content.

        Args:
            content: PCB file content
        """
        # Look for page dimensions
        page_match = re.search(r"\(page\s+([A-Za-z0-9]+)\)", content)
        if page_match:
            page_size = page_match.group(1)
            # Standard page sizes
            page_sizes = {
                "A4": (297, 210),
                "A3": (420, 297),
                "A2": (594, 420),
                "A1": (841, 594),
                "A0": (1189, 841),
                "Letter": (279.4, 215.9),
                "Legal": (355.6, 215.9),
            }
            if page_size in page_sizes:
                self.dimensions = page_sizes[page_size]

        # Look for sheet size
        sheet_match = re.search(
            r'\(page\s+"([^"]+)"\s+([0-9.]+)\s+([0-9.]+)\)', content
        )
        if sheet_match:
            width = float(sheet_match.group(2))
            height = float(sheet_match.group(3))
            self.dimensions = (width, height)

        # As a fallback, calculate from module positions
        if self.dimensions == (0, 0) and self.modules:
            min_x = min(m["position"][0] for m in self.modules)
            max_x = max(m["position"][0] for m in self.modules)
            min_y = min(m["position"][1] for m in self.modules)
            max_y = max(m["position"][1] for m in self.modules)

            # Add some margin
            width = max_x - min_x + 20
            height = max_y - min_y + 20

            self.dimensions = (width, height)

    def generate_module_list(self) -> Table:
        """
        Generate a table of modules (footprints) in the PCB.

        Returns:
            Rich Table object with module information
        """
        if not self.modules:
            self.parse()

        table = Table(
            "Reference", "Value", "Footprint", "Layer", "Position", "Rotation"
        )

        for module in sorted(self.modules, key=lambda m: m.get("reference", "")):
            ref = module.get("reference", "Unknown")
            value = module.get("value", "Unknown")
            name = module.get("name", "Unknown")
            layer = module.get("layer", "Unknown")
            position = module.get("position", (0, 0))
            rotation = module.get("rotation", 0.0)

            table.add_row(
                ref,
                value,
                name,
                layer,
                f"({position[0]:.2f}, {position[1]:.2f})",
                f"{rotation}°",
            )

        return table

    def get_statistics(self) -> Dict[str, Any]:
        """
        Generate statistics about the PCB.

        Returns:
            Dictionary with PCB statistics
        """
        if not self.modules:
            self.parse()

        # Count components by layer
        components_by_layer = {}
        for module in self.modules:
            layer = module.get("layer", "Unknown")
            components_by_layer[layer] = components_by_layer.get(layer, 0) + 1

        # Count tracks by layer
        tracks_by_layer = {}
        total_track_length = 0
        for track in self.tracks:
            layer = track.get("layer", "Unknown")
            tracks_by_layer[layer] = tracks_by_layer.get(layer, 0) + 1

            # Calculate track length
            start = track.get("start", (0, 0))
            end = track.get("end", (0, 0))
            length = ((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2) ** 0.5
            total_track_length += length

        # Count vias
        via_count = len(self.vias)

        # Count zones by layer
        zones_by_layer = {}
        for zone in self.zones:
            layer = zone.get("layer", "Unknown")
            zones_by_layer[layer] = zones_by_layer.get(layer, 0) + 1

        return {
            "total_components": len(self.modules),
            "components_by_layer": components_by_layer,
            "total_tracks": len(self.tracks),
            "tracks_by_layer": tracks_by_layer,
            "total_track_length": total_track_length,
            "total_vias": via_count,
            "zones_by_layer": zones_by_layer,
            "board_dimensions": self.dimensions,
        }


# Create an alias for backward compatibility
PCBParser = KiCadPCBParser


def analyze_kicad_pcb(pcb_path: str) -> Dict[str, Any]:
    """
    Analyze a KiCad PCB layout file.

    Args:
        pcb_path: Path to the KiCad PCB file

    Returns:
        Dictionary with PCB analysis results
    """
    parser = KiCadPCBParser(pcb_path)
    pcb_data = parser.parse()

    console.print(f"[green]Analyzing PCB layout:[/green] {pcb_path}")

    # Generate module table
    module_table = parser.generate_module_list()
    console.print(module_table)

    # Get statistics
    statistics = parser.get_statistics()

    # Display statistics
    console.print("\n[bold]PCB Statistics:[/bold]")
    console.print(
        f"Board dimensions: {statistics['board_dimensions'][0]:.2f} x {statistics['board_dimensions'][1]:.2f} mm"
    )
    console.print(f"Total components: {statistics['total_components']}")
    console.print(f"Total tracks: {statistics['total_tracks']}")
    console.print(f"Total track length: {statistics['total_track_length']:.2f} mm")
    console.print(f"Total vias: {statistics['total_vias']}")

    # Components by layer
    console.print("\n[bold]Components by Layer:[/bold]")
    layer_table = Table("Layer", "Count")
    for layer, count in statistics["components_by_layer"].items():
        layer_table.add_row(layer, str(count))
    console.print(layer_table)

    # Tracks by layer
    console.print("\n[bold]Tracks by Layer:[/bold]")
    track_table = Table("Layer", "Count")
    for layer, count in statistics["tracks_by_layer"].items():
        track_table.add_row(layer, str(count))
    console.print(track_table)

    return {
        "pcb_data": pcb_data,
        "module_table": module_table,
        "statistics": statistics,
    }
