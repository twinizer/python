"""
png.py
"""

"""
PNG export for Mermaid diagrams.

This module provides functionality to convert Mermaid diagrams to PNG images.
It requires the Mermaid CLI (mmdc) to be installed.
"""

import os
import subprocess
import tempfile
from typing import Any, Dict, List, Optional, Union

from ..utils import add_theme_directive


def to_png(
    mermaid_code: str,
    output_path: str,
    width: int = 800,
    height: Optional[int] = None,
    background_color: str = "#ffffff",
    theme: str = "default",
) -> str:
    """
    Convert a Mermaid diagram to PNG image (requires Node.js and the Mermaid CLI).

    Args:
        mermaid_code: Mermaid diagram code
        output_path: Path to save the PNG file
        width: Width of the output image
        height: Height of the output image (auto-calculated if None)
        background_color: Background color for the image
        theme: Theme for the diagram ('default', 'dark', 'forest', 'neutral')

    Returns:
        Path to the output PNG file

    Raises:
        RuntimeError: If Mermaid CLI is not installed or conversion fails
    """
    # Check if mmdc is installed
    if not _is_mmdc_installed():
        raise RuntimeError(
            "Mermaid CLI (mmdc) is not installed or not found in PATH. "
            "Install it with: npm install -g @mermaid-js/mermaid-cli"
        )

    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # Add theme directive if not default
    if theme != "default":
        # Check if theme directive already exists
        if not mermaid_code.strip().startswith("%%{"):
            theme_directive = add_theme_directive(theme)
            if theme_directive:
                mermaid_code = f"{theme_directive}\n{mermaid_code}"

    # Create a temporary file to store the Mermaid code
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".mmd", delete=False
    ) as temp_file:
        temp_path = temp_file.name
        temp_file.write(mermaid_code)

    try:
        # Build command to generate PNG
        cmd = [
            "mmdc",
            "-i",
            temp_path,
            "-o",
            output_path,
            "-w",
            str(width),
            "-b",
            background_color,
        ]

        # Add height if specified
        if height:
            cmd.extend(["-H", str(height)])

        # Add theme if not default and wasn't added as directive
        if theme != "default" and not mermaid_code.strip().startswith("%%{"):
            cmd.extend(["-t", theme])

        # Execute command
        process = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False
        )

        # Check for errors
        if process.returncode != 0:
            raise RuntimeError(
                f"Failed to convert diagram to PNG: {process.stderr}\n"
                f"Command: {' '.join(cmd)}"
            )

        return output_path

    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def batch_convert_to_png(
    diagrams: Dict[str, str],
    output_dir: str,
    width: int = 800,
    height: Optional[int] = None,
    background_color: str = "#ffffff",
    theme: str = "default",
) -> Dict[str, str]:
    """
    Convert multiple Mermaid diagrams to PNG images.

    Args:
        diagrams: Dictionary mapping diagram IDs to Mermaid code
        output_dir: Directory to save the PNG files
        width: Width of the output images
        height: Height of the output images (auto-calculated if None)
        background_color: Background color for the images
        theme: Theme for the diagrams ('default', 'dark', 'forest', 'neutral')

    Returns:
        Dictionary mapping diagram IDs to output file paths
    """
    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # Convert each diagram
    output_paths = {}
    for diagram_id, mermaid_code in diagrams.items():
        # Create a safe filename from the diagram ID
        safe_id = "".join(c if c.isalnum() else "_" for c in diagram_id)
        output_path = os.path.join(output_dir, f"{safe_id}.png")

        try:
            output_paths[diagram_id] = to_png(
                mermaid_code, output_path, width, height, background_color, theme
            )
        except Exception as e:
            print(f"Failed to convert diagram '{diagram_id}': {e}")

    return output_paths


def _is_mmdc_installed() -> bool:
    """
    Check if Mermaid CLI (mmdc) is installed and available in PATH.

    Returns:
        True if mmdc is installed, False otherwise
    """
    try:
        process = subprocess.run(
            ["mmdc", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return process.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def install_mmdc() -> bool:
    """
    Attempt to install Mermaid CLI (mmdc) using npm.

    Returns:
        True if installation was successful, False otherwise
    """
    try:
        process = subprocess.run(
            ["npm", "install", "-g", "@mermaid-js/mermaid-cli"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return process.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False
