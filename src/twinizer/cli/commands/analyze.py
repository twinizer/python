"""
analyze.py
"""

"""
Analyze command for the Twinizer CLI.

This module provides commands for analyzing project structure, hardware files,
firmware files, and binary files.
"""

import os

import click
from rich.console import Console
from rich.panel import Panel

from twinizer.core.project import Project

console = Console()


@click.group(name="analyze")
def analyze():
    """
    Analyze project structure and files.

    This command provides various subcommands for analyzing different aspects
    of a project, including structure, hardware files, firmware files, and binary files.
    """
    pass


@analyze.command(name="structure")
@click.option(
    "--source-dir",
    "-d",
    default=None,
    help="Source directory to analyze (defaults to ./source)",
)
def analyze_structure(source_dir):
    """
    Analyze project directory structure.

    This command scans the project directory and identifies hardware files,
    firmware files, binary files, and other components.
    """
    if source_dir is None:
        source_dir = os.environ.get("TWINIZER_SOURCE_DIR", "./source")

    console.print(f"[bold blue]Analyzing project structure:[/bold blue] {source_dir}")

    project = Project(source_dir)
    project.scan()
    project.analyze_structure()


@analyze.command(name="hardware")
@click.argument("file", required=False)
@click.option(
    "--source-dir",
    "-d",
    default=None,
    help="Source directory to analyze (defaults to ./source)",
)
def analyze_hardware(file, source_dir):
    """
    Analyze hardware files (schematics, PCB).

    If a specific file is provided, it will be analyzed in detail.
    Otherwise, all hardware files in the project will be analyzed.
    """
    if source_dir is None:
        source_dir = os.environ.get("TWINIZER_SOURCE_DIR", "./source")

    project = Project(source_dir)

    if file:
        # Analyze specific file
        file_path = os.path.join(source_dir, file)
        if not os.path.exists(file_path):
            console.print(f"[bold red]Error:[/bold red] File not found: {file}")
            return

        console.print(f"[bold blue]Analyzing hardware file:[/bold blue] {file}")

        if file.endswith((".sch", ".kicad_sch")):
            from twinizer.hardware.kicad import analyze_kicad_schematic

            analyze_kicad_schematic(file_path)
        elif file.endswith(".kicad_pcb"):
            from twinizer.hardware.kicad import analyze_kicad_pcb

            analyze_kicad_pcb(file_path)
        elif file.endswith((".SchDoc", ".PcbDoc")):
            console.print(
                Panel(
                    "Altium files (.SchDoc, .PcbDoc) analysis is not fully implemented yet.",
                    title="Altium Analysis",
                    border_style="yellow",
                )
            )
        else:
            console.print(
                f"[bold yellow]Warning:[/bold yellow] Unsupported hardware file format: {file}"
            )
    else:
        # Analyze all hardware files
        project.scan()
        project.analyze_hardware()


@analyze.command(name="firmware")
@click.argument("file", required=False)
@click.option(
    "--source-dir",
    "-d",
    default=None,
    help="Source directory to analyze (defaults to ./source)",
)
def analyze_firmware(file, source_dir):
    """
    Analyze firmware files (.c, .h, etc.).

    If a specific file is provided, it will be analyzed in detail.
    Otherwise, all firmware files in the project will be analyzed.
    """
    if source_dir is None:
        source_dir = os.environ.get("TWINIZER_SOURCE_DIR", "./source")

    project = Project(source_dir)

    if file:
        # Analyze specific file
        file_path = os.path.join(source_dir, file)
        if not os.path.exists(file_path):
            console.print(f"[bold red]Error:[/bold red] File not found: {file}")
            return

        console.print(f"[bold blue]Analyzing firmware file:[/bold blue] {file}")

        if file.endswith((".c", ".h")):
            from twinizer.software.analyze import analyze_c_file

            analyze_c_file(file_path)
        elif file.endswith((".cpp", ".hpp")):
            from twinizer.software.analyze import analyze_cpp_file

            analyze_cpp_file(file_path)
        elif file.endswith(".asm"):
            from twinizer.software.analyze import analyze_asm_file

            analyze_asm_file(file_path)
        else:
            console.print(
                f"[bold yellow]Warning:[/bold yellow] Unsupported firmware file format: {file}"
            )
    else:
        # Analyze all firmware files
        project.scan()
        project.analyze_firmware()


@analyze.command(name="binary")
@click.argument("file", required=True)
@click.option(
    "--source-dir",
    "-d",
    default=None,
    help="Source directory to analyze (defaults to ./source)",
)
def analyze_binary(file, source_dir):
    """
    Analyze binary files (.bin, .hex, .elf, etc.).

    A specific binary file must be provided for detailed analysis.
    """
    if source_dir is None:
        source_dir = os.environ.get("TWINIZER_SOURCE_DIR", "./source")

    project = Project(source_dir)

    file_path = os.path.join(source_dir, file)
    if not os.path.exists(file_path):
        console.print(f"[bold red]Error:[/bold red] File not found: {file}")
        return

    console.print(f"[bold blue]Analyzing binary file:[/bold blue] {file}")
    project.analyze_binary(file)


@analyze.command(name="all")
@click.option(
    "--source-dir",
    "-d",
    default=None,
    help="Source directory to analyze (defaults to ./source)",
)
def analyze_all(source_dir):
    """
    Perform a complete analysis of the project.

    This command analyzes the project structure, hardware files,
    firmware files, and selected binary files.
    """
    if source_dir is None:
        source_dir = os.environ.get("TWINIZER_SOURCE_DIR", "./source")

    console.print(
        f"[bold blue]Performing complete project analysis:[/bold blue] {source_dir}"
    )

    project = Project(source_dir)
    project.scan()

    # Structure analysis
    console.print("\n[bold blue]Project Structure Analysis[/bold blue]")
    project.analyze_structure()

    # Hardware analysis
    if project.hardware_files:
        console.print("\n[bold blue]Hardware Analysis[/bold blue]")
        project.analyze_hardware()

    # Firmware analysis
    if project.firmware_files:
        console.print("\n[bold blue]Firmware Analysis[/bold blue]")
        project.analyze_firmware()

    # Binary files summary
    if project.binary_files:
        console.print("\n[bold blue]Binary Files Summary[/bold blue]")
        for binary_file in project.binary_files[:5]:  # Limit to first 5
            console.print(f"- {binary_file}")

        if len(project.binary_files) > 5:
            console.print(f"  ... and {len(project.binary_files) - 5} more")

        console.print(
            "\nUse 'twinizer analyze binary <file>' to analyze specific binary files."
        )

    # Project statistics
    console.print("\n[bold blue]Project Statistics[/bold blue]")
    project.show_statistics()
