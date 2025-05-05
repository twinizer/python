"""
Image conversion command module.

This module provides CLI commands for image conversion operations,
including ASCII art, Mermaid diagrams, and 3D model generation.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax

from twinizer.converters.image.ascii import AsciiArtConverter
from twinizer.converters.image.mermaid import MermaidDiagramGenerator


# Używamy importów warunkowych dla modułów, które wymagają matplotlib
# aby uniknąć błędów, gdy matplotlib nie jest zainstalowany
def _import_image_to_3d():
    try:
        from twinizer.converters.image.image_to_3d import (
            ImageTo3DConverter,
            image_to_heightmap,
            image_to_mesh,
            image_to_normalmap,
            image_to_point_cloud,
        )

        return (
            ImageTo3DConverter,
            image_to_heightmap,
            image_to_normalmap,
            image_to_mesh,
            image_to_point_cloud,
        )
    except ImportError:
        return None, None, None, None, None


console = Console()


@click.group(name="image", help="Commands for image conversion and processing")
def image_group():
    """Image conversion command group."""
    pass


@image_group.command(name="to-ascii", help="Convert image to ASCII art")
@click.argument("image_path", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option(
    "--width", "-w", type=int, default=80, help="Width of ASCII art in characters"
)
@click.option("--height", "-h", type=int, help="Height of ASCII art in characters")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["text", "html", "ansi"]),
    default="text",
    help="Output format",
)
@click.option(
    "--charset",
    "-c",
    type=click.Choice(["standard", "simple", "blocks", "extended"]),
    default="standard",
    help="Character set to use",
)
@click.option("--invert", "-i", is_flag=True, help="Invert brightness")
def image_to_ascii(
    image_path: str,
    output: Optional[str] = None,
    width: int = 80,
    height: Optional[int] = None,
    format: str = "text",
    charset: str = "standard",
    invert: bool = False,
):
    """
    Convert an image to ASCII art.

    Args:
        image_path: Path to the input image
        output: Output file path (optional)
        width: Width of ASCII art in characters
        height: Height of ASCII art in characters (optional)
        format: Output format (text, html, or ansi)
        charset: Character set to use
        invert: Invert brightness
    """
    try:
        # Create converter
        converter = AsciiArtConverter()

        # Convert image to ASCII art
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(
                "[green]Converting image to ASCII art...", total=None
            )

            result = converter.convert(
                image_path=image_path,
                width=width,
                height=height,
                output_format=format,
                charset=charset,
                invert=invert,
                output_path=output,
            )

            progress.update(
                task, completed=True, description=f"[green]Conversion complete"
            )

        # Display result
        if output:
            console.print(f"[green]ASCII art saved to: {output}[/green]")
        else:
            if format == "html":
                console.print("[yellow]HTML output:[/yellow]")
                console.print(result)
            elif format == "ansi":
                console.print(result)
            else:
                syntax = Syntax(result, "text", theme="monokai")
                console.print(syntax)

    except Exception as e:
        console.print(f"[red]Error converting image to ASCII art: {e}[/red]")
        import traceback

        console.print(traceback.format_exc())
        sys.exit(1)


@image_group.command(name="to-mermaid", help="Convert image to Mermaid diagram")
@click.argument("image_path", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option(
    "--diagram-type",
    "-t",
    type=click.Choice(["flowchart", "sequence", "class", "entity", "state"]),
    default="flowchart",
    help="Type of diagram to generate",
)
@click.option(
    "--threshold", type=float, default=128, help="Threshold for edge detection (0-255)"
)
@click.option(
    "--simplify", type=float, default=0.05, help="Simplification factor (0-1)"
)
@click.option(
    "--direction",
    type=click.Choice(["TB", "BT", "LR", "RL"]),
    default="TB",
    help="Direction for flowchart",
)
def image_to_mermaid(
    image_path: str,
    output: Optional[str] = None,
    diagram_type: str = "flowchart",
    threshold: float = 128,
    simplify: float = 0.05,
    direction: str = "TB",
):
    """
    Convert an image to a Mermaid diagram.

    Args:
        image_path: Path to the input image
        output: Output file path (optional)
        diagram_type: Type of diagram to generate
        threshold: Threshold for edge detection (0-255)
        simplify: Simplification factor (0-1)
        direction: Direction for flowchart
    """
    try:
        # Create generator
        generator = MermaidDiagramGenerator()

        # Convert image to Mermaid diagram
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(
                "[green]Converting image to Mermaid diagram...", total=None
            )

            if diagram_type == "flowchart":
                result = generator.image_to_flowchart(
                    image_path=image_path,
                    threshold=threshold,
                    simplify=simplify,
                    direction=direction,
                )
            elif diagram_type == "sequence":
                result = generator.image_to_sequence(
                    image_path=image_path, threshold=threshold, simplify=simplify
                )
            elif diagram_type == "class":
                result = generator.image_to_class(
                    image_path=image_path, threshold=threshold, simplify=simplify
                )
            elif diagram_type == "entity":
                result = generator.image_to_entity(
                    image_path=image_path, threshold=threshold, simplify=simplify
                )
            elif diagram_type == "state":
                result = generator.image_to_state(
                    image_path=image_path, threshold=threshold, simplify=simplify
                )

            progress.update(
                task, completed=True, description=f"[green]Conversion complete"
            )

        # Save to file if output path is provided
        if output:
            with open(output, "w") as f:
                f.write(result)
            console.print(f"[green]Mermaid diagram saved to: {output}[/green]")
        else:
            syntax = Syntax(result, "mermaid", theme="monokai", line_numbers=True)
            console.print(syntax)

    except Exception as e:
        console.print(f"[red]Error converting image to Mermaid diagram: {e}[/red]")
        import traceback

        console.print(traceback.format_exc())
        sys.exit(1)


@image_group.command(name="to-heightmap", help="Convert image to height map")
@click.argument("image_path", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--invert", "-i", is_flag=True, help="Invert height values")
@click.option(
    "--blur", "-b", type=float, default=0.0, help="Apply Gaussian blur (sigma value)"
)
@click.option("--normalize", "-n", is_flag=True, help="Normalize height values")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["png", "jpg", "tiff"]),
    default="png",
    help="Output format",
)
def image_to_heightmap_cmd(
    image_path: str,
    output: Optional[str] = None,
    invert: bool = False,
    blur: float = 0.0,
    normalize: bool = False,
    format: str = "png",
):
    """
    Convert an image to a height map.

    This command takes an input image and generates a height map where pixel intensity
    corresponds to height.
    """
    try:
        # Lazy import
        _, image_to_heightmap_func, _, _, _ = _import_image_to_3d()
        if image_to_heightmap_func is None:
            console.print(
                "[red]Error:[/red] Required dependency 'matplotlib' is not installed."
            )
            console.print(
                "Please install it with: [green]pip install matplotlib[/green]"
            )
            return

        # Set output path if not provided
        if not output:
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            output = f"{base_name}_heightmap.{format}"

        # Show progress
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(
                "[green]Converting image to height map...", total=None
            )

            result = image_to_heightmap_func(
                image_path=image_path,
                invert=invert,
                blur_sigma=blur,
                normalize=normalize,
                output_path=output,
            )

            progress.update(task, completed=True)

        console.print(f"[green]Height map generated:[/green] {output}")

    except Exception as e:
        console.print(f"[red]Error generating height map:[/red] {str(e)}")


@image_group.command(name="to-normalmap", help="Convert image to normal map")
@click.argument("image_path", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option(
    "--strength", "-s", type=float, default=1.0, help="Strength of normal map effect"
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["png", "jpg", "tiff"]),
    default="png",
    help="Output format",
)
def image_to_normalmap_cmd(
    image_path: str,
    output: Optional[str] = None,
    strength: float = 1.0,
    format: str = "png",
):
    """
    Convert an image to a normal map.

    This command takes an input image (typically a height map) and generates a normal map
    for use in 3D rendering and games.
    """
    try:
        # Lazy import
        _, _, image_to_normalmap_func, _, _ = _import_image_to_3d()
        if image_to_normalmap_func is None:
            console.print(
                "[red]Error:[/red] Required dependency 'matplotlib' is not installed."
            )
            console.print(
                "Please install it with: [green]pip install matplotlib[/green]"
            )
            return

        # Set output path if not provided
        if not output:
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            output = f"{base_name}_normalmap.{format}"

        # Show progress
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(
                "[green]Converting image to normal map...", total=None
            )

            result = image_to_normalmap_func(
                image_path=image_path, strength=strength, output_path=output
            )

            progress.update(task, completed=True)

        console.print(f"[green]Normal map generated:[/green] {output}")

    except Exception as e:
        console.print(f"[red]Error generating normal map:[/red] {str(e)}")


@image_group.command(name="to-mesh", help="Convert image to 3D mesh")
@click.argument("image_path", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["obj", "stl", "ply", "glb"]),
    default="obj",
    help="Output format",
)
@click.option(
    "--scale-z", "-z", type=float, default=1.0, help="Scale factor for Z axis"
)
@click.option("--invert", "-i", is_flag=True, help="Invert height values")
@click.option("--smooth/--no-smooth", default=True, help="Apply smoothing to the mesh")
@click.option(
    "--resolution",
    "-r",
    type=int,
    default=100,
    help="Resolution of the mesh (percentage of image resolution)",
)
def image_to_mesh_cmd(
    image_path: str,
    output: Optional[str] = None,
    format: str = "obj",
    scale_z: float = 1.0,
    invert: bool = False,
    smooth: bool = True,
    resolution: int = 100,
):
    """
    Convert an image to a 3D mesh.

    This command takes an input image (typically a height map) and generates a 3D mesh
    where pixel intensity corresponds to height.
    """
    try:
        # Lazy import
        _, _, _, image_to_mesh_func, _ = _import_image_to_3d()
        if image_to_mesh_func is None:
            console.print(
                "[red]Error:[/red] Required dependency 'matplotlib' is not installed."
            )
            console.print(
                "Please install it with: [green]pip install matplotlib[/green]"
            )
            return

        # Set output path if not provided
        if not output:
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            output = f"{base_name}_mesh.{format}"

        # Show progress
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(
                "[green]Converting image to 3D mesh...", total=None
            )

            result = image_to_mesh_func(
                image_path=image_path,
                scale_z=scale_z,
                invert=invert,
                smooth=smooth,
                resolution=resolution,
                output_format=format,
                output_path=output,
            )

            progress.update(task, completed=True)

        console.print(f"[green]3D mesh generated:[/green] {output}")

    except Exception as e:
        console.print(f"[red]Error generating 3D mesh:[/red] {str(e)}")


@image_group.command(name="to-pointcloud", help="Convert image to 3D point cloud")
@click.argument("image_path", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["ply", "xyz", "pcd"]),
    default="ply",
    help="Output format",
)
@click.option(
    "--scale-z", "-z", type=float, default=1.0, help="Scale factor for Z axis"
)
@click.option("--invert", "-i", is_flag=True, help="Invert height values")
@click.option(
    "--sample-ratio",
    "-s",
    type=float,
    default=1.0,
    help="Sampling ratio (percentage of pixels to include)",
)
@click.option("--color/--no-color", default=True, help="Include color information")
def image_to_pointcloud_cmd(
    image_path: str,
    output: Optional[str] = None,
    format: str = "ply",
    scale_z: float = 1.0,
    invert: bool = False,
    sample_ratio: float = 1.0,
    color: bool = True,
):
    """
    Convert an image to a 3D point cloud.

    This command takes an input image (typically a height map) and generates a 3D point cloud
    where pixel intensity corresponds to height.
    """
    try:
        # Lazy import
        _, _, _, _, image_to_point_cloud_func = _import_image_to_3d()
        if image_to_point_cloud_func is None:
            console.print(
                "[red]Error:[/red] Required dependency 'matplotlib' is not installed."
            )
            console.print(
                "Please install it with: [green]pip install matplotlib[/green]"
            )
            return

        # Set output path if not provided
        if not output:
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            output = f"{base_name}_pointcloud.{format}"

        # Show progress
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(
                "[green]Converting image to 3D point cloud...", total=None
            )

            result = image_to_point_cloud_func(
                image_path=image_path,
                scale_z=scale_z,
                sample_ratio=sample_ratio,
                invert=invert,
                include_color=color,
                output_format=format,
                output_path=output,
            )

            progress.update(task, completed=True)

        console.print(f"[green]3D point cloud generated:[/green] {output}")

    except Exception as e:
        console.print(f"[red]Error generating 3D point cloud:[/red] {str(e)}")
