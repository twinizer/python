#!/usr/bin/env python3
"""
Example script demonstrating software analysis functionality.

This example shows how to use the DependencyAnalyzer, ELFDecompiler,
and BinaryDisassembler classes to analyze software projects.
"""

import os
import sys
import argparse
from pathlib import Path

# Add the parent directory to the path so we can import twinizer
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from twinizer.software.analyze.dependency import DependencyAnalyzer
from twinizer.software.decompile.elf import ELFDecompiler
from twinizer.software.disassemble.binary import BinaryDisassembler


def analyze_dependencies(project_path, output_format="text", output_path=None):
    """Analyze dependencies in a software project."""
    print(f"\nAnalyzing dependencies in {project_path}...")
    
    # Create analyzer
    analyzer = DependencyAnalyzer(project_path)
    
    # Detect project type
    project_type = analyzer.detect_project_type()
    print(f"Detected project type: {project_type}")
    
    # Analyze dependencies
    dependencies = analyzer.analyze()
    
    # Display or save results
    if output_path:
        analyzer.save_results(dependencies, output_path, output_format)
        print(f"Dependency analysis saved to: {output_path}")
    else:
        # Display dependency tree
        analyzer.display_tree(dependencies)
    
    return dependencies


def decompile_binary(binary_path, output_format="c", output_path=None, 
                    decompiler="auto", function=None):
    """Decompile a binary file."""
    print(f"\nDecompiling binary {binary_path}...")
    
    # Create decompiler
    decompiler = ELFDecompiler(binary_path)
    
    # Get binary info
    binary_info = decompiler.get_binary_info()
    print(f"Binary architecture: {binary_info.get('architecture', 'unknown')}")
    print(f"Binary type: {binary_info.get('type', 'unknown')}")
    
    # Decompile binary
    result = decompiler.decompile(
        output_format=output_format,
        decompiler_tool=decompiler,
        function_name=function,
        output_path=output_path
    )
    
    # Display or save results
    if output_path:
        print(f"Decompiled code saved to: {output_path}")
    else:
        print("\nDecompiled code:")
        print(result[:1000] + "..." if len(result) > 1000 else result)
    
    return result


def disassemble_binary(binary_path, output_format="text", output_path=None, 
                      disassembler="auto", function=None):
    """Disassemble a binary file."""
    print(f"\nDisassembling binary {binary_path}...")
    
    # Create disassembler
    disassembler = BinaryDisassembler(binary_path)
    
    # Get binary info
    binary_info = disassembler.get_binary_info()
    print(f"Binary architecture: {binary_info.get('architecture', 'unknown')}")
    print(f"Binary type: {binary_info.get('type', 'unknown')}")
    
    # Disassemble binary
    result = disassembler.disassemble(
        output_format=output_format,
        disassembler_tool=disassembler,
        function_name=function,
        output_path=output_path
    )
    
    # Display or save results
    if output_path:
        print(f"Disassembled code saved to: {output_path}")
    else:
        print("\nDisassembled code:")
        print(result[:1000] + "..." if len(result) > 1000 else result)
    
    return result


def main():
    """Run the example."""
    parser = argparse.ArgumentParser(description="Software analysis example")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Dependency analysis parser
    deps_parser = subparsers.add_parser("analyze-deps", help="Analyze project dependencies")
    deps_parser.add_argument("project_path", help="Path to the project to analyze")
    deps_parser.add_argument("--format", choices=["text", "json", "xml", "dot"], default="text", 
                            help="Output format")
    deps_parser.add_argument("--output", help="Output file path")
    
    # Decompile parser
    decompile_parser = subparsers.add_parser("decompile", help="Decompile a binary file")
    decompile_parser.add_argument("binary_path", help="Path to the binary file")
    decompile_parser.add_argument("--format", choices=["c", "cpp", "pseudocode"], default="c", 
                                 help="Output format")
    decompile_parser.add_argument("--decompiler", choices=["ghidra", "ida", "retdec", "auto"], 
                                 default="auto", help="Decompiler to use")
    decompile_parser.add_argument("--function", help="Function to decompile")
    decompile_parser.add_argument("--output", help="Output file path")
    
    # Disassemble parser
    disasm_parser = subparsers.add_parser("disassemble", help="Disassemble a binary file")
    disasm_parser.add_argument("binary_path", help="Path to the binary file")
    disasm_parser.add_argument("--format", choices=["text", "html", "json"], default="text", 
                              help="Output format")
    disasm_parser.add_argument("--disassembler", choices=["objdump", "radare2", "capstone", "auto"], 
                              default="auto", help="Disassembler to use")
    disasm_parser.add_argument("--function", help="Function to disassemble")
    disasm_parser.add_argument("--output", help="Output file path")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == "analyze-deps":
            # Check if the project exists
            if not os.path.exists(args.project_path):
                print(f"Error: Project not found: {args.project_path}")
                return 1
            
            analyze_dependencies(
                project_path=args.project_path,
                output_format=args.format,
                output_path=args.output
            )
        
        elif args.command == "decompile":
            # Check if the binary exists
            if not os.path.exists(args.binary_path):
                print(f"Error: Binary not found: {args.binary_path}")
                return 1
            
            decompile_binary(
                binary_path=args.binary_path,
                output_format=args.format,
                output_path=args.output,
                decompiler=args.decompiler,
                function=args.function
            )
        
        elif args.command == "disassemble":
            # Check if the binary exists
            if not os.path.exists(args.binary_path):
                print(f"Error: Binary not found: {args.binary_path}")
                return 1
            
            disassemble_binary(
                binary_path=args.binary_path,
                output_format=args.format,
                output_path=args.output,
                disassembler=args.disassembler,
                function=args.function
            )
        
        return 0
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
