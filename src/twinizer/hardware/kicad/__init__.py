"""
KiCad schematic and PCB analysis package.

This package provides functionality to parse and analyze KiCad schematic (.sch, .kicad_sch)
and PCB layout (.kicad_pcb) files.
"""

from .converters import convert_kicad_to_image
from .pcb_parser import KiCadPCBParser, analyze_kicad_pcb
from .sch_parser import KiCadSchematicParser, analyze_kicad_schematic

__all__ = [
    "KiCadSchematicParser",
    "KiCadPCBParser",
    "analyze_kicad_schematic",
    "analyze_kicad_pcb",
    "convert_kicad_to_image",
]
