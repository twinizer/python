"""
KiCad Docker command module.

This module provides CLI commands for working with KiCad files using Docker,
including schematic and PCB conversion to various formats and project analysis.
"""

import os
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from twinizer.converters.kicad2image import (
    analyze_kicad_project,
    convert_kicad_file,
    list_supported_formats,
)

console = Console()


@click.group(
    name="kicad-docker", help="Commands for working with KiCad files using Docker"
)
def kicad_docker_group():
    """KiCad Docker command group."""
    pass


@kicad_docker_group.command(
    name="convert", help="Convert KiCad file to various formats using Docker"
)
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "--format",
    "-f",
    type=str,
    default="svg",
    help="Output format (svg, png, pdf, dxf, hpgl, ps, eps)",
)
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option(
    "--color-theme",
    "-c",
    type=click.Choice(["light", "dark"]),
    default="light",
    help="Color theme for PDF output",
)
@click.option(
    "--paper-size",
    "-p",
    type=str,
    default="A4",
    help="Paper size for PDF output (A4, A3, etc.)",
)
@click.option(
    "--orientation",
    "-r",
    type=click.Choice(["portrait", "landscape"]),
    default="portrait",
    help="Page orientation for PDF output",
)
@click.option(
    "--debug", "-d", is_flag=True, help="Enable debug mode to analyze the project"
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def convert_kicad(
    input_file: str,
    format: str = "svg",
    output: Optional[str] = None,
    color_theme: str = "light",
    paper_size: str = "A4",
    orientation: str = "portrait",
    debug: bool = False,
    verbose: bool = False,
):
    """
    Convert a KiCad file to the specified format using Docker.

    Args:
        input_file: Path to the KiCad file (.sch, .kicad_sch, .kicad_pcb)
        format: Output format (svg, png, pdf, dxf, hpgl, ps, eps)
        output: Path to save the output file
        color_theme: Color theme for PDF output (light, dark)
        paper_size: Paper size for PDF output (A4, A3, etc.)
        orientation: Page orientation for PDF output (portrait, landscape)
        debug: Enable debug mode to analyze the project
        verbose: Enable verbose output
    """
    try:
        # Convert the file
        result = convert_kicad_file(
            input_file=input_file,
            output_format=format,
            output_path=output,
            color_theme=color_theme,
            paper_size=paper_size,
            orientation=orientation,
            debug=debug,
            verbose=verbose,
        )

        if result:
            console.print(f"[green]Conversion successful![/green]")
            console.print(f"Output file: [cyan]{result}[/cyan]")
        else:
            console.print("[red]Conversion failed.[/red]")
            sys.exit(1)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if verbose:
            import traceback

            console.print(traceback.format_exc())
        sys.exit(1)


@kicad_docker_group.command(
    name="analyze", help="Analyze KiCad project for missing dependencies"
)
@click.argument(
    "project_dir", type=click.Path(exists=True, file_okay=False, dir_okay=True)
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "html"]),
    default="html",
    help="Output format (json, html)",
)
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def analyze_project(
    project_dir: str,
    format: str = "html",
    output: Optional[str] = None,
    verbose: bool = False,
):
    """
    Analyze a KiCad project for missing dependencies.

    Args:
        project_dir: Path to the KiCad project directory
        format: Output format (json, html)
        output: Path to save the output file
        verbose: Enable verbose output
    """
    try:
        # Analyze the project
        result = analyze_kicad_project(
            project_dir=project_dir,
            output_format=format,
            output_path=output,
            verbose=verbose,
        )

        if result:
            if format == "json":
                # Display a summary of the analysis results
                console.print("[green]Analysis successful![/green]")

                # Create a table with the results
                table = Table(title="KiCad Project Analysis")
                table.add_column("Category", style="cyan")
                table.add_column("Total", style="green")
                table.add_column("Missing", style="red")

                # Add rows to the table
                if "components" in result:
                    total = len(result["components"])
                    missing = sum(
                        1 for c in result["components"] if c.get("missing", False)
                    )
                    table.add_row("Components", str(total), str(missing))

                if "libraries" in result:
                    total = len(result["libraries"])
                    missing = sum(
                        1 for l in result["libraries"] if l.get("missing", False)
                    )
                    table.add_row("Libraries", str(total), str(missing))

                if "models" in result:
                    total = len(result["models"])
                    missing = sum(
                        1 for m in result["models"] if m.get("missing", False)
                    )
                    table.add_row("3D Models", str(total), str(missing))

                console.print(table)

                # If output file was specified, show its path
                if output:
                    console.print(f"Full analysis saved to: [cyan]{output}[/cyan]")
            else:  # html
                console.print("[green]Analysis successful![/green]")
                console.print(f"HTML report saved to: [cyan]{result}[/cyan]")

                # Try to open the HTML file in the default browser
                try:
                    import webbrowser

                    webbrowser.open(f"file://{os.path.abspath(result)}")
                except Exception as e:
                    console.print(f"[yellow]Could not open browser: {e}[/yellow]")
        else:
            console.print("[red]Analysis failed.[/red]")
            sys.exit(1)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if verbose:
            import traceback

            console.print(traceback.format_exc())
        sys.exit(1)


@kicad_docker_group.command(name="formats", help="List supported output formats")
def list_formats():
    """List all supported output formats for KiCad file conversion."""
    formats = list_supported_formats()

    # Create a table with the formats
    table = Table(title="Supported Output Formats")
    table.add_column("Format", style="cyan")
    table.add_column("Description", style="green")
    table.add_column("Default", style="yellow")
    table.add_column("Options", style="blue")

    # Add rows to the table
    for fmt in formats:
        default = "✓" if fmt.get("default", False) else ""
        options = ", ".join(fmt.get("options", []))
        table.add_row(fmt["format"], fmt["description"], default, options)

    console.print(table)
