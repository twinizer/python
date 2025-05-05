#!/usr/bin/env python3
"""
Batch processing module for KiCad files.

This module provides functions for batch processing of KiCad schematic (.sch, .kicad_sch)
and PCB (.kicad_pcb) files. It supports recursive directory traversal and parallel processing.
"""

import concurrent.futures
import glob
import logging
import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from twinizer.hardware.kicad.converters import (
    PCBTo3DModel,
    PCBToMermaid,
    SchematicToBOM,
    SchematicToMermaid,
)
from twinizer.hardware.kicad.pcb_parser import PCBParser

# Import KiCad parsers and converters
from twinizer.hardware.kicad.sch_parser import SchematicParser

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def find_files(
    directory: str, patterns: List[str], recursive: bool = False
) -> List[str]:
    """
    Find files matching the given patterns in the specified directory.

    Args:
        directory: Directory to search in
        patterns: List of file patterns to match (e.g., ["*.sch", "*.kicad_sch"])
        recursive: Whether to search recursively in subdirectories

    Returns:
        List of file paths matching the patterns
    """
    found_files = []

    # Convert to absolute path
    directory = os.path.abspath(directory)

    for pattern in patterns:
        if recursive:
            # Use ** for recursive search
            search_pattern = os.path.join(directory, "**", pattern)
            matches = glob.glob(search_pattern, recursive=True)
        else:
            search_pattern = os.path.join(directory, pattern)
            matches = glob.glob(search_pattern)

        found_files.extend(matches)

    # Sort files for consistent processing order
    found_files.sort()

    logger.info(f"Found {len(found_files)} files matching patterns {patterns}")
    return found_files


def process_schematic_to_mermaid(
    schematic_file: str,
    output_dir: str,
    diagram_type: str = "flowchart",
    output_format: str = "mmd",
) -> str:
    """
    Convert a schematic file to a Mermaid diagram.

    Args:
        schematic_file: Path to the schematic file
        output_dir: Directory to save the output file
        diagram_type: Type of diagram to generate ("flowchart", "class", "er")
        output_format: Output format ("mmd" or "svg")

    Returns:
        Path to the output file
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Determine output filename
        base_name = os.path.basename(schematic_file)
        name_without_ext = os.path.splitext(base_name)[0]
        output_file = os.path.join(output_dir, f"{name_without_ext}.{output_format}")

        # Convert schematic to Mermaid diagram
        converter = SchematicToMermaid(schematic_file)

        if diagram_type.lower() == "flowchart":
            output_path = converter.to_flowchart(output_file)
        elif diagram_type.lower() == "class":
            output_path = converter.to_class_diagram(output_file)
        elif diagram_type.lower() == "er":
            output_path = converter.to_er_diagram(output_file)
        else:
            raise ValueError(f"Unsupported diagram type: {diagram_type}")

        logger.info(f"Converted {schematic_file} to {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Error converting {schematic_file} to Mermaid diagram: {str(e)}")
        return ""


def process_schematic_to_bom(
    schematic_file: str, output_dir: str, output_format: str = "csv"
) -> str:
    """
    Convert a schematic file to a Bill of Materials.

    Args:
        schematic_file: Path to the schematic file
        output_dir: Directory to save the output file
        output_format: Output format ("csv", "json", "xlsx")

    Returns:
        Path to the output file
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Determine output filename
        base_name = os.path.basename(schematic_file)
        name_without_ext = os.path.splitext(base_name)[0]
        output_file = os.path.join(
            output_dir, f"{name_without_ext}_bom.{output_format}"
        )

        # Convert schematic to BOM
        converter = SchematicToBOM(schematic_file)

        if output_format.lower() == "csv":
            output_path = converter.to_csv(output_file)
        elif output_format.lower() == "json":
            output_path = converter.to_json(output_file)
        elif output_format.lower() == "xlsx":
            output_path = converter.to_excel(output_file)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")

        logger.info(f"Converted {schematic_file} to BOM: {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Error converting {schematic_file} to BOM: {str(e)}")
        return ""


def process_pcb_to_mermaid(
    pcb_file: str,
    output_dir: str,
    diagram_type: str = "flowchart",
    output_format: str = "mmd",
) -> str:
    """
    Convert a PCB file to a Mermaid diagram.

    Args:
        pcb_file: Path to the PCB file
        output_dir: Directory to save the output file
        diagram_type: Type of diagram to generate ("flowchart", "class", "er")
        output_format: Output format ("mmd" or "svg")

    Returns:
        Path to the output file
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Determine output filename
        base_name = os.path.basename(pcb_file)
        name_without_ext = os.path.splitext(base_name)[0]
        output_file = os.path.join(output_dir, f"{name_without_ext}.{output_format}")

        # Convert PCB to Mermaid diagram
        converter = PCBToMermaid(pcb_file)

        if diagram_type.lower() == "flowchart":
            output_path = converter.to_flowchart(output_file)
        elif diagram_type.lower() == "class":
            output_path = converter.to_class_diagram(output_file)
        elif diagram_type.lower() == "er":
            output_path = converter.to_er_diagram(output_file)
        else:
            raise ValueError(f"Unsupported diagram type: {diagram_type}")

        logger.info(f"Converted {pcb_file} to {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Error converting {pcb_file} to Mermaid diagram: {str(e)}")
        return ""


def process_pcb_to_3d(
    pcb_file: str, output_dir: str, output_format: str = "step"
) -> str:
    """
    Convert a PCB file to a 3D model.

    Args:
        pcb_file: Path to the PCB file
        output_dir: Directory to save the output file
        output_format: Output format ("step", "stl", "wrl", "obj")

    Returns:
        Path to the output file
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Determine output filename
        base_name = os.path.basename(pcb_file)
        name_without_ext = os.path.splitext(base_name)[0]
        output_file = os.path.join(output_dir, f"{name_without_ext}.{output_format}")

        # Convert PCB to 3D model
        converter = PCBTo3DModel(pcb_file)

        if output_format.lower() == "step":
            output_path = converter.to_step(output_file)
        elif output_format.lower() == "stl":
            output_path = converter.to_stl(output_file)
        elif output_format.lower() == "wrl":
            output_path = converter.to_wrl(output_file)
        elif output_format.lower() == "obj":
            output_path = converter.to_obj(output_file)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")

        logger.info(f"Converted {pcb_file} to 3D model: {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Error converting {pcb_file} to 3D model: {str(e)}")
        return ""


def process_schematic_to_json(schematic_file: str, output_dir: str) -> str:
    """
    Parse a schematic file and save the result as JSON.

    Args:
        schematic_file: Path to the schematic file
        output_dir: Directory to save the output file

    Returns:
        Path to the output file
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Determine output filename
        base_name = os.path.basename(schematic_file)
        name_without_ext = os.path.splitext(base_name)[0]
        output_file = os.path.join(output_dir, f"{name_without_ext}.json")

        # Parse schematic
        parser = SchematicParser(schematic_file)
        schematic_data = parser.parse()

        # Save as JSON
        import json

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(schematic_data, f, indent=2)

        logger.info(f"Parsed {schematic_file} to {output_file}")
        return output_file

    except Exception as e:
        logger.error(f"Error parsing {schematic_file} to JSON: {str(e)}")
        return ""


def process_pcb_to_json(pcb_file: str, output_dir: str) -> str:
    """
    Parse a PCB file and save the result as JSON.

    Args:
        pcb_file: Path to the PCB file
        output_dir: Directory to save the output file

    Returns:
        Path to the output file
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Determine output filename
        base_name = os.path.basename(pcb_file)
        name_without_ext = os.path.splitext(base_name)[0]
        output_file = os.path.join(output_dir, f"{name_without_ext}.json")

        # Parse PCB
        parser = PCBParser(pcb_file)
        pcb_data = parser.parse()

        # Save as JSON
        import json

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(pcb_data, f, indent=2)

        logger.info(f"Parsed {pcb_file} to {output_file}")
        return output_file

    except Exception as e:
        logger.error(f"Error parsing {pcb_file} to JSON: {str(e)}")
        return ""


def batch_process_schematics(
    input_dir: str,
    output_dir: str,
    conversion_type: str = "mermaid",
    output_format: str = "mmd",
    diagram_type: str = "flowchart",
    recursive: bool = False,
    max_workers: Optional[int] = None,
) -> List[str]:
    """
    Batch process schematic files in a directory.

    Args:
        input_dir: Directory containing schematic files
        output_dir: Directory to save output files
        conversion_type: Type of conversion to perform ("mermaid", "bom", "json")
        output_format: Output format (depends on conversion_type)
        diagram_type: Type of diagram for Mermaid conversion
        recursive: Whether to search recursively in subdirectories
        max_workers: Maximum number of worker processes (None = auto)

    Returns:
        List of paths to output files
    """
    # Find schematic files
    schematic_patterns = ["*.sch", "*.kicad_sch"]
    schematic_files = find_files(input_dir, schematic_patterns, recursive)

    if not schematic_files:
        logger.warning(f"No schematic files found in {input_dir}")
        return []

    # Process files in parallel
    output_files = []

    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        if conversion_type.lower() == "mermaid":
            futures = [
                executor.submit(
                    process_schematic_to_mermaid,
                    schematic_file,
                    output_dir,
                    diagram_type,
                    output_format,
                )
                for schematic_file in schematic_files
            ]
        elif conversion_type.lower() == "bom":
            futures = [
                executor.submit(
                    process_schematic_to_bom, schematic_file, output_dir, output_format
                )
                for schematic_file in schematic_files
            ]
        elif conversion_type.lower() == "json":
            futures = [
                executor.submit(process_schematic_to_json, schematic_file, output_dir)
                for schematic_file in schematic_files
            ]
        else:
            raise ValueError(f"Unsupported conversion type: {conversion_type}")

        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                output_files.append(result)

    logger.info(f"Processed {len(output_files)} schematic files")
    return output_files


def batch_process_pcbs(
    input_dir: str,
    output_dir: str,
    conversion_type: str = "mermaid",
    output_format: str = "mmd",
    diagram_type: str = "flowchart",
    recursive: bool = False,
    max_workers: Optional[int] = None,
) -> List[str]:
    """
    Batch process PCB files in a directory.

    Args:
        input_dir: Directory containing PCB files
        output_dir: Directory to save output files
        conversion_type: Type of conversion to perform ("mermaid", "3d", "json")
        output_format: Output format (depends on conversion_type)
        diagram_type: Type of diagram for Mermaid conversion
        recursive: Whether to search recursively in subdirectories
        max_workers: Maximum number of worker processes (None = auto)

    Returns:
        List of paths to output files
    """
    # Find PCB files
    pcb_patterns = ["*.kicad_pcb"]
    pcb_files = find_files(input_dir, pcb_patterns, recursive)

    if not pcb_files:
        logger.warning(f"No PCB files found in {input_dir}")
        return []

    # Process files in parallel
    output_files = []

    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        if conversion_type.lower() == "mermaid":
            futures = [
                executor.submit(
                    process_pcb_to_mermaid,
                    pcb_file,
                    output_dir,
                    diagram_type,
                    output_format,
                )
                for pcb_file in pcb_files
            ]
        elif conversion_type.lower() == "3d":
            futures = [
                executor.submit(process_pcb_to_3d, pcb_file, output_dir, output_format)
                for pcb_file in pcb_files
            ]
        elif conversion_type.lower() == "json":
            futures = [
                executor.submit(process_pcb_to_json, pcb_file, output_dir)
                for pcb_file in pcb_files
            ]
        else:
            raise ValueError(f"Unsupported conversion type: {conversion_type}")

        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                output_files.append(result)

    logger.info(f"Processed {len(output_files)} PCB files")
    return output_files


def batch_process_hardware_files(
    input_dir: str,
    output_dir: str,
    file_types: List[str] = ["sch", "pcb"],
    conversion_types: Dict[str, str] = {"sch": "mermaid", "pcb": "mermaid"},
    output_formats: Dict[str, str] = {"sch": "mmd", "pcb": "mmd"},
    diagram_types: Dict[str, str] = {"sch": "flowchart", "pcb": "flowchart"},
    recursive: bool = False,
    max_workers: Optional[int] = None,
) -> Dict[str, List[str]]:
    """
    Batch process hardware files (schematics and PCBs) in a directory.

    Args:
        input_dir: Directory containing hardware files
        output_dir: Directory to save output files
        file_types: Types of files to process ("sch", "pcb")
        conversion_types: Conversion type for each file type
        output_formats: Output format for each file type
        diagram_types: Diagram type for Mermaid conversion
        recursive: Whether to search recursively in subdirectories
        max_workers: Maximum number of worker processes (None = auto)

    Returns:
        Dictionary mapping file types to lists of output files
    """
    results = {}

    if "sch" in file_types:
        sch_output_dir = os.path.join(output_dir, "schematics")
        results["sch"] = batch_process_schematics(
            input_dir,
            sch_output_dir,
            conversion_types.get("sch", "mermaid"),
            output_formats.get("sch", "mmd"),
            diagram_types.get("sch", "flowchart"),
            recursive,
            max_workers,
        )

    if "pcb" in file_types:
        pcb_output_dir = os.path.join(output_dir, "pcbs")
        results["pcb"] = batch_process_pcbs(
            input_dir,
            pcb_output_dir,
            conversion_types.get("pcb", "mermaid"),
            output_formats.get("pcb", "mmd"),
            diagram_types.get("pcb", "flowchart"),
            recursive,
            max_workers,
        )

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Batch process KiCad files")
    parser.add_argument(
        "--input-dir", required=True, help="Input directory containing KiCad files"
    )
    parser.add_argument(
        "--output-dir", required=True, help="Output directory for processed files"
    )
    parser.add_argument(
        "--file-types",
        nargs="+",
        default=["sch", "pcb"],
        choices=["sch", "pcb"],
        help="Types of files to process",
    )
    parser.add_argument(
        "--sch-conversion",
        default="mermaid",
        choices=["mermaid", "bom", "json"],
        help="Conversion type for schematic files",
    )
    parser.add_argument(
        "--pcb-conversion",
        default="mermaid",
        choices=["mermaid", "3d", "json"],
        help="Conversion type for PCB files",
    )
    parser.add_argument(
        "--sch-format", default="mmd", help="Output format for schematic conversion"
    )
    parser.add_argument(
        "--pcb-format", default="mmd", help="Output format for PCB conversion"
    )
    parser.add_argument(
        "--sch-diagram",
        default="flowchart",
        choices=["flowchart", "class", "er"],
        help="Diagram type for schematic Mermaid conversion",
    )
    parser.add_argument(
        "--pcb-diagram",
        default="flowchart",
        choices=["flowchart", "class", "er"],
        help="Diagram type for PCB Mermaid conversion",
    )
    parser.add_argument(
        "--recursive", action="store_true", help="Search recursively in subdirectories"
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=None,
        help="Maximum number of worker processes",
    )

    args = parser.parse_args()

    conversion_types = {"sch": args.sch_conversion, "pcb": args.pcb_conversion}

    output_formats = {"sch": args.sch_format, "pcb": args.pcb_format}

    diagram_types = {"sch": args.sch_diagram, "pcb": args.pcb_diagram}

    results = batch_process_hardware_files(
        args.input_dir,
        args.output_dir,
        args.file_types,
        conversion_types,
        output_formats,
        diagram_types,
        args.recursive,
        args.max_workers,
    )

    # Print summary
    print("\nProcessing Summary:")
    for file_type, output_files in results.items():
        print(f"{file_type.upper()} files processed: {len(output_files)}")
        for output_file in output_files[:5]:  # Show first 5 files
            print(f"  - {output_file}")
        if len(output_files) > 5:
            print(f"  - ... and {len(output_files) - 5} more files")
