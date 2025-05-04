"""
KiCad command module.

This module provides CLI commands for working with KiCad files,
including schematic and PCB parsing and conversion.
"""

import os
import sys
import argparse
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax

from twinizer.hardware.kicad.sch_parser import SchematicParser
from twinizer.hardware.kicad.pcb_parser import PCBParser
from twinizer.hardware.kicad.converters import (
    SchematicToMermaid, SchematicToBOM, PCBToMermaid, PCBTo3DModel,
    convert_kicad_to_image, convert_kicad_to_mermaid, convert_kicad_to_svg
)

console = Console()


@click.group(name="kicad", help="Commands for working with KiCad files")
def kicad_group():
    """KiCad command group."""
    pass


@kicad_group.command(name="parse-sch", help="Parse KiCad schematic file")
@click.argument("schematic_file", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--format", "-f", type=click.Choice(["json", "yaml", "text"]), default="text", 
              help="Output format")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def parse_schematic(schematic_file: str, output: Optional[str] = None, 
                   format: str = "text", verbose: bool = False):
    """
    Parse a KiCad schematic file and output the results.
    
    Args:
        schematic_file: Path to the KiCad schematic file
        output: Output file path (optional)
        format: Output format (json, yaml, or text)
        verbose: Enable verbose output
    """
    try:
        # Parse the schematic
        parser = SchematicParser(verbose=verbose)
        schematic = parser.parse(schematic_file)
        
        # Format the output
        if format == "json":
            import json
            result = json.dumps(schematic.to_dict(), indent=2)
        elif format == "yaml":
            import yaml
            result = yaml.dump(schematic.to_dict(), default_flow_style=False)
        else:  # text
            result = _format_schematic_text(schematic)
        
        # Output the result
        if output:
            with open(output, "w") as f:
                f.write(result)
            console.print(f"[green]Schematic parsed and saved to {output}[/green]")
        else:
            console.print(result)
    
    except Exception as e:
        console.print(f"[red]Error parsing schematic: {e}[/red]")
        if verbose:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)


@kicad_group.command(name="parse-pcb", help="Parse KiCad PCB file")
@click.argument("pcb_file", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--format", "-f", type=click.Choice(["json", "yaml", "text"]), default="text", 
              help="Output format")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def parse_pcb(pcb_file: str, output: Optional[str] = None, 
             format: str = "text", verbose: bool = False):
    """
    Parse a KiCad PCB file and output the results.
    
    Args:
        pcb_file: Path to the KiCad PCB file
        output: Output file path (optional)
        format: Output format (json, yaml, or text)
        verbose: Enable verbose output
    """
    try:
        # Parse the PCB
        parser = PCBParser(verbose=verbose)
        pcb = parser.parse(pcb_file)
        
        # Format the output
        if format == "json":
            import json
            result = json.dumps(pcb.to_dict(), indent=2)
        elif format == "yaml":
            import yaml
            result = yaml.dump(pcb.to_dict(), default_flow_style=False)
        else:  # text
            result = _format_pcb_text(pcb)
        
        # Output the result
        if output:
            with open(output, "w") as f:
                f.write(result)
            console.print(f"[green]PCB parsed and saved to {output}[/green]")
        else:
            console.print(result)
    
    except Exception as e:
        console.print(f"[red]Error parsing PCB: {e}[/red]")
        if verbose:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)


@kicad_group.command(name="sch-to-mermaid", help="Convert KiCad schematic to Mermaid diagram")
@click.argument("schematic_file", type=click.Path(exists=True))
@click.option("--diagram-type", type=click.Choice(["flowchart", "class", "graph"]), default="flowchart",
              help="Type of diagram to generate")
@click.option("--output", type=click.Path(), default=None,
              help="Output file path (default: <schematic_name>_<diagram_type>.mmd)")
@click.option("--include-components/--no-include-components", default=True, 
              help="Include component details")
@click.option("--include-values/--no-include-values", default=True, 
              help="Include component values")
@click.option("--include-pins/--no-include-pins", default=False, 
              help="Include component pins")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def schematic_to_mermaid(schematic_file: str, output: Optional[str] = None,
                        diagram_type: str = "flowchart",
                        include_components: bool = True, include_values: bool = True,
                        include_pins: bool = False, verbose: bool = False):
    """
    Convert a KiCad schematic to a Mermaid diagram.
    
    Args:
        schematic_file: Path to the KiCad schematic file
        output: Output file path (optional)
        diagram_type: Type of diagram to generate (flowchart, class, or graph)
        include_components: Include component details
        include_values: Include component values
        include_pins: Include component pins
        verbose: Enable verbose output
    """
    try:
        # Create the converter
        converter = SchematicToMermaid(schematic_file)
        
        # Generate the diagram
        if diagram_type == "flowchart":
            output_path = converter.to_flowchart(output)
        elif diagram_type == "class":
            output_path = converter.to_class_diagram(output)
        elif diagram_type == "graph":
            output_path = converter.to_graph(output)
        else:
            raise ValueError(f"Unsupported diagram type: {diagram_type}")
        
        console.print(f"[green]Mermaid diagram generated:[/green] {output_path}")
    
    except Exception as e:
        console.print(f"[red]Error generating Mermaid diagram:[/red] {e}")
        if verbose:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)


@kicad_group.command(name="sch-to-bom", help="Generate BOM from KiCad schematic")
@click.argument("schematic_file", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--format", "-f", type=click.Choice(["csv", "markdown"]), default="csv",
              help="Output format")
@click.option("--group-by", type=click.Choice(["value", "footprint", "library", "none"]), default="value",
              help="Group components by")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def schematic_to_bom(schematic_file: str, output: Optional[str] = None,
                    format: str = "csv", group_by: str = "value",
                    verbose: bool = False):
    """
    Generate a Bill of Materials (BOM) from a KiCad schematic.
    
    Args:
        schematic_file: Path to the KiCad schematic file
        output: Output file path (optional)
        format: Output format (csv, json, markdown, or html)
        group_by: Group components by (value, footprint, library, or none)
        verbose: Enable verbose output
    """
    try:
        # Create converter
        converter = SchematicToBOM(schematic_file)
        
        # Generate BOM based on format
        if format == "csv":
            output_path = converter.to_csv(output)
        else:  # markdown
            output_path = converter.to_markdown(output)
            
        if verbose:
            console.print(f"[green]BOM saved to:[/green] {output_path}")
            
    except Exception as e:
        console.print(f"[red]Error generating BOM:[/red] {e}")
        sys.exit(1)


@kicad_group.command(name="pcb-to-mermaid", help="Convert KiCad PCB to Mermaid diagram")
@click.argument("pcb_file", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--diagram-type", type=click.Choice(["flowchart", "class"]), default="flowchart",
              help="Type of diagram to generate")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def pcb_to_mermaid(pcb_file: str, output: Optional[str] = None,
                  diagram_type: str = "flowchart", verbose: bool = False):
    """
    Convert a KiCad PCB to a Mermaid diagram.
    
    Args:
        pcb_file: Path to the KiCad PCB file
        output: Output file path (optional)
        diagram_type: Type of diagram to generate (flowchart or class)
        verbose: Enable verbose output
    """
    try:
        # Create converter
        converter = PCBToMermaid(pcb_file)
        
        # Generate diagram based on type
        if diagram_type == "flowchart":
            output_path = converter.to_flowchart(output)
        else:  # class diagram
            output_path = converter.to_class_diagram(output)
            
        if verbose:
            console.print(f"[green]Mermaid PCB diagram saved to:[/green] {output_path}")
            
    except Exception as e:
        console.print(f"[red]Error converting PCB to Mermaid:[/red] {e}")
        sys.exit(1)


@kicad_group.command(name="pcb-to-3d", help="Convert KiCad PCB to 3D model")
@click.argument("pcb_file", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--format", "-f", type=click.Choice(["stl", "step", "vrml"]), default="step",
              help="Output format")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def pcb_to_3d(pcb_file: str, output: Optional[str] = None,
             format: str = "step", verbose: bool = False):
    """
    Convert a KiCad PCB to a 3D model.
    
    Args:
        pcb_file: Path to the KiCad PCB file
        output: Output file path (optional)
        format: Output format (stl, step, or vrml)
        verbose: Enable verbose output
    """
    try:
        # Create converter
        converter = PCBTo3DModel(pcb_file)
        
        # Generate 3D model based on format
        if format == "stl":
            output_path = converter.to_stl(output)
        elif format == "step":
            output_path = converter.to_step(output)
        else:  # vrml
            output_path = converter.to_vrml(output)
            
        if verbose and output_path:
            console.print(f"[green]3D model saved to:[/green] {output_path}")
            
    except Exception as e:
        console.print(f"[red]Error converting PCB to 3D model:[/red] {e}")
        sys.exit(1)


@kicad_group.command(name="sch-to-svg", help="Convert KiCad schematic to SVG")
@click.argument('schematic_file', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output SVG file path')
@click.option('--theme', '-t', type=click.Choice(['default', 'dark', 'blue', 'minimal']), 
              default='default', help='Theme for the SVG output')
@click.option('--html', '-w', is_flag=True, help='Generate HTML file with embedded SVG')
def schematic_to_svg(schematic_file, output, theme, html):
    """
    Convert KiCad schematic to SVG format.
    
    This command converts a KiCad schematic file (.kicad_sch) to SVG format using schemdraw.
    It can also generate an HTML file with the SVG embedded for easy viewing.
    
    Example:
        twinizer kicad schematic-to-svg path/to/schematic.kicad_sch --theme dark --html
    """
    try:
        result = convert_kicad_to_svg(schematic_file, output, theme, html)
        
        if html:
            svg_path, html_path = result
            click.echo(f"SVG file created: {svg_path}")
            click.echo(f"HTML file created: {html_path}")
        else:
            click.echo(f"SVG file created: {result}")
            
    except ImportError as e:
        click.echo(f"Error: {e}")
        click.echo("Please install the required package with: pip install schemdraw")
    except Exception as e:
        click.echo(f"Error during conversion: {e}")


def _format_schematic_text(schematic) -> str:
    """Format schematic as text."""
    result = f"Schematic: {schematic.name}\n\n"
    
    # Components
    table = Table(title="Components")
    table.add_column("Reference")
    table.add_column("Value")
    table.add_column("Footprint")
    table.add_column("Library")
    
    for component in schematic.components:
        table.add_row(
            component.reference,
            component.value,
            component.footprint,
            component.library
        )
    
    result += str(table) + "\n\n"
    
    # Nets
    table = Table(title="Nets")
    table.add_column("Name")
    table.add_column("Connections")
    
    for net in schematic.nets:
        connections = ", ".join([f"{conn.component}:{conn.pin}" for conn in net.connections])
        table.add_row(net.name, connections)
    
    result += str(table)
    
    return result


def _format_pcb_text(pcb) -> str:
    """Format PCB as text."""
    result = f"PCB: {pcb.name}\n\n"
    
    # Layers
    table = Table(title="Layers")
    table.add_column("Number")
    table.add_column("Name")
    table.add_column("Type")
    
    for layer in pcb.layers:
        table.add_row(
            str(layer.number),
            layer.name,
            layer.type
        )
    
    result += str(table) + "\n\n"
    
    # Modules (Footprints)
    table = Table(title="Modules (Footprints)")
    table.add_column("Reference")
    table.add_column("Value")
    table.add_column("Layer")
    table.add_column("Position")
    
    for module in pcb.modules:
        table.add_row(
            module.reference,
            module.value,
            module.layer,
            f"({module.position_x}, {module.position_y})"
        )
    
    result += str(table) + "\n\n"
    
    # Tracks
    table = Table(title="Tracks")
    table.add_column("Layer")
    table.add_column("Width")
    table.add_column("Net")
    table.add_column("Start")
    table.add_column("End")
    
    for track in pcb.tracks[:10]:  # Limit to first 10 tracks to avoid overwhelming output
        table.add_row(
            track.layer,
            str(track.width),
            track.net,
            f"({track.start_x}, {track.start_y})",
            f"({track.end_x}, {track.end_y})"
        )
    
    if len(pcb.tracks) > 10:
        result += str(table) + f"\n... and {len(pcb.tracks) - 10} more tracks\n\n"
    else:
        result += str(table) + "\n\n"
    
    return result
