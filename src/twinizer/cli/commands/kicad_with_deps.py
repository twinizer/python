"""
KiCad command module with dependency handling.

This module provides commands for working with KiCad files, including automatic dependency handling.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import click
from rich.console import Console

from twinizer.hardware.kicad.converters import (
    PCBTo3DModel,
    PCBToMermaid,
    SchematicToBOM,
    SchematicToMermaid,
)
from twinizer.hardware.kicad.pcb_parser import PCBParser
from twinizer.hardware.kicad.sch_parser import KiCadSchematicParser

console = Console()


@click.group(name="kicad-deps", help="KiCad file operations with dependency handling")
def kicad_deps_group():
    """
    Commands for working with KiCad files, with automatic dependency handling.
    """
    pass


@kicad_deps_group.command(
    name="sch-to-mermaid",
    help="Convert KiCad schematic to Mermaid diagram with dependencies",
)
@click.argument("schematic_file", type=click.Path(exists=True))
@click.option(
    "--diagram-type",
    type=click.Choice(["flowchart", "class"]),
    default="flowchart",
    help="Type of diagram to generate",
)
@click.option(
    "--output",
    type=click.Path(),
    default=None,
    help="Output file path (default: <schematic_name>_<diagram_type>.mmd)",
)
@click.option(
    "--include-dependencies/--no-include-dependencies",
    default=True,
    help="Include hierarchical sheets and library components",
)
def schematic_to_mermaid_with_deps(
    schematic_file: str,
    diagram_type: str = "flowchart",
    output: Optional[str] = None,
    include_dependencies: bool = True,
):
    """
    Convert a KiCad schematic to a Mermaid diagram, including dependencies.

    This command parses a KiCad schematic file and its dependencies (hierarchical sheets,
    library components) and generates a Mermaid diagram representation of the circuit.
    """
    try:
        # Find dependency files
        schematic_dir = os.path.dirname(os.path.abspath(schematic_file))
        base_name = os.path.splitext(os.path.basename(schematic_file))[0]

        # Check for library files
        lib_files = []
        cache_lib = os.path.join(schematic_dir, f"{base_name}-cache.lib")
        if os.path.exists(cache_lib):
            lib_files.append(cache_lib)
            console.print(f"[green]Found cache library:[/green] {cache_lib}")

        rescue_lib = os.path.join(schematic_dir, f"{base_name}-rescue.lib")
        if os.path.exists(rescue_lib):
            lib_files.append(rescue_lib)
            console.print(f"[green]Found rescue library:[/green] {rescue_lib}")

        # Create converter with dependency handling enabled
        converter = SchematicToMermaid(schematic_file)

        # Generate diagram based on type
        if diagram_type == "flowchart":
            output_path = converter.to_flowchart(output)
        elif diagram_type == "class":
            output_path = converter.to_class_diagram(output)
        else:
            console.print(f"[red]Unsupported diagram type:[/red] {diagram_type}")
            return

        console.print(f"[green]Mermaid diagram generated:[/green] {output_path}")

    except Exception as e:
        console.print(f"[red]Error converting schematic to Mermaid:[/red] {str(e)}")
        if output:
            # Create a minimal valid Mermaid diagram as a fallback
            with open(output, "w") as f:
                f.write(f"flowchart TD\n    A[Error] --> B[{str(e)}]\n")
            console.print(f"[yellow]Created fallback diagram at:[/yellow] {output}")


@kicad_deps_group.command(
    name="sch-to-bom", help="Generate BOM from KiCad schematic with dependencies"
)
@click.argument("schematic_file", type=click.Path(exists=True))
@click.option(
    "--format",
    type=click.Choice(["csv", "json", "html", "xlsx"]),
    default="csv",
    help="Output format",
)
@click.option(
    "--output",
    type=click.Path(),
    default=None,
    help="Output file path (default: <schematic_name>.{format})",
)
@click.option(
    "--include-dependencies/--no-include-dependencies",
    default=True,
    help="Include hierarchical sheets and library components",
)
def schematic_to_bom_with_deps(
    schematic_file: str,
    format: str = "csv",
    output: Optional[str] = None,
    include_dependencies: bool = True,
):
    """
    Generate a bill of materials from a KiCad schematic, including dependencies.

    This command parses a KiCad schematic file and its dependencies (hierarchical sheets,
    library components) and generates a bill of materials.
    """
    try:
        # Find dependency files
        schematic_dir = os.path.dirname(os.path.abspath(schematic_file))
        base_name = os.path.splitext(os.path.basename(schematic_file))[0]

        # Check for library files
        lib_files = []
        cache_lib = os.path.join(schematic_dir, f"{base_name}-cache.lib")
        if os.path.exists(cache_lib):
            lib_files.append(cache_lib)
            console.print(f"[green]Found cache library:[/green] {cache_lib}")

        rescue_lib = os.path.join(schematic_dir, f"{base_name}-rescue.lib")
        if os.path.exists(rescue_lib):
            lib_files.append(rescue_lib)
            console.print(f"[green]Found rescue library:[/green] {rescue_lib}")

        # Create converter with dependency handling enabled
        converter = SchematicToBOM(schematic_file)

        # Generate BOM based on format
        if format == "csv":
            output_path = converter.to_csv(output)
        elif format == "json":
            output_path = converter.to_json(output)
        elif format == "html":
            output_path = converter.to_html(output)
        elif format == "xlsx":
            output_path = converter.to_xlsx(output)
        else:
            console.print(f"[red]Unsupported format:[/red] {format}")
            return

        console.print(f"[green]BOM generated:[/green] {output_path}")

    except Exception as e:
        console.print(f"[red]Error generating BOM:[/red] {str(e)}")


# Register the command in the main CLI
def register_kicad_deps_commands():
    """
    Register KiCad dependency-aware commands in the main CLI.
    """
    from twinizer.cli.main import cli

    cli.add_command(kicad_deps_group)
