"""
KiCad file conversion utilities.

This module provides functionality to convert KiCad schematic and PCB files to various formats.
"""

import os
import subprocess
from pathlib import Path
from typing import Optional

from rich.console import Console

console = Console()

def convert_kicad_to_image(kicad_file: str, output_path: Optional[str] = None,
                          format: str = 'png', dpi: int = 300) -> str:
    """
    Convert a KiCad schematic or PCB file to an image.

    Args:
        kicad_file: Path to the KiCad file (.sch, .kicad_sch, or .kicad_pcb)
        output_path: Path to save the image, if None uses the same name with the format extension
        format: Output image format (png, jpg, svg, pdf)
        dpi: Resolution for raster outputs

    Returns:
        Path to the output image file
    """
    if not os.path.exists(kicad_file):
        raise FileNotFoundError(f"KiCad file not found: {kicad_file}")

    if output_path is None:
        output_path = os.path.splitext(kicad_file)[0] + f".{format}"

    console.print(f"Converting [cyan]{kicad_file}[/cyan] to [green]{output_path}[/green]")

    # Determine file type
    file_ext = os.path.splitext(kicad_file)[1].lower()

    # Check if KiCad CLI is available
    kicad_cli_available = _check_kicad_cli()

    if kicad_cli_available:
        return _convert_using_kicad_cli(kicad_file, output_path, format, dpi, file_ext)
    else:
        return _convert_using_alternative_method(kicad_file, output_path, format, dpi, file_ext)

def _check_kicad_cli() -> bool:
    """
    Check if KiCad CLI is available.

    Returns:
        Boolean indicating if KiCad CLI is available
    """
    try:
        result = subprocess.run(
            ['kicad-cli', '--version'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=3
        )
        return result.returncode == 0
    except Exception:
        return False

def _convert_using_kicad_cli(kicad_file: str, output_path: str, format: str, dpi: int, file_ext: str) -> str:
    """
    Convert KiCad file using the KiCad CLI.

    Args:
        kicad_file: Path to the KiCad file
        output_path: Path to save the image
        format: Output image format
        dpi: Resolution for raster outputs
        file_ext: File extension of the KiCad file

    Returns:
        Path to the output image file
    """
    try:
        # Determine command based on file type
        if file_ext in ['.sch', '.kicad_sch']:
            cmd = ['kicad-cli', 'sch', 'export', format]
        elif file_ext == '.kicad_pcb':
            cmd = ['kicad-cli', 'pcb', 'export', format]
        else:
            raise ValueError(f"Unsupported file extension: {file_ext}")

        # Add parameters
        cmd.extend(['-o', output_path])

        if format in ['png', 'jpg', 'jpeg']:
            cmd.extend(['--dpi', str(dpi)])

        # Add input file
        cmd.append(kicad_file)

        # Run the command
        console.print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )

        if os.path.exists(output_path):
            console.print(f"[green]Conversion successful:[/green] {output_path}")
            return output_path
        else:
            console.print(f"[yellow]Warning: Output file not found after conversion[/yellow]")
            return ""

    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error during conversion:[/red] {e}")
        console.print(f"Command output: {e.stdout}")
        console.print(f"Command error: {e.stderr}")
        raise
    except Exception as e:
        console.print(f"[red]Error during conversion:[/red] {e}")
        raise

def _convert_using_alternative_method(kicad_file: str, output_path: str, format: str, dpi: int, file_ext: str) -> str:
    """
    Convert KiCad file using alternative methods when KiCad CLI is not available.

    Args:
        kicad_file: Path to the KiCad file
        output_path: Path to save the image
        format: Output image format
        dpi: Resolution for raster outputs
        file_ext: File extension of the KiCad file

    Returns:
        Path to the output image file
    """
    # Check for pcbnew Python module (part of KiCad)
    try:
        import pcbnew
        return _convert_using_pcbnew(kicad_file, output_path, format, dpi, file_ext)
    except ImportError:
        pass

    # Check for eeschema automation
    try:
        return _convert_using_eeschema(kicad_file, output_path, format, dpi, file_ext)
    except Exception:
        pass

    # Fallback method - generate placeholder image with warning
    console.print(f"[yellow]Warning: KiCad CLI not available, generating placeholder image[/yellow]")
    _generate_placeholder_image(kicad_file, output_path, format)

    return output_path

def _convert_using_pcbnew(kicad_file: str, output_path: str, format: str, dpi: int, file_ext: str) -> str:
    """
    Convert PCB file using the pcbnew Python module.

    Args:
        kicad_file: Path to the KiCad file
        output_path: Path to save the image
        format: Output image format
        dpi: Resolution for raster outputs
        file_ext: File extension of the KiCad file

    Returns:
        Path to the output image file
    """
    import pcbnew

    if file_ext != '.kicad_pcb':
        raise ValueError("pcbnew module can only convert PCB files")

    console.print(f"Converting PCB using pcbnew Python module")

    # Load the PCB
    board = pcbnew.LoadBoard(kicad_file)

    # Set up plot controller
    pctl = pcbnew.PLOT_CONTROLLER(board)
    popt = pctl.GetPlotOptions()

    # Set plot options
    popt.SetOutputDirectory(os.path.dirname(output_path))
    popt.SetScale(1)
    popt.SetMirror(False)
    popt.SetUseGerberAttributes(True)
    popt.SetExcludeEdgeLayer(False)
    popt.SetScale(1)
    popt.SetUseAuxOrigin(False)

    # Map format string to plot format
    format_map = {
        'pdf': pcbnew.PLOT_FORMAT_PDF,
        'svg': pcbnew.PLOT_FORMAT_SVG,
        'png': pcbnew.PLOT_FORMAT_PNG,
    }

    if format not in format_map:
        raise ValueError(f"Unsupported format for pcbnew: {format}")

    plot_format = format_map[format]

    # Set DPI for raster formats
    if format == 'png':
        popt.SetDPI(dpi)

    # Plot all copper layers
    plot_plan = [
        (pcbnew.F_Cu, "F.Cu"),
        (pcbnew.B_Cu, "B.Cu"),
    ]

    for layer_id, layer_name in plot_plan:
        pctl.SetLayer(layer_id)
        pctl.OpenPlotfile(layer_name, plot_format, layer_name)
        pctl.PlotLayer()

    # Close the plot controller
    pctl.ClosePlot()

    # The plot controller creates files with names like "F.Cu.pdf"
    # We need to rename the file to match the expected output path
    plot_file = os.path.join(os.path.dirname(output_path), f"F.Cu.{format}")

    if os.path.exists(plot_file):
        import shutil
        shutil.move(plot_file, output_path)
        console.print(f"[green]Conversion successful:[/green] {output_path}")
        return output_path
    else:
        console.print(f"[yellow]Warning: Output file not found after conversion[/yellow]")
        return ""

def _convert_using_eeschema(kicad_file: str, output_path: str, format: str, dpi: int, file_ext: str) -> str:
    """
    Convert schematic file using eeschema command line.

    Args:
        kicad_file: Path to the KiCad file
        output_path: Path to save the image
        format: Output image format
        dpi: Resolution for raster outputs
        file_ext: File extension of the KiCad file

    Returns:
        Path to the output image file
    """
    if file_ext not in ['.sch', '.kicad_sch']:
        raise ValueError("eeschema can only convert schematic files")

    console.print(f"Converting schematic using eeschema command line")

    # Check if eeschema is available
    try:
        subprocess.run(
            ['eeschema', '--version'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=3
        )
    except Exception:
        raise RuntimeError("eeschema command not found")

    # Create a temporary plot script
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as script_file:
        script_path = script_file.name

        script_content = f"""
import sys
import os
import time

output_dir = os.path.dirname(r"{output_path}")
output_format = "{format.upper()}"
output_file = r"{output_path}"

# Wait for eeschema to start
time.sleep(1)

# Import eeschema scripting modules
import eeschema
from scripting import ExportFunctions

# Get the schematic frame
schframe = eeschema.GetSchematicFrame()

# Plot the schematic
plot_controller = ExportFunctions(schframe)
plot_controller.ExportToFormat(output_format, output_dir, False)

# Exit eeschema
eeschema.Exit()
"""
        script_file.write(script_content)

    try:
        # Run eeschema with the script
        cmd = ['eeschema', kicad_file, '--run', script_path]

        console.print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=60  # Longer timeout as eeschema can be slow to start
        )

        # Check if the output file exists
        if os.path.exists(output_path):
            console.print(f"[green]Conversion successful:[/green] {output_path}")
            return output_path
        else:
            # Look for files with similar names that might have been created
            output_dir = os.path.dirname(output_path)
            base_name = os.path.splitext(os.path.basename(kicad_file))[0]

            for file in os.listdir(output_dir):
                if file.startswith(base_name) and file.endswith(f".{format}"):
                    full_path = os.path.join(output_dir, file)
                    os.rename(full_path, output_path)
                    console.print(f"[green]Conversion successful:[/green] {output_path}")
                    return output_path

            console.print(f"[yellow]Warning: Output file not found after conversion[/yellow]")
            return ""

    except Exception as e:
        console.print(f"[red]Error during conversion:[/red] {e}")
        raise
    finally:
        # Clean up the temporary script
        if os.path.exists(script_path):
            os.unlink(script_path)

def _generate_placeholder_image(kicad_file: str, output_path: str, format: str) -> str:
    """
    Generate a placeholder image when conversion is not possible.

    Args:
        kicad_file: Path to the KiCad file
        output_path: Path to save the image
        format: Output image format

    Returns:
        Path to the output image file
    """
    try:
        from PIL import Image, ImageDraw, ImageFont

        # Create a blank image
        width, height = 800, 600
        img = Image.new('RGB', (width, height), color=(255, 255, 255))

        # Create a drawing context
        draw = ImageDraw.Draw(img)

        # Draw a border
        draw.rectangle([(10, 10), (width-10, height-10)], outline=(0, 0, 0), width=2)

        # Add text
        try:
            font = ImageFont.truetype("Arial", 24)
        except IOError:
            font = ImageFont.load_default()

        file_name = os.path.basename(kicad_file)

        draw.text(
            (width//2, height//3),
            f"Placeholder Image for",
            fill=(0, 0, 0),
            font=font,
            anchor="mm"
        )

        draw.text(
            (width//2, height//2),
            file_name,
            fill=(0, 0, 0),
            font=font,
            anchor="mm"
        )

        draw.text(
            (width//2, 2*height//3),
            "KiCad CLI not available for conversion",
            fill=(0, 0, 0),
            font=font,
            anchor="mm"
        )

        # Save the image
        img.save(output_path, format=format.upper())

        console.print(f"[green]Placeholder image generated:[/green] {output_path}")
        return output_path

    except Exception as e:
        console.print(f"[red]Error generating placeholder image:[/red] {e}")
        return ""

def convert_kicad_schematic_to_netlist(schematic_path: str, output_path: Optional[str] = None) -> str:
    """
    Convert a KiCad schematic to a netlist file.

    Args:
        schematic_path: Path to the KiCad schematic file
        output_path: Path to save the netlist, if None uses the same name with .net extension

    Returns:
        Path to the output netlist file
    """
    if not os.path.exists(schematic_path):
        raise FileNotFoundError(f"Schematic file not found: {schematic_path}")

    if output_path is None:
        output_path = os.path.splitext(schematic_path)[0] + ".net"

    console.print(f"Converting [cyan]{schematic_path}[/cyan] to netlist [green]{output_path}[/green]")

    # Check if KiCad CLI is available
    kicad_cli_available = _check_kicad_cli()

    if kicad_cli_available:
        try:
            cmd = ['kicad-cli', 'sch', 'export', 'netlist', '-o', output_path, schematic_path]

            console.print(f"Running: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )

            if os.path.exists(output_path):
                console.print(f"[green]Conversion successful:[/green] {output_path}")
                return output_path
            else:
                console.print(f"[yellow]Warning: Output file not found after conversion[/yellow]")
                return ""

        except subprocess.CalledProcessError as e:
            console.print(f"[red]Error during conversion:[/red] {e}")
            console.print(f"Command output: {e.stdout}")
            console.print(f"Command error: {e.stderr}")
            raise
        except Exception as e:
            console.print(f"[red]Error during conversion:[/red] {e}")
            raise
    else:
        console.print(f"[yellow]Warning: KiCad CLI not available for netlist generation[/yellow]")
        return ""

def convert_kicad_pcb_to_gerber(pcb_path: str, output_dir: Optional[str] = None) -> str:
    """
    Convert a KiCad PCB to Gerber files.

    Args:
        pcb_path: Path to the KiCad PCB file
        output_dir: Directory to save the Gerber files, if None uses the same name as the PCB file

    Returns:
        Path to the output directory containing Gerber files
    """
    if not os.path.exists(pcb_path):
        raise FileNotFoundError(f"PCB file not found: {pcb_path}")

    if output_dir is None:
        output_dir = os.path.splitext(pcb_path)[0] + "_gerber"

    os.makedirs(output_dir, exist_ok=True)

    console.print(f"Converting [cyan]{pcb_path}[/cyan] to Gerber files in [green]{output_dir}[/green]")

    # Check if KiCad CLI is available
    kicad_cli_available = _check_kicad_cli()

    if kicad_cli_available:
        try:
            cmd = ['kicad-cli', 'pcb', 'export', 'gerber', '--output', output_dir, pcb_path]

            console.print(f"Running: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )

            # Check if any Gerber files were created
            gerber_files = [f for f in os.listdir(output_dir) if f.endswith(('.gbr', '.gbl', '.gtl', '.gtp', '.gto', '.gts'))]

            if gerber_files:
                console.print(f"[green]Conversion successful:[/green] Generated {len(gerber_files)} Gerber files in {output_dir}")
                for file in gerber_files:
                    console.print(f"  - {file}")
                return output_dir
            else:
                console.print(f"[yellow]Warning: No Gerber files found after conversion[/yellow]")
                return ""

        except subprocess.CalledProcessError as e:
            console.print(f"[red]Error during conversion:[/red] {e}")
            console.print(f"Command output: {e.stdout}")
            console.print(f"Command error: {e.stderr}")
            raise
        except Exception as e:
            console.print(f"[red]Error during conversion:[/red] {e}")
            raise
    else:
        # Try using pcbnew Python module
        try:
            import pcbnew

            console.print(f"Converting PCB using pcbnew Python module")

            # Load the PCB
            board = pcbnew.LoadBoard(pcb_path)

            # Set up plot controller
            pctl = pcbnew.PLOT_CONTROLLER(board)
            popt = pctl.GetPlotOptions()

            # Set plot options
            popt.SetOutputDirectory(output_dir)
            popt.SetPlotFrameRef(False)
            popt.SetPlotValue(True)
            popt.SetPlotReference(True)
            popt.SetPlotInvisibleText(False)
            popt.SetExcludeEdgeLayer(True)
            popt.SetPlotPadsOnSilkLayer(False)
            popt.SetUseGerberAttributes(True)
            popt.SetUseGerberProtelExtensions(False)
            popt.SetCreateGerberJobFile(True)
            popt.SetSubtractMaskFromSilk(True)
            popt.SetPlotViaOnMaskLayer(False)
            popt.SetExcludeEdgeLayer(True)

            # Plot standard Gerber layers
            plot_plan = [
                (pcbnew.F_Cu, "F.Cu", "Top Layer"),
                (pcbnew.B_Cu, "B.Cu", "Bottom Layer"),
                (pcbnew.F_Paste, "F.Paste", "Top Paste"),
                (pcbnew.B_Paste, "B.Paste", "Bottom Paste"),
                (pcbnew.F_SilkS, "F.SilkS", "Top Silk"),
                (pcbnew.B_SilkS, "B.SilkS", "Bottom Silk"),
                (pcbnew.F_Mask, "F.Mask", "Top Mask"),
                (pcbnew.B_Mask, "B.Mask", "Bottom Mask"),
                (pcbnew.Edge_Cuts, "Edge.Cuts", "Board Outline")
            ]

            for layer_id, layer_name, layer_desc in plot_plan:
                pctl.SetLayer(layer_id)
                pctl.OpenPlotfile(layer_name, pcbnew.PLOT_FORMAT_GERBER, layer_desc)
                pctl.PlotLayer()

            # Close the plot controller
            pctl.ClosePlot()

            # Check if any Gerber files were created
            gerber_files = [f for f in os.listdir(output_dir) if f.endswith(('.gbr', '.gbl', '.gtl', '.gtp', '.gto', '.gts'))]

            if gerber_files:
                console.print(f"[green]Conversion successful:[/green] Generated {len(gerber_files)} Gerber files in {output_dir}")
                for file in gerber_files:
                    console.print(f"  - {file}")
                return output_dir
            else:
                console.print(f"[yellow]Warning: No Gerber files found after conversion[/yellow]")
                return ""

        except ImportError:
            console.print(f"[yellow]Warning: Neither KiCad CLI nor pcbnew module available for Gerber generation[/yellow]")
            return ""
        except Exception as e:
            console.print(f"[red]Error during conversion:[/red] {e}")
            return ""