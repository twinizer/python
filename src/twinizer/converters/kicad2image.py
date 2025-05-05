"""
KiCad to image converter module.

This module provides functionality to convert KiCad files to various formats
using the docker-kicad.sh script from the docker/ready-image project.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from rich.console import Console

console = Console()

# Path to the docker-kicad.sh script
DOCKER_KICAD_SCRIPT = os.path.join(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    ),
    "docker",
    "ready-image",
    "docker-kicad.sh",
)


def convert_kicad_file(
    input_file: str,
    output_format: str = "svg",
    output_path: Optional[str] = None,
    color_theme: str = "light",
    paper_size: str = "A4",
    orientation: str = "portrait",
    debug: bool = False,
    verbose: bool = False,
) -> str:
    """
    Convert a KiCad file to the specified format using the docker-kicad.sh script.

    Args:
        input_file: Path to the KiCad file (.sch, .kicad_sch, .kicad_pcb)
        output_format: Output format (svg, png, pdf, dxf, hpgl, ps, eps)
        output_path: Path to save the output file, if None uses the same name with the format extension
        color_theme: Color theme for PDF output (light, dark)
        paper_size: Paper size for PDF output (A4, A3, etc.)
        orientation: Page orientation for PDF output (portrait, landscape)
        debug: Enable debug mode to analyze the project
        verbose: Enable verbose output

    Returns:
        Path to the output file
    """
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"KiCad file not found: {input_file}")

    # Check if docker-kicad.sh script exists
    if not os.path.exists(DOCKER_KICAD_SCRIPT):
        raise FileNotFoundError(
            f"docker-kicad.sh script not found at {DOCKER_KICAD_SCRIPT}"
        )

    # Determine output path if not provided
    if output_path is None:
        output_path = os.path.splitext(input_file)[0] + f".{output_format}"

    # Build command arguments
    cmd = [DOCKER_KICAD_SCRIPT]

    # Add input file
    cmd.extend(["-i", input_file])

    # Add output format
    cmd.extend(["-f", output_format])

    # Add output path
    cmd.extend(["-o", output_path])

    # Add color theme for PDF
    if output_format.lower() == "pdf":
        cmd.extend(["-c", color_theme])
        cmd.extend(["-p", paper_size])
        cmd.extend(["-r", orientation])

    # Add debug flag if requested
    if debug:
        cmd.append("-d")

    # Add verbose flag if requested
    if verbose:
        cmd.append("-v")

    console.print(
        f"Converting [cyan]{input_file}[/cyan] to [green]{output_format}[/green] format"
    )

    try:
        # Run the command
        result = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
        )

        if verbose:
            console.print(result.stdout)

        # Check if output file was created
        if not os.path.exists(output_path):
            console.print(
                f"[yellow]Warning: Output file not found at {output_path}[/yellow]"
            )
            console.print(f"[yellow]Command output: {result.stdout}[/yellow]")
            console.print(f"[red]Command error: {result.stderr}[/red]")
            return None

        return output_path

    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error running docker-kicad.sh: {e}[/red]")
        console.print(f"[red]Command error: {e.stderr}[/red]")
        return None


def analyze_kicad_project(
    project_dir: str,
    output_format: str = "json",
    output_path: Optional[str] = None,
    verbose: bool = False,
) -> Union[str, Dict[str, Any]]:
    """
    Analyze a KiCad project for missing dependencies using the docker-kicad.sh script.

    Args:
        project_dir: Path to the KiCad project directory
        output_format: Output format (json, html)
        output_path: Path to save the output file, if None uses a temporary file
        verbose: Enable verbose output

    Returns:
        If output_format is 'json': Dictionary containing the analysis results
        If output_format is 'html': Path to the HTML report file
    """
    if not os.path.exists(project_dir):
        raise FileNotFoundError(f"KiCad project directory not found: {project_dir}")

    # Check if docker-kicad.sh script exists
    if not os.path.exists(DOCKER_KICAD_SCRIPT):
        raise FileNotFoundError(
            f"docker-kicad.sh script not found at {DOCKER_KICAD_SCRIPT}"
        )

    # Determine output path if not provided
    if output_path is None:
        if output_format.lower() == "html":
            # Create a temporary file for HTML output
            fd, output_path = tempfile.mkstemp(suffix=".html")
            os.close(fd)
        else:
            # Create a temporary file for JSON output
            fd, output_path = tempfile.mkstemp(suffix=".json")
            os.close(fd)

    # Build command arguments
    cmd = [DOCKER_KICAD_SCRIPT, "-d"]

    # Add project directory
    cmd.extend(["-i", project_dir])

    # Add output format
    cmd.extend(["-f", output_format])

    # Add output path
    cmd.extend(["-o", output_path])

    # Add verbose flag if requested
    if verbose:
        cmd.append("-v")

    console.print(f"Analyzing KiCad project in [cyan]{project_dir}[/cyan]")

    try:
        # Run the command
        result = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
        )

        if verbose:
            console.print(result.stdout)

        # Check if output file was created
        if not os.path.exists(output_path):
            console.print(
                f"[yellow]Warning: Output file not found at {output_path}[/yellow]"
            )
            console.print(f"[yellow]Command output: {result.stdout}[/yellow]")
            console.print(f"[red]Command error: {result.stderr}[/red]")
            return None

        # If JSON output, parse and return the data
        if output_format.lower() == "json":
            with open(output_path, "r") as f:
                data = json.load(f)
            return data

        # If HTML output, return the path to the file
        return output_path

    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error running docker-kicad.sh: {e}[/red]")
        console.print(f"[red]Command error: {e.stderr}[/red]")
        return None


def list_supported_formats() -> List[Dict[str, str]]:
    """
    List all supported output formats for KiCad file conversion.

    Returns:
        List of dictionaries containing format information
    """
    return [
        {"format": "svg", "description": "Scalable Vector Graphics", "default": True},
        {"format": "png", "description": "Portable Network Graphics"},
        {
            "format": "pdf",
            "description": "Portable Document Format",
            "options": ["color_theme", "paper_size", "orientation"],
        },
        {"format": "dxf", "description": "Drawing Exchange Format"},
        {"format": "hpgl", "description": "HP Graphics Language"},
        {"format": "ps", "description": "PostScript"},
        {"format": "eps", "description": "Encapsulated PostScript"},
    ]


def is_kicad_file(file_path: str) -> bool:
    """
    Check if a file is a KiCad file.

    Args:
        file_path: Path to the file

    Returns:
        Boolean indicating if the file is a KiCad file
    """
    if not os.path.exists(file_path):
        return False

    # Check file extension
    ext = os.path.splitext(file_path)[1].lower()
    return ext in [".sch", ".kicad_sch", ".kicad_pcb", ".kicad_pro"]
