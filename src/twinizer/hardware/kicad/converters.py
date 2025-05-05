"""
KiCad file conversion utilities.

This module provides functionality to convert KiCad schematic and PCB files to various formats.
"""

import datetime
import json
import logging
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from rich.console import Console

console = Console()

# Import schemdraw dla konwersji do SVG
try:
    import schemdraw
    from schemdraw import elements as elm

    SCHEMDRAW_AVAILABLE = True
except ImportError:
    SCHEMDRAW_AVAILABLE = False


def convert_kicad_to_image(
    kicad_file: str,
    output_path: Optional[str] = None,
    format: str = "png",
    dpi: int = 300,
) -> str:
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

    console.print(
        f"Converting [cyan]{kicad_file}[/cyan] to [green]{output_path}[/green]"
    )

    # Determine file type
    file_ext = os.path.splitext(kicad_file)[1].lower()

    # Check if KiCad CLI is available
    kicad_cli_available = _check_kicad_cli()

    if kicad_cli_available:
        return _convert_using_kicad_cli(kicad_file, output_path, format, dpi, file_ext)
    else:
        return _convert_using_alternative_method(
            kicad_file, output_path, format, dpi, file_ext
        )


def _check_kicad_cli() -> bool:
    """
    Check if KiCad CLI is available.

    Returns:
        Boolean indicating if KiCad CLI is available
    """
    try:
        result = subprocess.run(
            ["kicad-cli", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=3,
        )
        return result.returncode == 0
    except Exception:
        return False


def _convert_using_kicad_cli(
    kicad_file: str, output_path: str, format: str, dpi: int, file_ext: str
) -> str:
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
        if file_ext in [".sch", ".kicad_sch"]:
            cmd = ["kicad-cli", "sch", "export", format]
        elif file_ext == ".kicad_pcb":
            cmd = ["kicad-cli", "pcb", "export", format]
        else:
            raise ValueError(f"Unsupported file extension: {file_ext}")

        # Add parameters
        cmd.extend(["-o", output_path])

        if format in ["png", "jpg", "jpeg"]:
            cmd.extend(["--dpi", str(dpi)])

        # Add input file
        cmd.append(kicad_file)

        # Run the command
        console.print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
        )

        if os.path.exists(output_path):
            console.print(f"[green]Conversion successful:[/green] {output_path}")
            return output_path
        else:
            console.print(
                f"[yellow]Warning: Output file not found after conversion[/yellow]"
            )
            return ""

    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error during conversion:[/red] {e}")
        console.print(f"Command output: {e.stdout}")
        console.print(f"Command error: {e.stderr}")
        raise
    except Exception as e:
        console.print(f"[red]Error during conversion:[/red] {e}")
        raise


def _convert_using_alternative_method(
    kicad_file: str, output_path: str, format: str, dpi: int, file_ext: str
) -> str:
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
    console.print(
        f"[yellow]Warning: KiCad CLI not available, generating placeholder image[/yellow]"
    )
    _generate_placeholder_image(kicad_file, output_path, format)

    return output_path


def _convert_using_pcbnew(
    kicad_file: str, output_path: str, format: str, dpi: int, file_ext: str
) -> str:
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

    if file_ext != ".kicad_pcb":
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
        "pdf": pcbnew.PLOT_FORMAT_PDF,
        "svg": pcbnew.PLOT_FORMAT_SVG,
        "png": pcbnew.PLOT_FORMAT_PNG,
    }

    if format not in format_map:
        raise ValueError(f"Unsupported format for pcbnew: {format}")

    plot_format = format_map[format]

    # Set DPI for raster formats
    if format == "png":
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
        console.print(
            f"[yellow]Warning: Output file not found after conversion[/yellow]"
        )
        return ""


def _convert_using_eeschema(
    kicad_file: str, output_path: str, format: str, dpi: int, file_ext: str
) -> str:
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
    if file_ext not in [".sch", ".kicad_sch"]:
        raise ValueError("eeschema can only convert schematic files")

    console.print(f"Converting schematic using eeschema command line")

    # Check if eeschema is available
    try:
        subprocess.run(
            ["eeschema", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=3,
        )
    except Exception:
        raise RuntimeError("eeschema command not found")

    # Create a temporary plot script
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False
    ) as script_file:
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
        cmd = ["eeschema", kicad_file, "--run", script_path]

        console.print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=60,  # Longer timeout as eeschema can be slow to start
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
                    console.print(
                        f"[green]Conversion successful:[/green] {output_path}"
                    )
                    return output_path

            console.print(
                f"[yellow]Warning: Output file not found after conversion[/yellow]"
            )
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
        img = Image.new("RGB", (width, height), color=(255, 255, 255))

        # Create a drawing context
        draw = ImageDraw.Draw(img)

        # Draw a border
        draw.rectangle(
            [(10, 10), (width - 10, height - 10)], outline=(0, 0, 0), width=2
        )

        # Add text
        try:
            font = ImageFont.truetype("Arial", 24)
        except IOError:
            font = ImageFont.load_default()

        file_name = os.path.basename(kicad_file)

        draw.text(
            (width // 2, height // 3),
            f"Placeholder Image for",
            fill=(0, 0, 0),
            font=font,
            anchor="mm",
        )

        draw.text(
            (width // 2, height // 2), file_name, fill=(0, 0, 0), font=font, anchor="mm"
        )

        draw.text(
            (width // 2, 2 * height // 3),
            "KiCad CLI not available for conversion",
            fill=(0, 0, 0),
            font=font,
            anchor="mm",
        )

        # Save the image
        img.save(output_path, format=format.upper())

        console.print(f"[green]Placeholder image generated:[/green] {output_path}")
        return output_path

    except Exception as e:
        console.print(f"[red]Error generating placeholder image:[/red] {e}")
        return ""


class SchematicToMermaid:
    """
    Converter for KiCad schematics to Mermaid diagrams.
    """

    def __init__(self, schematic_path: str):
        """
        Initialize the converter with a schematic file path.

        Args:
            schematic_path: Path to the KiCad schematic file
        """
        self.schematic_path = schematic_path
        from twinizer.hardware.kicad.sch_parser import SchematicParser

        self.parser = SchematicParser(schematic_path)

    def to_flowchart(self, output_path: Optional[str] = None) -> str:
        """
        Convert the schematic to a Mermaid flowchart diagram.

        Args:
            output_path: Path to save the Mermaid file, if None uses the same name with .mmd extension

        Returns:
            Path to the output Mermaid file
        """
        try:
            if output_path is None:
                base_path = os.path.splitext(self.schematic_path)[0]
                output_path = f"{base_path}_flowchart.mmd"

            # Parse the schematic
            self.parser.parse()

            # Generate flowchart
            mermaid_lines = ["flowchart TD"]

            # Add components as nodes
            for component in self.parser.components:
                comp_id = component.get("reference", "UNKNOWN")
                comp_value = component.get("value", "")
                comp_name = f"{comp_id}[{comp_id}: {comp_value}]"
                mermaid_lines.append(f"    {comp_name}")

            # Add connections
            for net in self.parser.nets:
                net_name = net.get("name", "")
                connections = net.get("connections", [])

                if len(connections) >= 2:
                    for i in range(len(connections) - 1):
                        src = connections[i]
                        dst = connections[i + 1]
                        mermaid_lines.append(f"    {src} -- {net_name} --> {dst}")

            # Write to file
            with open(output_path, "w") as f:
                f.write("\n".join(mermaid_lines))

            console.print(f"[green]Mermaid flowchart saved to:[/green] {output_path}")
            return output_path
        except Exception as e:
            console.print(f"[red]Error generating Mermaid flowchart:[/red] {str(e)}")
            # Create a minimal valid Mermaid diagram as a fallback
            with open(output_path, "w") as f:
                f.write("flowchart TD\n    A[Error] --> B[Could not parse schematic]\n")
            console.print(
                f"[yellow]Created fallback diagram at:[/yellow] {output_path}"
            )
            return output_path

    def to_graph(self, output_path: Optional[str] = None) -> str:
        """
        Convert the schematic to a Mermaid graph diagram with LR layout.

        This diagram type often provides a better visualization of electronic schematics
        with clearer connection paths.

        Args:
            output_path: Path to save the Mermaid file, if None uses the same name with .mmd extension

        Returns:
            Path to the output Mermaid file
        """
        try:
            if output_path is None:
                base_path = os.path.splitext(self.schematic_path)[0]
                output_path = f"{base_path}_graph.mmd"

            # Parse the schematic
            self.parser.parse()

            # Generate graph
            mermaid_lines = ["graph LR"]

            # Define component groups and their styles
            mermaid_lines.append("    %% Component Groups")
            mermaid_lines.append('    subgraph Connectors["Connectors and Headers"]')
            mermaid_lines.append(
                "    style Connectors fill:#e6f7ff,stroke:#1890ff,stroke-width:2px"
            )

            # Add connectors to the Connectors subgraph
            connector_ids = []
            for component in self.parser.components:
                comp_id = component.get("reference", "UNKNOWN")
                if (
                    comp_id.startswith("J")
                    or comp_id.startswith("P")
                    or comp_id.startswith("CN")
                ):
                    connector_ids.append(comp_id)
                    comp_value = component.get("value", "")
                    comp_name = f"{comp_id}>J{comp_id}: {comp_value}]"
                    mermaid_lines.append(f"        {comp_name}")

            mermaid_lines.append("    end")

            # Power components subgraph
            mermaid_lines.append('    subgraph Power["Power Supply"]')
            mermaid_lines.append(
                "    style Power fill:#fff7e6,stroke:#fa8c16,stroke-width:2px"
            )

            # Add power components to the Power subgraph
            power_ids = []
            for component in self.parser.components:
                comp_id = component.get("reference", "UNKNOWN")
                if (
                    comp_id.startswith("#PWR")
                    or comp_id.startswith("U")
                    and ("VCC" in comp_id or "VDD" in comp_id or "REG" in comp_id)
                ):
                    power_ids.append(comp_id)
                    comp_value = component.get("value", "")
                    comp_name = f"{comp_id}([{comp_id}: {comp_value}])"
                    mermaid_lines.append(f"        {comp_name}")

            mermaid_lines.append("    end")

            # Passive components subgraph
            mermaid_lines.append('    subgraph Passives["Passive Components"]')
            mermaid_lines.append(
                "    style Passives fill:#f6ffed,stroke:#52c41a,stroke-width:2px"
            )

            # Add passive components to the Passives subgraph
            passive_ids = []
            for component in self.parser.components:
                comp_id = component.get("reference", "UNKNOWN")
                if (
                    comp_id.startswith("R")
                    or comp_id.startswith("C")
                    or comp_id.startswith("L")
                ):
                    passive_ids.append(comp_id)
                    comp_value = component.get("value", "")

                    # Choose shape based on component type
                    if comp_id.startswith("R"):
                        comp_name = f"{comp_id}[/{comp_id}: {comp_value}/]"
                    elif comp_id.startswith("C"):
                        comp_name = f"{comp_id}[({comp_id}: {comp_value})]"
                    elif comp_id.startswith("L"):
                        comp_name = f"{comp_id}[{{{comp_id}: {comp_value}}}]"
                    else:
                        comp_name = f"{comp_id}[{comp_id}: {comp_value}]"

                    mermaid_lines.append(f"        {comp_name}")

            mermaid_lines.append("    end")

            # Active components subgraph
            mermaid_lines.append('    subgraph Actives["Active Components"]')
            mermaid_lines.append(
                "    style Actives fill:#f9f0ff,stroke:#722ed1,stroke-width:2px"
            )

            # Add active components to the Actives subgraph
            active_ids = []
            for component in self.parser.components:
                comp_id = component.get("reference", "UNKNOWN")
                if (
                    (comp_id.startswith("U") and not comp_id.startswith("#PWR"))
                    or comp_id.startswith("Q")
                    or comp_id.startswith("D")
                    or comp_id.startswith("IC")
                ):
                    active_ids.append(comp_id)
                    comp_value = component.get("value", "")
                    comp_footprint = component.get("footprint", "")

                    # Add footprint info if available
                    footprint_info = f" ({comp_footprint})" if comp_footprint else ""

                    # Choose shape based on component type
                    if comp_id.startswith("D") or comp_id.startswith("LED"):
                        comp_name = (
                            f"{comp_id}[{{{comp_id}: {comp_value}{footprint_info}}}]"
                        )
                    elif comp_id.startswith("Q") or comp_id.startswith("T"):
                        comp_name = (
                            f"{comp_id}(({comp_id}: {comp_value}{footprint_info}))"
                        )
                    else:
                        comp_name = (
                            f"{comp_id}[{comp_id}: {comp_value}{footprint_info}]"
                        )

                    mermaid_lines.append(f"        {comp_name}")

            mermaid_lines.append("    end")

            # Other components (not in any group)
            other_components = []
            for component in self.parser.components:
                comp_id = component.get("reference", "UNKNOWN")
                if (
                    comp_id not in connector_ids
                    and comp_id not in power_ids
                    and comp_id not in passive_ids
                    and comp_id not in active_ids
                ):
                    other_components.append(component)

            if other_components:
                mermaid_lines.append('    subgraph Others["Other Components"]')
                mermaid_lines.append(
                    "    style Others fill:#f5f5f5,stroke:#d9d9d9,stroke-width:2px"
                )

                for component in other_components:
                    comp_id = component.get("reference", "UNKNOWN")
                    comp_value = component.get("value", "")
                    comp_name = f"{comp_id}[{comp_id}: {comp_value}]"
                    mermaid_lines.append(f"        {comp_name}")

                mermaid_lines.append("    end")

            # Add connections with different styles and colors
            mermaid_lines.append("    %% Connections")

            # Define connection styles
            mermaid_lines.append("    %% Connection Styles")
            mermaid_lines.append(
                "    classDef powerNet stroke:#fa8c16,stroke-width:2px,color:#fa8c16"
            )
            mermaid_lines.append(
                "    classDef groundNet stroke:#000000,stroke-width:2px,color:#000000"
            )
            mermaid_lines.append(
                "    classDef signalNet stroke:#1890ff,stroke-width:1px,color:#1890ff"
            )
            mermaid_lines.append(
                "    classDef controlNet stroke:#722ed1,stroke-width:1px,color:#722ed1"
            )

            # Track connection IDs for styling
            power_connections = []
            ground_connections = []
            signal_connections = []
            control_connections = []

            for net in self.parser.nets:
                net_name = net.get("name", "")
                connections = net.get("connections", [])

                # Choose line style and class based on net name
                line_style = "--"
                connection_class = "signalNet"

                if "GND" in net_name.upper() or "VSS" in net_name.upper():
                    line_style = "==="  # Thick line for ground
                    connection_class = "groundNet"
                elif (
                    "VCC" in net_name.upper()
                    or "VDD" in net_name.upper()
                    or "+5V" in net_name.upper()
                    or "+3V3" in net_name.upper()
                    or "+24V" in net_name.upper()
                ):
                    line_style = "-.-"  # Dotted line for power
                    connection_class = "powerNet"
                elif (
                    "CLK" in net_name.upper()
                    or "EN" in net_name.upper()
                    or "RST" in net_name.upper()
                    or "CS" in net_name.upper()
                ):
                    line_style = "-->"  # Arrow for control signals
                    connection_class = "controlNet"

                if len(connections) >= 2:
                    for i in range(len(connections) - 1):
                        src = connections[i]
                        dst = connections[i + 1]
                        connection_id = f"connection_{len(signal_connections) + len(power_connections) + len(ground_connections) + len(control_connections)}"

                        # Add the connection with a unique ID
                        mermaid_lines.append(
                            f"    {src} {line_style} {net_name} {line_style}> {dst}"
                        )

                        # Track the connection for styling
                        if connection_class == "powerNet":
                            power_connections.append(connection_id)
                        elif connection_class == "groundNet":
                            ground_connections.append(connection_id)
                        elif connection_class == "controlNet":
                            control_connections.append(connection_id)
                        else:
                            signal_connections.append(connection_id)

            # Apply styles to connections
            if power_connections:
                mermaid_lines.append(
                    f"    class {','.join(power_connections)} powerNet"
                )
            if ground_connections:
                mermaid_lines.append(
                    f"    class {','.join(ground_connections)} groundNet"
                )
            if control_connections:
                mermaid_lines.append(
                    f"    class {','.join(control_connections)} controlNet"
                )
            if signal_connections:
                mermaid_lines.append(
                    f"    class {','.join(signal_connections)} signalNet"
                )

            # Add title and description
            schematic_name = os.path.basename(self.schematic_path)
            mermaid_lines.insert(1, f"    %% KiCad Schematic: {schematic_name}")
            mermaid_lines.insert(
                2,
                f"    %% Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            )
            mermaid_lines.insert(
                3,
                f"    %% Components: {len(self.parser.components)}, Connections: {len(self.parser.nets)}",
            )

            # Write to file
            with open(output_path, "w") as f:
                f.write("\n".join(mermaid_lines))

            console.print(
                f"[green]Enhanced Mermaid graph saved to:[/green] {output_path}"
            )
            return output_path
        except Exception as e:
            console.print(f"[red]Error generating Mermaid graph:[/red] {str(e)}")
            # Create a minimal valid Mermaid diagram as a fallback
            with open(output_path, "w") as f:
                f.write("graph LR\n    A[Error] --> B[Could not parse schematic]\n")
            console.print(
                f"[yellow]Created fallback diagram at:[/yellow] {output_path}"
            )
            return output_path

    def to_class_diagram(self, output_path: Optional[str] = None) -> str:
        """
        Convert the schematic to a Mermaid class diagram.

        Args:
            output_path: Path to save the Mermaid file, if None uses the same name with .mmd extension

        Returns:
            Path to the output Mermaid file
        """
        try:
            if output_path is None:
                base_path = os.path.splitext(self.schematic_path)[0]
                output_path = f"{base_path}_class.mmd"

            # Parse the schematic
            self.parser.parse()

            # Generate class diagram
            mermaid_lines = ["classDiagram"]

            # Group components by type/library
            components_by_type = {}
            for component in self.parser.components:
                lib_id = component.get("lib_id", "Unknown")
                if lib_id not in components_by_type:
                    components_by_type[lib_id] = []
                components_by_type[lib_id].append(component)

            # Add classes for each component type
            for lib_id, components in components_by_type.items():
                class_name = lib_id.replace(":", "_").replace("/", "_")
                mermaid_lines.append(f"    class {class_name} {{")

                # Add properties based on the first component
                if components:
                    for key, value in components[0].items():
                        if key not in ["lib_id", "reference"]:
                            mermaid_lines.append(f"        +{key}: {value}")

                mermaid_lines.append("    }")

                # Add instances
                for component in components:
                    reference = component.get("reference", "UNKNOWN")
                    mermaid_lines.append(f"    {class_name} <|-- {reference}")

            # Write to file
            with open(output_path, "w") as f:
                f.write("\n".join(mermaid_lines))

            console.print(
                f"[green]Mermaid class diagram saved to:[/green] {output_path}"
            )
            return output_path
        except Exception as e:
            console.print(
                f"[red]Error generating Mermaid class diagram:[/red] {str(e)}"
            )
            # Create a minimal valid Mermaid diagram as a fallback
            with open(output_path, "w") as f:
                f.write(
                    "classDiagram\n    class Error {\n        +message: Could not parse schematic\n    }\n"
                )
            console.print(
                f"[yellow]Created fallback diagram at:[/yellow] {output_path}"
            )
            return output_path


class SchematicToBOM:
    """
    Converter for KiCad schematics to Bill of Materials (BOM).
    """

    def __init__(self, schematic_path: str):
        """
        Initialize the converter with a schematic file path.

        Args:
            schematic_path: Path to the KiCad schematic file
        """
        self.schematic_path = schematic_path
        from twinizer.hardware.kicad.sch_parser import SchematicParser

        self.parser = SchematicParser(schematic_path)

    def to_csv(self, output_path: Optional[str] = None) -> str:
        """
        Convert the schematic to a CSV BOM file.

        Args:
            output_path: Path to save the CSV file, if None uses the same name with .csv extension

        Returns:
            Path to the output CSV file
        """
        if output_path is None:
            base_path = os.path.splitext(self.schematic_path)[0]
            output_path = f"{base_path}_bom.csv"

        # Parse the schematic
        self.parser.parse()

        # Group components by value and footprint
        grouped_components = {}
        for component in self.parser.components:
            comp_value = component.get("value", "Unknown")
            comp_footprint = component.get("footprint", "Unknown")
            key = f"{comp_value}_{comp_footprint}"

            if key not in grouped_components:
                grouped_components[key] = {
                    "value": comp_value,
                    "footprint": comp_footprint,
                    "references": [],
                    "datasheet": component.get("datasheet", ""),
                    "description": component.get("description", ""),
                }

            grouped_components[key]["references"].append(
                component.get("reference", "Unknown")
            )

        # Write to CSV file
        import csv

        with open(output_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "Item",
                    "Quantity",
                    "References",
                    "Value",
                    "Footprint",
                    "Datasheet",
                    "Description",
                ]
            )

            for i, (_, component) in enumerate(grouped_components.items(), 1):
                writer.writerow(
                    [
                        i,
                        len(component["references"]),
                        ", ".join(sorted(component["references"])),
                        component["value"],
                        component["footprint"],
                        component["datasheet"],
                        component["description"],
                    ]
                )

        console.print(f"[green]BOM saved to:[/green] {output_path}")
        return output_path

    def to_markdown(self, output_path: Optional[str] = None) -> str:
        """
        Convert the schematic to a Markdown BOM file.

        Args:
            output_path: Path to save the Markdown file, if None uses the same name with .md extension

        Returns:
            Path to the output Markdown file
        """
        if output_path is None:
            base_path = os.path.splitext(self.schematic_path)[0]
            output_path = f"{base_path}_bom.md"

        # Parse the schematic
        self.parser.parse()

        # Group components by value and footprint
        grouped_components = {}
        for component in self.parser.components:
            comp_value = component.get("value", "Unknown")
            comp_footprint = component.get("footprint", "Unknown")
            key = f"{comp_value}_{comp_footprint}"

            if key not in grouped_components:
                grouped_components[key] = {
                    "value": comp_value,
                    "footprint": comp_footprint,
                    "references": [],
                    "datasheet": component.get("datasheet", ""),
                    "description": component.get("description", ""),
                }

            grouped_components[key]["references"].append(
                component.get("reference", "Unknown")
            )

        # Write to Markdown file
        with open(output_path, "w") as f:
            f.write(f"# Bill of Materials: {os.path.basename(self.schematic_path)}\n\n")
            f.write(
                "| Item | Quantity | References | Value | Footprint | Datasheet | Description |\n"
            )
            f.write(
                "|------|----------|------------|-------|-----------|-----------|-------------|\n"
            )

            for i, (_, component) in enumerate(grouped_components.items(), 1):
                f.write(
                    f"| {i} | {len(component['references'])} | {', '.join(sorted(component['references']))} | "
                )
                f.write(
                    f"{component['value']} | {component['footprint']} | {component['datasheet']} | "
                )
                f.write(f"{component['description']} |\n")

        console.print(f"[green]BOM saved to:[/green] {output_path}")
        return output_path

    def to_json(self, output_path: Optional[str] = None) -> str:
        """
        Convert the schematic to a JSON BOM file.

        Args:
            output_path: Path to save the JSON file, if None uses the same name with .json extension

        Returns:
            Path to the output JSON file
        """
        if output_path is None:
            base_path = os.path.splitext(self.schematic_path)[0]
            output_path = f"{base_path}_bom.json"

        # Parse the schematic
        self.parser.parse()

        # Group components by value and footprint
        grouped_components = {}
        for component in self.parser.components:
            comp_value = component.get("value", "Unknown")
            comp_footprint = component.get("footprint", "Unknown")
            key = f"{comp_value}_{comp_footprint}"

            if key not in grouped_components:
                grouped_components[key] = {
                    "value": comp_value,
                    "footprint": comp_footprint,
                    "references": [],
                    "datasheet": component.get("datasheet", ""),
                    "description": component.get("description", ""),
                }

            grouped_components[key]["references"].append(
                component.get("reference", "Unknown")
            )

        # Convert to list for JSON serialization
        bom_data = []
        for i, (_, component) in enumerate(grouped_components.items(), 1):
            bom_data.append(
                {
                    "item": i,
                    "quantity": len(component["references"]),
                    "references": sorted(component["references"]),
                    "value": component["value"],
                    "footprint": component["footprint"],
                    "datasheet": component["datasheet"],
                    "description": component["description"],
                }
            )

        # Write to JSON file
        import json

        with open(output_path, "w") as f:
            json.dump({"bom": bom_data}, f, indent=2)

        console.print(f"[green]BOM saved to:[/green] {output_path}")
        return output_path

    def to_html(self, output_path: Optional[str] = None) -> str:
        """
        Convert the schematic to an HTML BOM file.

        Args:
            output_path: Path to save the HTML file, if None uses the same name with .html extension

        Returns:
            Path to the output HTML file
        """
        if output_path is None:
            base_path = os.path.splitext(self.schematic_path)[0]
            output_path = f"{base_path}_bom.html"

        # Parse the schematic
        self.parser.parse()

        # Group components by value and footprint
        grouped_components = {}
        for component in self.parser.components:
            comp_value = component.get("value", "Unknown")
            comp_footprint = component.get("footprint", "Unknown")
            key = f"{comp_value}_{comp_footprint}"

            if key not in grouped_components:
                grouped_components[key] = {
                    "value": comp_value,
                    "footprint": comp_footprint,
                    "references": [],
                    "datasheet": component.get("datasheet", ""),
                    "description": component.get("description", ""),
                }

            grouped_components[key]["references"].append(
                component.get("reference", "Unknown")
            )

        # Write to HTML file
        with open(output_path, "w") as f:
            f.write(
                f"""<!DOCTYPE html>
<html>
<head>
    <title>Bill of Materials: {os.path.basename(self.schematic_path)}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        h1 {{ color: #333; }}
    </style>
</head>
<body>
    <h1>Bill of Materials: {os.path.basename(self.schematic_path)}</h1>
    <table>
        <tr>
            <th>Item</th>
            <th>Quantity</th>
            <th>References</th>
            <th>Value</th>
            <th>Footprint</th>
            <th>Datasheet</th>
            <th>Description</th>
        </tr>
"""
            )

            for i, (_, component) in enumerate(grouped_components.items(), 1):
                f.write(
                    f"""        <tr>
            <td>{i}</td>
            <td>{len(component['references'])}</td>
            <td>{', '.join(sorted(component['references']))}</td>
            <td>{component['value']}</td>
            <td>{component['footprint']}</td>
            <td>{component['datasheet']}</td>
            <td>{component['description']}</td>
        </tr>
"""
                )

            f.write(
                """    </table>
</body>
</html>"""
            )

        console.print(f"[green]BOM saved to:[/green] {output_path}")
        return output_path

    def to_xlsx(self, output_path: Optional[str] = None) -> str:
        """
        Convert the schematic to an Excel XLSX BOM file.

        Args:
            output_path: Path to save the XLSX file, if None uses the same name with .xlsx extension

        Returns:
            Path to the output XLSX file
        """
        if output_path is None:
            base_path = os.path.splitext(self.schematic_path)[0]
            output_path = f"{base_path}_bom.xlsx"

        try:
            import pandas as pd
        except ImportError:
            console.print(
                "[red]Error:[/red] pandas is required for Excel export. Install with 'pip install pandas openpyxl'"
            )
            raise

        # Parse the schematic
        self.parser.parse()

        # Group components by value and footprint
        grouped_components = {}
        for component in self.parser.components:
            comp_value = component.get("value", "Unknown")
            comp_footprint = component.get("footprint", "Unknown")
            key = f"{comp_value}_{comp_footprint}"

            if key not in grouped_components:
                grouped_components[key] = {
                    "value": comp_value,
                    "footprint": comp_footprint,
                    "references": [],
                    "datasheet": component.get("datasheet", ""),
                    "description": component.get("description", ""),
                }

            grouped_components[key]["references"].append(
                component.get("reference", "Unknown")
            )

        # Convert to list for DataFrame
        bom_data = []
        for i, (_, component) in enumerate(grouped_components.items(), 1):
            bom_data.append(
                {
                    "Item": i,
                    "Quantity": len(component["references"]),
                    "References": ", ".join(sorted(component["references"])),
                    "Value": component["value"],
                    "Footprint": component["footprint"],
                    "Datasheet": component["datasheet"],
                    "Description": component["description"],
                }
            )

        # Create DataFrame and export to Excel
        df = pd.DataFrame(bom_data)
        df.to_excel(output_path, index=False, sheet_name="BOM")

        console.print(f"[green]BOM saved to:[/green] {output_path}")
        return output_path


class PCBToMermaid:
    """
    Converter for KiCad PCB layouts to Mermaid diagrams.
    """

    def __init__(self, pcb_path: str):
        """
        Initialize the converter with a PCB file path.

        Args:
            pcb_path: Path to the KiCad PCB file
        """
        self.pcb_path = pcb_path
        from twinizer.hardware.kicad.pcb_parser import PCBParser

        self.parser = PCBParser(pcb_path)

    def to_flowchart(self, output_path: Optional[str] = None) -> str:
        """
        Convert the PCB to a Mermaid flowchart diagram.

        Args:
            output_path: Path to save the Mermaid file, if None uses the same name with .mmd extension

        Returns:
            Path to the output Mermaid file
        """
        if output_path is None:
            base_path = os.path.splitext(self.pcb_path)[0]
            output_path = f"{base_path}_pcb_flowchart.mmd"

        # Parse the PCB
        self.parser.parse()

        # Generate flowchart
        mermaid_lines = ["flowchart TD"]

        # Add modules as nodes
        for module in self.parser.modules:
            module_ref = module.get("reference", "UNKNOWN")
            module_value = module.get("value", "")
            module_name = f"{module_ref}[{module_ref}: {module_value}]"
            mermaid_lines.append(f"    {module_name}")

        # Add connections based on nets
        for net in self.parser.nets:
            net_name = net.get("name", "")
            pads = net.get("pads", [])

            if len(pads) >= 2:
                for i in range(len(pads) - 1):
                    src = pads[i].split(":")[0]  # Extract module reference from pad
                    dst = pads[i + 1].split(":")[0]
                    mermaid_lines.append(f"    {src} -- {net_name} --> {dst}")

        # Write to file
        with open(output_path, "w") as f:
            f.write("\n".join(mermaid_lines))

        console.print(f"[green]Mermaid PCB flowchart saved to:[/green] {output_path}")
        return output_path

    def to_class_diagram(self, output_path: Optional[str] = None) -> str:
        """
        Convert the PCB to a Mermaid class diagram.

        Args:
            output_path: Path to save the Mermaid file, if None uses the same name with .mmd extension

        Returns:
            Path to the output Mermaid file
        """
        if output_path is None:
            base_path = os.path.splitext(self.pcb_path)[0]
            output_path = f"{base_path}_pcb_class.mmd"

        # Parse the PCB
        self.parser.parse()

        # Generate class diagram
        mermaid_lines = ["classDiagram"]

        # Group modules by type/value
        modules_by_type = {}
        for module in self.parser.modules:
            module_type = module.get("value", "Unknown")
            if module_type not in modules_by_type:
                modules_by_type[module_type] = []
            modules_by_type[module_type].append(module)

        # Add module types as classes
        for module_type, modules in modules_by_type.items():
            safe_type = module_type.replace(" ", "_").replace("-", "_")
            mermaid_lines.append(f"    class {safe_type} {{")

            # Add module instances as class members
            for module in modules:
                module_ref = module.get("reference", "UNKNOWN")
                module_pos = f"({module.get('position', {}).get('x', 0)}, {module.get('position', {}).get('y', 0)})"
                mermaid_lines.append(f"        +{module_ref} {module_pos}")

            mermaid_lines.append("    }")

            # Add connections between module types based on nets
            for net in self.parser.nets:
                pads = net.get("pads", [])
                if len(pads) >= 2:
                    # Extract module types for connections
                    connection_types = set()
                    for pad in pads:
                        # Extract module reference from pad (e.g., "R1:1" -> "R1")
                        module_ref = pad.split(":")[0] if ":" in pad else pad

                        # Find the module type
                        for module in self.parser.modules:
                            if module.get("reference") == module_ref:
                                connection_types.add(
                                    module.get("value", "Unknown")
                                    .replace(" ", "_")
                                    .replace("-", "_")
                                )
                                break

                    # Add relationships between types
                    connection_types = list(connection_types)
                    if len(connection_types) >= 2:
                        for i in range(len(connection_types) - 1):
                            mermaid_lines.append(
                                f"    {connection_types[i]} -- {connection_types[i+1]}"
                            )

        # Write to file
        with open(output_path, "w") as f:
            f.write("\n".join(mermaid_lines))

        console.print(
            f"[green]Mermaid PCB class diagram saved to:[/green] {output_path}"
        )
        return output_path


class PCBTo3DModel:
    """
    Converter for KiCad PCB layouts to 3D models.
    """

    def __init__(self, pcb_path: str):
        """
        Initialize the converter with a PCB file path.

        Args:
            pcb_path: Path to the KiCad PCB file
        """
        self.pcb_path = pcb_path
        from twinizer.hardware.kicad.pcb_parser import PCBParser

        self.parser = PCBParser(pcb_path)

    def to_stl(self, output_path: Optional[str] = None) -> str:
        """
        Convert the PCB to an STL 3D model file.

        Args:
            output_path: Path to save the STL file, if None uses the same name with .stl extension

        Returns:
            Path to the output STL file
        """
        if output_path is None:
            base_path = os.path.splitext(self.pcb_path)[0]
            output_path = f"{base_path}.stl"

        # Check if KiCad CLI is available
        if not _check_kicad_cli():
            console.print(
                "[yellow]Warning: KiCad CLI not found, cannot generate STL file.[/yellow]"
            )
            console.print(
                "[yellow]Please install KiCad with command-line tools to use this feature.[/yellow]"
            )
            return ""

        # Use KiCad CLI to export 3D model
        try:
            cmd = [
                "kicad-cli",
                "pcb",
                "export",
                "step",
                "--output",
                output_path,
                self.pcb_path,
            ]
            console.print(f"[blue]Running:[/blue] {' '.join(cmd)}")

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                console.print(f"[red]Error exporting STL:[/red] {result.stderr}")
                return ""

            console.print(f"[green]STL file saved to:[/green] {output_path}")
            return output_path

        except Exception as e:
            console.print(f"[red]Error exporting STL:[/red] {e}")
            return ""

    def to_step(self, output_path: Optional[str] = None) -> str:
        """
        Convert the PCB to a STEP 3D model file.

        Args:
            output_path: Path to save the STEP file, if None uses the same name with .step extension

        Returns:
            Path to the output STEP file
        """
        if output_path is None:
            base_path = os.path.splitext(self.pcb_path)[0]
            output_path = f"{base_path}.step"

        # Check if KiCad CLI is available
        if not _check_kicad_cli():
            console.print(
                "[yellow]Warning: KiCad CLI not found, cannot generate STEP file.[/yellow]"
            )
            console.print(
                "[yellow]Please install KiCad with command-line tools to use this feature.[/yellow]"
            )
            return ""

        # Use KiCad CLI to export 3D model
        try:
            cmd = [
                "kicad-cli",
                "pcb",
                "export",
                "step",
                "--output",
                output_path,
                self.pcb_path,
            ]
            console.print(f"[blue]Running:[/blue] {' '.join(cmd)}")

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                console.print(f"[red]Error exporting STEP:[/red] {result.stderr}")
                return ""

            console.print(f"[green]STEP file saved to:[/green] {output_path}")
            return output_path

        except Exception as e:
            console.print(f"[red]Error exporting STEP:[/red] {e}")
            return ""

    def to_vrml(self, output_path: Optional[str] = None) -> str:
        """
        Convert the PCB to a VRML 3D model file.

        Args:
            output_path: Path to save the VRML file, if None uses the same name with .wrl extension

        Returns:
            Path to the output VRML file
        """
        if output_path is None:
            base_path = os.path.splitext(self.pcb_path)[0]
            output_path = f"{base_path}.wrl"

        # Check if KiCad CLI is available
        if not _check_kicad_cli():
            console.print(
                "[yellow]Warning: KiCad CLI not found, cannot generate VRML file.[/yellow]"
            )
            console.print(
                "[yellow]Please install KiCad with command-line tools to use this feature.[/yellow]"
            )
            return ""

        # Use KiCad CLI to export 3D model
        try:
            cmd = [
                "kicad-cli",
                "pcb",
                "export",
                "vrml",
                "--output",
                output_path,
                self.pcb_path,
            ]
            console.print(f"[blue]Running:[/blue] {' '.join(cmd)}")

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                console.print(f"[red]Error exporting VRML:[/red] {result.stderr}")
                return ""

            console.print(f"[green]VRML file saved to:[/green] {output_path}")
            return output_path

        except Exception as e:
            console.print(f"[red]Error exporting VRML:[/red] {e}")
            return ""


def convert_kicad_schematic_to_netlist(
    schematic_path: str, output_path: Optional[str] = None
) -> str:
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

    console.print(
        f"Converting [cyan]{schematic_path}[/cyan] to netlist [green]{output_path}[/green]"
    )

    # Check if KiCad CLI is available
    kicad_cli_available = _check_kicad_cli()

    if kicad_cli_available:
        try:
            cmd = [
                "kicad-cli",
                "sch",
                "export",
                "netlist",
                "-o",
                output_path,
                schematic_path,
            ]

            console.print(f"Running: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            )

            if os.path.exists(output_path):
                console.print(f"[green]Conversion successful:[/green] {output_path}")
                return output_path
            else:
                console.print(
                    f"[yellow]Warning: Output file not found after conversion[/yellow]"
                )
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
        console.print(
            f"[yellow]Warning: KiCad CLI not available for netlist generation[/yellow]"
        )
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

    console.print(
        f"Converting [cyan]{pcb_path}[/cyan] to Gerber files in [green]{output_dir}[/green]"
    )

    # Check if KiCad CLI is available
    kicad_cli_available = _check_kicad_cli()

    if kicad_cli_available:
        try:
            cmd = [
                "kicad-cli",
                "pcb",
                "export",
                "gerber",
                "--output",
                output_dir,
                pcb_path,
            ]

            console.print(f"Running: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            )

            # Check if any Gerber files were created
            gerber_files = [
                f
                for f in os.listdir(output_dir)
                if f.endswith((".gbr", ".gbl", ".gtl", ".gtp", ".gto", ".gts"))
            ]

            if gerber_files:
                console.print(
                    f"[green]Conversion successful:[/green] Generated {len(gerber_files)} Gerber files in {output_dir}"
                )
                for file in gerber_files:
                    console.print(f"  - {file}")
                return output_dir
            else:
                console.print(
                    f"[yellow]Warning: No Gerber files found after conversion[/yellow]"
                )
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
                (pcbnew.F_Cu, "F.Cu"),
                (pcbnew.B_Cu, "B.Cu"),
                (pcbnew.F_Paste, "F.Paste"),
                (pcbnew.B_Paste, "B.Paste"),
                (pcbnew.F_SilkS, "F.SilkS"),
                (pcbnew.B_SilkS, "B.SilkS"),
                (pcbnew.F_Mask, "F.Mask"),
                (pcbnew.B_Mask, "B.Mask"),
                (pcbnew.Edge_Cuts, "Edge.Cuts"),
            ]

            for layer_id, layer_name in plot_plan:
                pctl.SetLayer(layer_id)
                pctl.OpenPlotfile(layer_name, pcbnew.PLOT_FORMAT_GERBER, layer_name)
                pctl.PlotLayer()

            # Close the plot controller
            pctl.ClosePlot()

            # Check if any Gerber files were created
            gerber_files = [
                f
                for f in os.listdir(output_dir)
                if f.endswith((".gbr", ".gbl", ".gtl", ".gtp", ".gto", ".gts"))
            ]

            if gerber_files:
                console.print(
                    f"[green]Conversion successful:[/green] Generated {len(gerber_files)} Gerber files in {output_dir}"
                )
                for file in gerber_files:
                    console.print(f"  - {file}")
                return output_dir
            else:
                console.print(
                    f"[yellow]Warning: No Gerber files found after conversion[/yellow]"
                )
                return ""

        except ImportError:
            console.print(
                f"[yellow]Warning: Neither KiCad CLI nor pcbnew module available for Gerber generation[/yellow]"
            )
            return ""
        except Exception as e:
            console.print(f"[red]Error during conversion:[/red] {e}")
            return ""


def convert_kicad_to_mermaid(
    schematic_path: str,
    output_path: Optional[str] = None,
    diagram_type: str = "flowchart",
) -> str:
    """
    Convert a KiCad schematic to Mermaid diagram format.

    Args:
        schematic_path: Path to the KiCad schematic file
        output_path: Path to save the Mermaid file, if None uses the same name with .mmd extension
        diagram_type: Type of Mermaid diagram to generate (flowchart, class, etc.)

    Returns:
        Path to the output Mermaid file
    """
    converter = SchematicToMermaid(schematic_path)

    if diagram_type == "flowchart":
        return converter.to_flowchart(output_path)
    elif diagram_type == "class":
        return converter.to_class_diagram(output_path)
    elif diagram_type == "graph":
        return converter.to_graph(output_path)
    else:
        console.print(f"[red]Error: Unknown diagram type: {diagram_type}[/red]")
        return ""


class SchematicToSVG:
    """
    Converter for KiCad schematics to SVG format using schemdraw.
    """

    def __init__(self, schematic_path: str):
        """
        Initialize the converter with a schematic file path.

        Args:
            schematic_path: Path to the KiCad schematic file
        """
        self.schematic_path = schematic_path
        from twinizer.hardware.kicad.sch_parser import SchematicParser

        self.parser = SchematicParser(schematic_path)

        if not SCHEMDRAW_AVAILABLE:
            console.print(
                "[red]Error: schemdraw package is not installed. Please install it with:[/red]"
            )
            console.print("[yellow]pip install schemdraw[/yellow]")
            raise ImportError("schemdraw package is required for SVG conversion")

    def convert(
        self,
        output_path: Optional[str] = None,
        theme: str = "default",
        generate_html: bool = False,
    ) -> Union[str, Tuple[str, str]]:
        """
        Convert the schematic to SVG format.

        Args:
            output_path: Path to save the SVG file, if None uses the same name with .svg extension
            theme: Theme to use for the SVG (default, dark, blue, minimal)
            generate_html: Whether to generate an HTML file with the SVG embedded

        Returns:
            Path to the output SVG file, or a tuple of (svg_path, html_path) if generate_html is True
        """
        # Parse the schematic
        self.parser.parse()

        # Prepare the output path
        if output_path is None:
            base_path = os.path.splitext(self.schematic_path)[0]
            output_path = f"{base_path}.svg"

        # Define component mapping for schemdraw elements
        component_map = {
            # Basic components
            "R": elm.Resistor,
            "C": elm.Capacitor,
            "L": elm.Inductor,
            "D": elm.Diode,
            "LED": elm.LED,
            "Q": elm.Transistor,
            "M": elm.MOSFET,
            "U": elm.Opamp,
            "SW": elm.Switch,
            "CONN": elm.Connector,
            # Reference prefixes
            "R": elm.Resistor,
            "C": elm.Capacitor,
            "L": elm.Inductor,
            "D": elm.Diode,
            "Q": elm.Transistor,
            "U": elm.Block,
            "J": elm.Connector,
            "SW": elm.Switch,
            "IC": elm.Block,
            "X": elm.Block,
        }

        # Sprawdź, czy lista komponentów nie jest pusta
        components_with_x = [c for c in self.parser.components if "x" in c]
        components_with_y = [c for c in self.parser.components if "y" in c]

        if not components_with_x or not components_with_y:
            console.print(
                "[yellow]Warning: Components without coordinates found in the schematic.[/yellow]"
            )
            # Utwórz pusty rysunek z informacją
            d = schemdraw.Drawing()
            d += elm.Annotate(label="Components without proper coordinates found").at(
                (0, 0)
            )
            d.save(output_path)
            console.print(f"[green]SVG saved to:[/green] {output_path}")

            # Generate HTML if requested
            if generate_html:
                html_path = f"{os.path.splitext(output_path)[0]}.html"
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(
                        f"""<!DOCTYPE html>
<html>
<head>
    <title>KiCad Schematic: {os.path.basename(self.schematic_path)}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .svg-container {{ 
            border: 1px solid #ddd; 
            padding: 10px; 
            margin-bottom: 20px;
            background-color: white;
        }}
        svg {{ max-width: 100%; height: auto; }}
        .warning {{ color: orange; font-weight: bold; }}
    </style>
</head>
<body>
    <h1>KiCad Schematic: {os.path.basename(self.schematic_path)}</h1>
    <p class="warning">Warning: Components without proper coordinates found in the schematic.</p>
    <div class="svg-container">
"""
                    )

                    # Embed the SVG
                    try:
                        with open(output_path, "r", encoding="utf-8") as svg_f:
                            svg_content = svg_f.read()
                        f.write(f"        {svg_content}\n")
                    except Exception as e:
                        f.write(f"        <p>Error embedding SVG: {e}</p>\n")

                    f.write(
                        """    </div>
</body>
</html>"""
                    )

                console.print(f"[green]HTML file generated:[/green] {html_path}")
                return output_path, html_path

            return output_path

        min_x = min(c["x"] for c in components_with_x)
        min_y = min(c["y"] for c in components_with_y)
        max_x = max(c["x"] for c in components_with_x)
        max_y = max(c["y"] for c in components_with_y)

        # Scale factors - ensure we don't divide by zero
        width = max_x - min_x
        height = max_y - min_y

        x_scale = 20 / width if width > 0 else 1
        y_scale = 20 / height if height > 0 else 1

        # Use the smaller scale to maintain aspect ratio
        scale = min(x_scale, y_scale)

        # Keep track of unique positions to avoid overlapping
        used_positions = set()

        # Draw components
        for comp in self.parser.components:
            # Get component properties
            comp_type = comp.get("lib_id", "").split(":")[-1]
            ref = comp.get("reference", "UNKNOWN")
            value = comp.get("value", "")
            x = comp.get("x", 0)
            y = comp.get("y", 0)

            prefix = ref[0] if ref and len(ref) > 0 else ""

            # Try to get element type from the map
            element_type = None

            # First try exact match
            if comp_type in component_map:
                element_type = component_map[comp_type]
            # Then try prefix match for reference
            elif prefix in component_map:
                element_type = component_map[prefix]
            # Default to a block
            else:
                element_type = elm.Block

            # Get label from reference and value
            label = f"{ref}"
            if value:
                label += f"\n{value}"

            # Adjust position
            x_pos = (x - min_x) * scale
            y_pos = (y - min_y) * scale

            # Ensure unique position
            base_pos = (x_pos, y_pos)
            pos = base_pos
            offset = 0
            while pos in used_positions:
                offset += 0.5
                pos = (x_pos + offset, y_pos + offset)
            used_positions.add(pos)

            # Add element to drawing
            try:
                if callable(element_type):
                    d += element_type().at(pos).label(label)
                else:
                    # For pre-configured elements like Connector
                    d += element_type.at(pos).label(label)
            except Exception as e:
                console.print(
                    f"[yellow]Warning: Error adding component {ref}:[/yellow] {e}"
                )
                # Fallback to block if specific element fails
                d += elm.Block().at(pos).label(label)

        # Draw connections
        for net in self.parser.nets:
            connections = net.get("connections", [])
            if len(connections) >= 2:
                for i in range(len(connections) - 1):
                    # Find component positions for the connection endpoints
                    start_comp = next(
                        (
                            c
                            for c in self.parser.components
                            if c.get("reference") == connections[i]
                        ),
                        None,
                    )
                    end_comp = next(
                        (
                            c
                            for c in self.parser.components
                            if c.get("reference") == connections[i + 1]
                        ),
                        None,
                    )

                    if start_comp and end_comp:
                        start_x = (start_comp.get("x", 0) - min_x) * scale
                        start_y = (start_comp.get("y", 0) - min_y) * scale
                        end_x = (end_comp.get("x", 0) - min_x) * scale
                        end_y = (end_comp.get("y", 0) - min_y) * scale

                        try:
                            d += elm.Line().at((start_x, start_y)).to((end_x, end_y))
                        except Exception as e:
                            console.print(
                                f"[yellow]Warning: Error drawing connection:[/yellow] {e}"
                            )

        # Save as SVG
        d.save(output_path)
        console.print(f"[green]SVG saved to:[/green] {output_path}")

        # Generate HTML if requested
        if generate_html:
            html_path = f"{os.path.splitext(output_path)[0]}.html"
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(
                    f"""<!DOCTYPE html>
<html>
<head>
    <title>KiCad Schematic: {os.path.basename(self.schematic_path)}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .svg-container {{ 
            border: 1px solid #ddd; 
            padding: 10px; 
            margin-bottom: 20px;
            background-color: white;
        }}
        svg {{ max-width: 100%; height: auto; }}
    </style>
</head>
<body>
    <h1>KiCad Schematic: {os.path.basename(self.schematic_path)}</h1>
    <div class="svg-container">
"""
                )

                # Embed the SVG
                try:
                    with open(output_path, "r", encoding="utf-8") as svg_f:
                        svg_content = svg_f.read()
                    f.write(f"        {svg_content}\n")
                except Exception as e:
                    f.write(f"        <p>Error embedding SVG: {e}</p>\n")

                f.write(
                    """    </div>
</body>
</html>"""
                )

            console.print(f"[green]HTML file generated:[/green] {html_path}")
            return output_path, html_path

        return output_path


def convert_kicad_to_svg(
    schematic_path: str,
    output_path: Optional[str] = None,
    theme: str = "default",
    generate_html: bool = False,
) -> Union[str, Tuple[str, str]]:
    """
    Convert a KiCad schematic to SVG format.

    Args:
        schematic_path: Path to the KiCad schematic file
        output_path: Path to save the SVG file, if None uses the same name with .svg extension
        theme: Theme to use for the SVG (default, dark, blue, minimal)
        generate_html: Whether to generate an HTML file with the SVG embedded

    Returns:
        Path to the output SVG file, or a tuple of (svg_path, html_path) if generate_html is True
    """
    converter = SchematicToSVG(schematic_path)
    return converter.convert(output_path, theme, generate_html)
