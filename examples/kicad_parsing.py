#!/usr/bin/env python3
"""
Example script demonstrating KiCad file parsing and conversion.

This example shows how to use the KiCad parsers to extract information
from KiCad schematic and PCB files, and convert them to other formats.
"""

import os
import sys
import argparse
import json
from pathlib import Path

# Add the parent directory to the path so we can import twinizer
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from twinizer.hardware.kicad.sch_parser import SchematicParser
from twinizer.hardware.kicad.pcb_parser import PCBParser
from twinizer.hardware.kicad.converters import (
    schematic_to_mermaid, pcb_to_mermaid, generate_bom
)


def parse_schematic(schematic_path, output_format="json", output_path=None):
    """Parse a KiCad schematic file."""
    print(f"\nParsing KiCad schematic {schematic_path}...")
    
    # Create parser
    parser = SchematicParser(schematic_path)
    
    # Parse schematic
    schematic_data = parser.parse()
    
    # Display summary
    components = schematic_data.get("components", [])
    nets = schematic_data.get("nets", [])
    print(f"Found {len(components)} components and {len(nets)} nets")
    
    # Display or save results
    if output_path:
        if output_format == "json":
            with open(output_path, "w") as f:
                json.dump(schematic_data, f, indent=2)
        elif output_format == "mermaid":
            diagram = schematic_to_mermaid(schematic_data)
            with open(output_path, "w") as f:
                f.write(diagram)
        elif output_format == "bom":
            bom_data = generate_bom(schematic_data)
            with open(output_path, "w") as f:
                json.dump(bom_data, f, indent=2)
        
        print(f"Schematic data saved to: {output_path}")
    else:
        if output_format == "json":
            print("\nSchematic data:")
            print(json.dumps(schematic_data, indent=2)[:1000] + "..." 
                  if len(json.dumps(schematic_data, indent=2)) > 1000 
                  else json.dumps(schematic_data, indent=2))
        elif output_format == "mermaid":
            diagram = schematic_to_mermaid(schematic_data)
            print("\nMermaid diagram:")
            print(diagram[:1000] + "..." if len(diagram) > 1000 else diagram)
        elif output_format == "bom":
            bom_data = generate_bom(schematic_data)
            print("\nBill of Materials:")
            print(json.dumps(bom_data, indent=2))
    
    return schematic_data


def parse_pcb(pcb_path, output_format="json", output_path=None):
    """Parse a KiCad PCB file."""
    print(f"\nParsing KiCad PCB {pcb_path}...")
    
    # Create parser
    parser = PCBParser(pcb_path)
    
    # Parse PCB
    pcb_data = parser.parse()
    
    # Display summary
    modules = pcb_data.get("modules", [])
    tracks = pcb_data.get("tracks", [])
    print(f"Found {len(modules)} modules and {len(tracks)} tracks")
    
    # Display or save results
    if output_path:
        if output_format == "json":
            with open(output_path, "w") as f:
                json.dump(pcb_data, f, indent=2)
        elif output_format == "mermaid":
            diagram = pcb_to_mermaid(pcb_data)
            with open(output_path, "w") as f:
                f.write(diagram)
        
        print(f"PCB data saved to: {output_path}")
    else:
        if output_format == "json":
            print("\nPCB data:")
            print(json.dumps(pcb_data, indent=2)[:1000] + "..." 
                  if len(json.dumps(pcb_data, indent=2)) > 1000 
                  else json.dumps(pcb_data, indent=2))
        elif output_format == "mermaid":
            diagram = pcb_to_mermaid(pcb_data)
            print("\nMermaid diagram:")
            print(diagram[:1000] + "..." if len(diagram) > 1000 else diagram)
    
    return pcb_data


def main():
    """Run the example."""
    parser = argparse.ArgumentParser(description="KiCad file parsing example")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Schematic parser
    sch_parser = subparsers.add_parser("parse-sch", help="Parse a KiCad schematic file")
    sch_parser.add_argument("schematic_path", help="Path to the schematic file")
    sch_parser.add_argument("--format", choices=["json", "mermaid", "bom"], default="json", 
                           help="Output format")
    sch_parser.add_argument("--output", help="Output file path")
    
    # PCB parser
    pcb_parser = subparsers.add_parser("parse-pcb", help="Parse a KiCad PCB file")
    pcb_parser.add_argument("pcb_path", help="Path to the PCB file")
    pcb_parser.add_argument("--format", choices=["json", "mermaid"], default="json", 
                           help="Output format")
    pcb_parser.add_argument("--output", help="Output file path")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == "parse-sch":
            # Check if the schematic exists
            if not os.path.exists(args.schematic_path):
                print(f"Error: Schematic not found: {args.schematic_path}")
                return 1
            
            parse_schematic(
                schematic_path=args.schematic_path,
                output_format=args.format,
                output_path=args.output
            )
        
        elif args.command == "parse-pcb":
            # Check if the PCB exists
            if not os.path.exists(args.pcb_path):
                print(f"Error: PCB not found: {args.pcb_path}")
                return 1
            
            parse_pcb(
                pcb_path=args.pcb_path,
                output_format=args.format,
                output_path=args.output
            )
        
        return 0
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
