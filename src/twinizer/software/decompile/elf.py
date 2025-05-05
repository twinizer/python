"""
ELF file decompiler module.

This module provides functionality to decompile ELF (Executable and Linkable Format) files
into higher-level representations like C or assembly code.
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class ELFDecompiler:
    """
    Decompiler for ELF (Executable and Linkable Format) files.
    """

    def __init__(
        self,
        use_ghidra: bool = True,
        use_ida: bool = False,
        use_retdec: bool = False,
        output_dir: Optional[str] = None,
    ):
        """
        Initialize the ELF decompiler.

        Args:
            use_ghidra: Whether to use Ghidra for decompilation
            use_ida: Whether to use IDA Pro for decompilation
            use_retdec: Whether to use RetDec for decompilation
            output_dir: Directory to save decompiled files
        """
        self.use_ghidra = use_ghidra
        self.use_ida = use_ida
        self.use_retdec = use_retdec
        self.output_dir = output_dir or tempfile.mkdtemp(prefix="twinizer_decompile_")

        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)

        # Check for decompiler availability
        self._check_decompilers()

    def _check_decompilers(self):
        """Check if the selected decompilers are available."""
        if self.use_ghidra:
            # Check for Ghidra
            ghidra_path = os.environ.get("GHIDRA_HOME")
            if not ghidra_path or not os.path.exists(ghidra_path):
                console.print(
                    "[yellow]Warning: Ghidra not found. Set GHIDRA_HOME environment variable.[/yellow]"
                )
                self.use_ghidra = False

        if self.use_ida:
            # Check for IDA Pro
            ida_path = os.environ.get("IDA_HOME")
            if not ida_path or not os.path.exists(ida_path):
                console.print(
                    "[yellow]Warning: IDA Pro not found. Set IDA_HOME environment variable.[/yellow]"
                )
                self.use_ida = False

        if self.use_retdec:
            # Check for RetDec
            try:
                subprocess.run(
                    ["retdec-decompiler", "--version"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )
            except FileNotFoundError:
                console.print(
                    "[yellow]Warning: RetDec not found. Make sure it's installed and in your PATH.[/yellow]"
                )
                self.use_retdec = False

        if not any([self.use_ghidra, self.use_ida, self.use_retdec]):
            console.print(
                "[yellow]Warning: No decompilers available. Results will be limited.[/yellow]"
            )

    def decompile(
        self,
        elf_path: str,
        output_format: str = "c",
        function_name: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Decompile an ELF file.

        Args:
            elf_path: Path to the ELF file
            output_format: Output format ('c', 'assembly', or 'pseudocode')
            function_name: Specific function to decompile, or None for the entire file

        Returns:
            Dictionary with decompiler names as keys and file paths as values
        """
        if not os.path.exists(elf_path):
            raise FileNotFoundError(f"ELF file not found: {elf_path}")

        results = {}

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # Use Ghidra if available
            if self.use_ghidra:
                task = progress.add_task(
                    "[green]Decompiling with Ghidra...", total=None
                )
                output_path = self._decompile_with_ghidra(
                    elf_path, output_format, function_name
                )
                results["ghidra"] = output_path
                progress.update(
                    task,
                    completed=True,
                    description=f"[green]Ghidra decompilation complete: {output_path}",
                )

            # Use IDA Pro if available
            if self.use_ida:
                task = progress.add_task(
                    "[green]Decompiling with IDA Pro...", total=None
                )
                output_path = self._decompile_with_ida(
                    elf_path, output_format, function_name
                )
                results["ida"] = output_path
                progress.update(
                    task,
                    completed=True,
                    description=f"[green]IDA Pro decompilation complete: {output_path}",
                )

            # Use RetDec if available
            if self.use_retdec:
                task = progress.add_task(
                    "[green]Decompiling with RetDec...", total=None
                )
                output_path = self._decompile_with_retdec(
                    elf_path, output_format, function_name
                )
                results["retdec"] = output_path
                progress.update(
                    task,
                    completed=True,
                    description=f"[green]RetDec decompilation complete: {output_path}",
                )

        return results

    def _decompile_with_ghidra(
        self, elf_path: str, output_format: str, function_name: Optional[str] = None
    ) -> str:
        """
        Decompile an ELF file using Ghidra.

        Args:
            elf_path: Path to the ELF file
            output_format: Output format
            function_name: Specific function to decompile

        Returns:
            Path to the decompiled file
        """
        # Get Ghidra path from environment
        ghidra_path = os.environ.get("GHIDRA_HOME")
        if not ghidra_path:
            raise EnvironmentError("GHIDRA_HOME environment variable not set")

        # Create output file path
        base_name = os.path.basename(elf_path)
        output_name = f"{os.path.splitext(base_name)[0]}_ghidra"
        if function_name:
            output_name += f"_{function_name}"

        if output_format == "c":
            output_name += ".c"
        elif output_format == "assembly":
            output_name += ".asm"
        else:
            output_name += ".txt"

        output_path = os.path.join(self.output_dir, output_name)

        # Create Ghidra script to run headlessly
        script_content = self._generate_ghidra_script(
            output_path, output_format, function_name
        )
        script_path = os.path.join(self.output_dir, "ghidra_decompile.py")

        with open(script_path, "w") as f:
            f.write(script_content)

        # Run Ghidra headlessly
        project_path = os.path.join(self.output_dir, "ghidra_project")
        os.makedirs(project_path, exist_ok=True)

        ghidra_headless = os.path.join(ghidra_path, "support", "analyzeHeadless")
        cmd = [
            ghidra_headless,
            project_path,
            "TwinizerProject",
            "-import",
            elf_path,
            "-postScript",
            script_path,
            "-scriptPath",
            self.output_dir,
            "-deleteProject",
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Error running Ghidra: {e}[/red]")
            console.print(f"[red]Stderr: {e.stderr.decode()}[/red]")
            return "Error: Ghidra decompilation failed"

        return output_path

    def _generate_ghidra_script(
        self, output_path: str, output_format: str, function_name: Optional[str] = None
    ) -> str:
        """
        Generate a Ghidra script for decompilation.

        Args:
            output_path: Path to save the output
            output_format: Output format
            function_name: Specific function to decompile

        Returns:
            Ghidra script content
        """
        # This is a simplified script template
        script = f"""# Ghidra decompilation script
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

# Get current program
program = getCurrentProgram()
monitor = ConsoleTaskMonitor()

# Set up decompiler
decompiler = DecompInterface()
decompiler.openProgram(program)

# Open output file
output_file = open("{output_path}", "w")

"""

        if function_name:
            script += f"""
# Find specific function
symbol = getSymbol("{function_name}", None)
if symbol is None:
    print("Function {function_name} not found")
    output_file.write("Function {function_name} not found")
    output_file.close()
    exit(0)

function = symbol.getObject()
"""
        else:
            script += """
# Process all functions
function_manager = program.getFunctionManager()
functions = function_manager.getFunctions(True)
"""

        if output_format == "c":
            if function_name:
                script += """
# Decompile the function
result = decompiler.decompileFunction(function, 30, monitor)
if result.decompileCompleted():
    output_file.write(result.getDecompiledFunction().getC())
else:
    output_file.write(f"// Failed to decompile {function.getName()}")
"""
            else:
                script += """
# Decompile all functions
for function in functions:
    result = decompiler.decompileFunction(function, 30, monitor)
    if result.decompileCompleted():
        output_file.write(f"// Function: {function.getName()}\\n")
        output_file.write(result.getDecompiledFunction().getC())
        output_file.write("\\n\\n")
    else:
        output_file.write(f"// Failed to decompile {function.getName()}\\n\\n")
"""
        elif output_format == "assembly":
            if function_name:
                script += """
# Get assembly for the function
listing = program.getListing()
codeUnits = listing.getCodeUnits(function.getBody(), True)
while codeUnits.hasNext():
    codeUnit = codeUnits.next()
    output_file.write(f"{codeUnit.getAddress()}: {codeUnit}\\n")
"""
            else:
                script += """
# Get assembly for all functions
listing = program.getListing()
for function in functions:
    output_file.write(f"// Function: {function.getName()}\\n")
    codeUnits = listing.getCodeUnits(function.getBody(), True)
    while codeUnits.hasNext():
        codeUnit = codeUnits.next()
        output_file.write(f"{codeUnit.getAddress()}: {codeUnit}\\n")
    output_file.write("\\n\\n")
"""

        script += """
# Close output file
output_file.close()
print(f"Decompilation complete, output saved to {output_path}")
"""

        return script

    def _decompile_with_ida(
        self, elf_path: str, output_format: str, function_name: Optional[str] = None
    ) -> str:
        """
        Decompile an ELF file using IDA Pro.

        Args:
            elf_path: Path to the ELF file
            output_format: Output format
            function_name: Specific function to decompile

        Returns:
            Path to the decompiled file
        """
        # Implementation would depend on IDA Pro's command-line interface
        # This is a placeholder that would need to be implemented based on IDA's API
        return f"IDA Pro decompilation not implemented yet"

    def _decompile_with_retdec(
        self, elf_path: str, output_format: str, function_name: Optional[str] = None
    ) -> str:
        """
        Decompile an ELF file using RetDec.

        Args:
            elf_path: Path to the ELF file
            output_format: Output format
            function_name: Specific function to decompile

        Returns:
            Path to the decompiled file
        """
        # Create output file path
        base_name = os.path.basename(elf_path)
        output_name = f"{os.path.splitext(base_name)[0]}_retdec"
        output_path = os.path.join(self.output_dir, output_name)

        # Build RetDec command
        cmd = ["retdec-decompiler", elf_path, "-o", output_path]

        if function_name:
            cmd.extend(["--select-functions", function_name])

        if output_format == "assembly":
            cmd.append("--emit-asm")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Error running RetDec: {e}[/red]")
            console.print(f"[red]Stderr: {e.stderr.decode()}[/red]")
            return "Error: RetDec decompilation failed"

        # RetDec outputs .c and .dsm (assembly) files
        if output_format == "c":
            return f"{output_path}.c"
        elif output_format == "assembly":
            return f"{output_path}.dsm"
        else:
            return f"{output_path}.c"


def decompile_elf(
    elf_path: str,
    output_dir: Optional[str] = None,
    output_format: str = "c",
    function_name: Optional[str] = None,
    use_ghidra: bool = True,
    use_ida: bool = False,
    use_retdec: bool = False,
) -> Dict[str, str]:
    """
    Decompile an ELF file using available decompilers.

    Args:
        elf_path: Path to the ELF file
        output_dir: Directory to save decompiled files
        output_format: Output format ('c', 'assembly', or 'pseudocode')
        function_name: Specific function to decompile
        use_ghidra: Whether to use Ghidra
        use_ida: Whether to use IDA Pro
        use_retdec: Whether to use RetDec

    Returns:
        Dictionary with decompiler names as keys and file paths as values
    """
    decompiler = ELFDecompiler(
        use_ghidra=use_ghidra,
        use_ida=use_ida,
        use_retdec=use_retdec,
        output_dir=output_dir,
    )

    return decompiler.decompile(
        elf_path=elf_path, output_format=output_format, function_name=function_name
    )
