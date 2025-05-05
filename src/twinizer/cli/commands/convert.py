"""
Convert command for the Twinizer CLI.

This module provides commands for converting between different file formats,
including PDF to Markdown, schematic to image, binary to source code, etc.
"""

import os

import click
from rich.console import Console
from rich.panel import Panel

from twinizer.core.project import Project

console = Console()


@click.group(name="convert")
def convert():
    """
    Convert between file formats.

    This command provides various subcommands for converting between different file formats,
    including PDF to Markdown, schematic to image, binary to source code, etc.
    """
    pass


@convert.command(name="pdf2md")
@click.argument("file", required=True)
@click.option(
    "--output",
    "-o",
    default=None,
    help="Output file path (defaults to same name with .md extension)",
)
@click.option("--ocr/--no-ocr", default=False, help="Enable OCR for text in images")
@click.option(
    "--extract-images/--no-extract-images",
    default=True,
    help="Extract and save images from the PDF",
)
@click.option(
    "--image-format",
    default="png",
    help="Format to save extracted images (png, jpg, etc.)",
)
@click.option(
    "--source-dir", "-d", default=None, help="Source directory (defaults to ./source)"
)
def pdf_to_markdown(file, output, ocr, extract_images, image_format, source_dir):
    """
    Convert PDF to Markdown format.

    This command converts a PDF document to Markdown format, preserving text,
    structure, images, and tables where possible.
    """
    if source_dir is None:
        source_dir = os.environ.get("TWINIZER_SOURCE_DIR", "./source")

    file_path = os.path.join(source_dir, file)
    if not os.path.exists(file_path):
        console.print(f"[bold red]Error:[/bold red] File not found: {file}")
        return

    if output is None:
        output = os.path.splitext(file_path)[0] + ".md"

    console.print(f"[bold blue]Converting PDF to Markdown:[/bold blue] {file}")

    from twinizer.converters.pdf2md import convert_pdf_to_markdown

    # Set up conversion options
    options = {
        "ocr_enabled": ocr,
        "extract_images": extract_images,
        "image_format": image_format,
    }

    try:
        output_path = convert_pdf_to_markdown(file_path, output, **options)
        console.print(f"[bold green]Conversion successful:[/bold green] {output_path}")
    except Exception as e:
        console.print(f"[bold red]Error during conversion:[/bold red] {str(e)}")


@convert.command(name="sch2img")
@click.argument("file", required=True)
@click.option(
    "--output",
    "-o",
    default=None,
    help="Output file path (defaults to same name with image extension)",
)
@click.option(
    "--format", "-f", default="png", help="Output image format (png, jpg, svg, pdf)"
)
@click.option("--dpi", default=300, help="Resolution for raster outputs (DPI)")
@click.option(
    "--source-dir", "-d", default=None, help="Source directory (defaults to ./source)"
)
def schematic_to_image(file, output, format, dpi, source_dir):
    """
    Convert schematic file to image.

    This command converts a schematic file (.sch, .kicad_sch, etc.) to an image format.
    """
    if source_dir is None:
        source_dir = os.environ.get("TWINIZER_SOURCE_DIR", "./source")

    file_path = os.path.join(source_dir, file)
    if not os.path.exists(file_path):
        console.print(f"[bold red]Error:[/bold red] File not found: {file}")
        return

    if output is None:
        output = os.path.splitext(file_path)[0] + f".{format}"

    console.print(f"[bold blue]Converting schematic to image:[/bold blue] {file}")

    # Check file extension to use appropriate converter
    if file.endswith((".sch", ".kicad_sch", ".kicad_pcb")):
        from twinizer.hardware.kicad import convert_kicad_to_image

        try:
            output_path = convert_kicad_to_image(file_path, output, format, dpi)
            console.print(
                f"[bold green]Conversion successful:[/bold green] {output_path}"
            )
        except Exception as e:
            console.print(f"[bold red]Error during conversion:[/bold red] {str(e)}")
    elif file.endswith((".SchDoc", ".PcbDoc")):
        console.print(
            Panel(
                "Altium files (.SchDoc, .PcbDoc) conversion is not fully implemented yet.",
                title="Altium Conversion",
                border_style="yellow",
            )
        )
    else:
        console.print(
            f"[bold yellow]Warning:[/bold yellow] Unsupported schematic file format: {file}"
        )


@convert.command(name="bin2source")
@click.argument("file", required=True)
@click.option(
    "--output",
    "-o",
    default=None,
    help="Output file path (defaults to same name with appropriate extension)",
)
@click.option(
    "--language", "-l", default=None, help="Target language (c, python, etc.)"
)
@click.option(
    "--source-dir", "-d", default=None, help="Source directory (defaults to ./source)"
)
def binary_to_source(file, output, language, source_dir):
    """
    Convert binary file to source code.

    This command attempts to decompile or disassemble a binary file to source code.
    """
    if source_dir is None:
        source_dir = os.environ.get("TWINIZER_SOURCE_DIR", "./source")

    file_path = os.path.join(source_dir, file)
    if not os.path.exists(file_path):
        console.print(f"[bold red]Error:[/bold red] File not found: {file}")
        return

    # Determine target language based on file extension if not specified
    if language is None:
        if file.endswith(".pyc"):
            language = "python"
        elif file.endswith((".so", ".dll")):
            language = "c"
        elif file.endswith(".class"):
            language = "java"
        elif file.endswith(".exe"):
            language = "c"
        elif file.endswith((".bin", ".hex", ".elf")):
            language = "asm"
        else:
            language = "c"  # Default to C

    # Determine output path
    if output is None:
        ext_map = {
            "python": ".py",
            "c": ".c",
            "java": ".java",
            "asm": ".asm",
        }
        ext = ext_map.get(language, ".c")
        output = os.path.splitext(file_path)[0] + ext

    console.print(
        f"[bold blue]Converting binary to {language} source code:[/bold blue] {file}"
    )

    # Choose the appropriate converter based on file type and target language
    if file.endswith(".pyc"):
        from twinizer.software.decompile.pyc import decompile_pyc

        try:
            output_path = decompile_pyc(file_path, output)
            console.print(
                f"[bold green]Decompilation successful:[/bold green] {output_path}"
            )
        except Exception as e:
            console.print(f"[bold red]Error during decompilation:[/bold red] {str(e)}")
    elif file.endswith(".so") or file.endswith(".dll"):
        from twinizer.software.decompile.so import create_python_bindings

        try:
            output_path = create_python_bindings(file_path, output)
            console.print(
                f"[bold green]Bindings generation successful:[/bold green] {output_path}"
            )
        except Exception as e:
            console.print(f"[bold red]Error generating bindings:[/bold red] {str(e)}")
    elif file.endswith((".elf", ".bin", ".hex", ".exe")):
        from twinizer.software.decompile.elf import decompile_binary

        try:
            output_path = decompile_binary(file_path, output, language)
            console.print(
                f"[bold green]Decompilation successful:[/bold green] {output_path}"
            )
        except Exception as e:
            console.print(f"[bold red]Error during decompilation:[/bold red] {str(e)}")
    else:
        console.print(
            f"[bold yellow]Warning:[/bold yellow] Unsupported binary file format: {file}"
        )


@convert.command(name="image2ascii")
@click.argument("file", required=True)
@click.option(
    "--output",
    "-o",
    default=None,
    help="Output file path (defaults to same name with .txt extension)",
)
@click.option("--width", default=80, help="Width of the ASCII art in characters")
@click.option(
    "--source-dir", "-d", default=None, help="Source directory (defaults to ./source)"
)
def image_to_ascii(file, output, width, source_dir):
    """
    Convert image to ASCII art.

    This command converts an image file to ASCII art representation.
    """
    if source_dir is None:
        source_dir = os.environ.get("TWINIZER_SOURCE_DIR", "./source")

    file_path = os.path.join(source_dir, file)
    if not os.path.exists(file_path):
        console.print(f"[bold red]Error:[/bold red] File not found: {file}")
        return

    if output is None:
        output = os.path.splitext(file_path)[0] + ".txt"

    console.print(f"[bold blue]Converting image to ASCII art:[/bold blue] {file}")

    from twinizer.converters.image.ascii import convert_image_to_ascii

    try:
        output_path = convert_image_to_ascii(file_path, output, width=width)
        console.print(f"[bold green]Conversion successful:[/bold green] {output_path}")

        # Display preview
        with open(output_path, "r") as f:
            ascii_art = f.read()

        if len(ascii_art.splitlines()) > 20:
            # Show only the first 20 lines if the ASCII art is large
            preview = "\n".join(ascii_art.splitlines()[:20]) + "\n..."
        else:
            preview = ascii_art

        console.print(Panel(preview, title="ASCII Art Preview", border_style="green"))

    except Exception as e:
        console.print(f"[bold red]Error during conversion:[/bold red] {str(e)}")


@convert.command(name="doc2tree")
@click.argument("file", required=True)
@click.option(
    "--output",
    "-o",
    default=None,
    help="Output file path (defaults to same name with _tree.md extension)",
)
@click.option(
    "--source-dir", "-d", default=None, help="Source directory (defaults to ./source)"
)
def doc_to_tree(file, output, source_dir):
    """
    Convert documentation to tree structure.

    This command analyzes a documentation file (MD, TXT, etc.) and converts it
    to a tree structure representation.
    """
    if source_dir is None:
        source_dir = os.environ.get("TWINIZER_SOURCE_DIR", "./source")

    file_path = os.path.join(source_dir, file)
    if not os.path.exists(file_path):
        console.print(f"[bold red]Error:[/bold red] File not found: {file}")
        return

    if output is None:
        output = os.path.splitext(file_path)[0] + "_tree.md"

    console.print(
        f"[bold blue]Converting documentation to tree structure:[/bold blue] {file}"
    )

    # Determine file type
    if file.endswith((".md", ".markdown")):
        from twinizer.converters.doc2tree.markdown import extract_structure
    elif file.endswith(".txt"):
        from twinizer.converters.doc2tree.text import extract_structure
    elif file.endswith((".pdf")):
        from twinizer.converters.doc2tree.pdf import extract_structure
    else:
        console.print(
            f"[bold yellow]Warning:[/bold yellow] Unsupported documentation file format: {file}"
        )
        return

    try:
        output_path = extract_structure(file_path, output)
        console.print(f"[bold green]Conversion successful:[/bold green] {output_path}")
    except Exception as e:
        console.print(f"[bold red]Error during conversion:[/bold red] {str(e)}")


@convert.command(name="netlist")
@click.argument("file", required=True)
@click.option(
    "--output",
    "-o",
    default=None,
    help="Output file path (defaults to same name with .net extension)",
)
@click.option(
    "--source-dir", "-d", default=None, help="Source directory (defaults to ./source)"
)
def schematic_to_netlist(file, output, source_dir):
    """
    Convert schematic to netlist.

    This command converts a schematic file to a netlist file, which can be used
    for various analysis and simulation purposes.
    """
    if source_dir is None:
        source_dir = os.environ.get("TWINIZER_SOURCE_DIR", "./source")

    file_path = os.path.join(source_dir, file)
    if not os.path.exists(file_path):
        console.print(f"[bold red]Error:[/bold red] File not found: {file}")
        return

    if output is None:
        output = os.path.splitext(file_path)[0] + ".net"

    console.print(f"[bold blue]Converting schematic to netlist:[/bold blue] {file}")

    # Check file extension to use appropriate converter
    if file.endswith((".sch", ".kicad_sch")):
        from twinizer.hardware.kicad.converters import (
            convert_kicad_schematic_to_netlist,
        )

        try:
            output_path = convert_kicad_schematic_to_netlist(file_path, output)
            console.print(
                f"[bold green]Conversion successful:[/bold green] {output_path}"
            )
        except Exception as e:
            console.print(f"[bold red]Error during conversion:[/bold red] {str(e)}")
    elif file.endswith(".SchDoc"):
        console.print(
            Panel(
                "Altium schematic to netlist conversion is not fully implemented yet.",
                title="Altium Conversion",
                border_style="yellow",
            )
        )
    else:
        console.print(
            f"[bold yellow]Warning:[/bold yellow] Unsupported schematic file format: {file}"
        )


@convert.command(name="gerber")
@click.argument("file", required=True)
@click.option(
    "--output-dir",
    "-o",
    default=None,
    help="Output directory (defaults to same name as PCB file with _gerber suffix)",
)
@click.option(
    "--source-dir", "-d", default=None, help="Source directory (defaults to ./source)"
)
def pcb_to_gerber(file, output_dir, source_dir):
    """
    Convert PCB file to Gerber files.

    This command converts a PCB layout file to Gerber files, which can be used
    for manufacturing.
    """
    if source_dir is None:
        source_dir = os.environ.get("TWINIZER_SOURCE_DIR", "./source")

    file_path = os.path.join(source_dir, file)
    if not os.path.exists(file_path):
        console.print(f"[bold red]Error:[/bold red] File not found: {file}")
        return

    if output_dir is None:
        output_dir = os.path.splitext(file_path)[0] + "_gerber"

    console.print(f"[bold blue]Converting PCB to Gerber files:[/bold blue] {file}")

    # Check file extension to use appropriate converter
    if file.endswith(".kicad_pcb"):
        from twinizer.hardware.kicad.converters import convert_kicad_pcb_to_gerber

        try:
            output_path = convert_kicad_pcb_to_gerber(file_path, output_dir)
            console.print(
                f"[bold green]Conversion successful:[/bold green] {output_path}"
            )
        except Exception as e:
            console.print(f"[bold red]Error during conversion:[/bold red] {str(e)}")
    elif file.endswith(".PcbDoc"):
        console.print(
            Panel(
                "Altium PCB to Gerber conversion is not fully implemented yet.",
                title="Altium Conversion",
                border_style="yellow",
            )
        )
    else:
        console.print(
            f"[bold yellow]Warning:[/bold yellow] Unsupported PCB file format: {file}"
        )
