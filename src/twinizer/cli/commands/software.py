"""
Software analysis command module.

This module provides CLI commands for software analysis, decompilation,
and disassembly operations.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.table import Table

from twinizer.software.analyze.dependency import DependencyAnalyzer
from twinizer.software.decompile.elf import ELFDecompiler
from twinizer.software.disassemble.binary import BinaryDisassembler

console = Console()


@click.group(
    name="software", help="Commands for software analysis and reverse engineering"
)
def software_group():
    """Software analysis command group."""
    pass


@software_group.command(name="analyze-deps", help="Analyze project dependencies")
@click.argument("project_path", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "yaml", "text"]),
    default="text",
    help="Output format",
)
@click.option("--visualize", "-v", is_flag=True, help="Visualize dependencies")
def analyze_dependencies(
    project_path: str,
    output: Optional[str] = None,
    format: str = "text",
    visualize: bool = False,
):
    """
    Analyze dependencies in a software project.

    Args:
        project_path: Path to the project to analyze
        output: Output file path (optional)
        format: Output format (json, yaml, or text)
        visualize: Visualize dependencies
    """
    try:
        # Create analyzer
        analyzer = DependencyAnalyzer(project_path)

        # Analyze dependencies
        if visualize:
            analyzer.visualize()
            return

        analysis = analyzer.analyze()

        # Format the output
        if format == "json":
            import json

            result = json.dumps(analysis, indent=2)
        elif format == "yaml":
            import yaml

            result = yaml.dump(analysis, default_flow_style=False)
        else:  # text
            result = _format_dependency_analysis(analysis)

        # Output the result
        if output:
            with open(output, "w") as f:
                f.write(result)
            console.print(f"[green]Dependency analysis saved to {output}[/green]")
        else:
            console.print(result)

    except Exception as e:
        console.print(f"[red]Error analyzing dependencies: {e}[/red]")
        import traceback

        console.print(traceback.format_exc())
        sys.exit(1)


@software_group.command(name="decompile", help="Decompile binary file")
@click.argument("binary_path", type=click.Path(exists=True))
@click.option("--output-dir", "-o", type=click.Path(), help="Output directory")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["c", "assembly", "pseudocode"]),
    default="c",
    help="Output format",
)
@click.option("--function", help="Specific function to decompile")
@click.option("--use-ghidra/--no-ghidra", default=True, help="Use Ghidra decompiler")
@click.option("--use-ida/--no-ida", default=False, help="Use IDA Pro decompiler")
@click.option("--use-retdec/--no-retdec", default=False, help="Use RetDec decompiler")
def decompile_binary(
    binary_path: str,
    output_dir: Optional[str] = None,
    format: str = "c",
    function: Optional[str] = None,
    use_ghidra: bool = True,
    use_ida: bool = False,
    use_retdec: bool = False,
):
    """
    Decompile a binary file.

    Args:
        binary_path: Path to the binary file
        output_dir: Output directory (optional)
        format: Output format (c, assembly, or pseudocode)
        function: Specific function to decompile (optional)
        use_ghidra: Use Ghidra decompiler
        use_ida: Use IDA Pro decompiler
        use_retdec: Use RetDec decompiler
    """
    try:
        # Create decompiler
        decompiler = ELFDecompiler(
            use_ghidra=use_ghidra,
            use_ida=use_ida,
            use_retdec=use_retdec,
            output_dir=output_dir,
        )

        # Decompile binary
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[green]Decompiling binary...", total=None)

            results = decompiler.decompile(
                elf_path=binary_path, output_format=format, function_name=function
            )

            progress.update(
                task, completed=True, description=f"[green]Decompilation complete"
            )

        # Display results
        console.print("[bold green]Decompilation Results:[/bold green]")
        for tool, output_path in results.items():
            console.print(f"[bold]{tool}:[/bold] {output_path}")

            # Show a preview of the decompiled code if available
            if os.path.exists(output_path) and os.path.isfile(output_path):
                with open(output_path, "r") as f:
                    content = f.read()

                # Truncate if too long
                if len(content) > 1000:
                    content = content[:1000] + "\n... (truncated)"

                syntax = Syntax(
                    content,
                    "c" if format == "c" else "asm",
                    theme="monokai",
                    line_numbers=True,
                )
                console.print(syntax)

    except Exception as e:
        console.print(f"[red]Error decompiling binary: {e}[/red]")
        import traceback

        console.print(traceback.format_exc())
        sys.exit(1)


@software_group.command(name="disassemble", help="Disassemble binary file")
@click.argument("binary_path", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["text", "html", "json"]),
    default="text",
    help="Output format",
)
@click.option(
    "--architecture",
    "-a",
    type=click.Choice(["auto", "x86", "x86_64", "arm", "arm64", "mips"]),
    default="auto",
    help="Target architecture",
)
@click.option("--function", help="Specific function to disassemble")
@click.option("--start-address", type=int, help="Start address for disassembly")
@click.option("--end-address", type=int, help="End address for disassembly")
def disassemble_binary_cmd(
    binary_path: str,
    output: Optional[str] = None,
    format: str = "text",
    architecture: str = "auto",
    function: Optional[str] = None,
    start_address: Optional[int] = None,
    end_address: Optional[int] = None,
):
    """
    Disassemble a binary file.

    Args:
        binary_path: Path to the binary file
        output: Output file path (optional)
        format: Output format (text, html, or json)
        architecture: Target architecture
        function: Specific function to disassemble (optional)
        start_address: Start address for disassembly (optional)
        end_address: End address for disassembly (optional)
    """
    try:
        # Create disassembler
        disassembler = BinaryDisassembler(
            architecture=architecture,
            output_dir=os.path.dirname(output) if output else None,
        )

        # Disassemble binary
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[green]Disassembling binary...", total=None)

            result = disassembler.disassemble(
                binary_path=binary_path,
                output_format=format,
                start_address=start_address,
                end_address=end_address,
                function_name=function,
            )

            progress.update(
                task, completed=True, description=f"[green]Disassembly complete"
            )

        # Display result
        console.print(f"[bold green]Disassembly saved to:[/bold green] {result}")

        # Show a preview of the disassembled code if available
        if os.path.exists(result) and os.path.isfile(result):
            with open(result, "r") as f:
                content = f.read()

            # Truncate if too long
            if len(content) > 1000:
                content = content[:1000] + "\n... (truncated)"

            syntax = Syntax(content, "asm", theme="monokai", line_numbers=True)
            console.print(syntax)

    except Exception as e:
        console.print(f"[red]Error disassembling binary: {e}[/red]")
        import traceback

        console.print(traceback.format_exc())
        sys.exit(1)


def _format_dependency_analysis(analysis: Dict) -> str:
    """Format dependency analysis as text."""
    result = f"Project: {analysis['project_path']}\n"
    result += f"Language: {analysis['language']}\n"
    result += f"Build System: {analysis['build_system']}\n\n"

    # Dependencies
    table = Table(title="Dependencies")
    table.add_column("Name")
    table.add_column("Version")

    for name, version in sorted(analysis["dependencies"].items()):
        table.add_row(name, str(version))

    result += str(table)

    return result
