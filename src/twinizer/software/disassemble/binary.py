"""
Binary disassembler module.

This module provides functionality to disassemble binary files into assembly code
for various architectures.
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from rich.console import Console
from rich.syntax import Syntax

console = Console()


class BinaryDisassembler:
    """
    Disassembler for binary files.
    """

    def __init__(self, architecture: str = "auto", output_dir: Optional[str] = None):
        """
        Initialize the binary disassembler.

        Args:
            architecture: Target architecture ('x86', 'x86_64', 'arm', 'arm64', 'mips', 'auto')
            output_dir: Directory to save disassembled files
        """
        self.architecture = architecture
        self.output_dir = output_dir or tempfile.mkdtemp(prefix="twinizer_disasm_")

        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)

        # Check for disassembler tools
        self._check_tools()

    def _check_tools(self) -> Dict[str, bool]:
        """
        Check if required disassembler tools are available.

        Returns:
            Dictionary with tool names as keys and availability as values
        """
        tools = {
            "objdump": False,
            "radare2": False,
            "capstone": False,
        }

        # Check for objdump
        try:
            subprocess.run(
                ["objdump", "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            tools["objdump"] = True
        except FileNotFoundError:
            pass

        # Check for radare2
        try:
            subprocess.run(
                ["r2", "-version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            tools["radare2"] = True
        except FileNotFoundError:
            pass

        # Check for capstone (Python library)
        try:
            import capstone

            tools["capstone"] = True
        except ImportError:
            pass

        # Print available tools
        available_tools = [name for name, available in tools.items() if available]
        if available_tools:
            console.print(
                f"[green]Available disassemblers: {', '.join(available_tools)}[/green]"
            )
        else:
            console.print(
                "[yellow]Warning: No disassemblers found. Install objdump, radare2, or capstone.[/yellow]"
            )

        self.available_tools = tools
        return tools

    def detect_architecture(self, binary_path: str) -> str:
        """
        Detect the architecture of a binary file.

        Args:
            binary_path: Path to the binary file

        Returns:
            Detected architecture
        """
        if not os.path.exists(binary_path):
            raise FileNotFoundError(f"Binary file not found: {binary_path}")

        # Try using file command
        try:
            output = subprocess.check_output(["file", binary_path], text=True)

            # Parse output to determine architecture
            if "x86-64" in output or "x86_64" in output or "AMD64" in output:
                return "x86_64"
            elif "80386" in output or "i386" in output or "Intel 80386" in output:
                return "x86"
            elif "ARM" in output:
                if "aarch64" in output or "ARM64" in output:
                    return "arm64"
                else:
                    return "arm"
            elif "MIPS" in output:
                return "mips"
            elif "PowerPC" in output:
                return "powerpc"
            elif "SPARC" in output:
                return "sparc"
        except (subprocess.SubprocessError, FileNotFoundError):
            console.print(
                "[yellow]Warning: Could not detect architecture using 'file' command.[/yellow]"
            )

        # Fallback to checking ELF header if it's an ELF file
        try:
            with open(binary_path, "rb") as f:
                magic = f.read(4)
                if magic == b"\x7fELF":
                    # It's an ELF file, read e_machine field
                    f.seek(18)
                    machine = int.from_bytes(f.read(2), byteorder="little")

                    # Map e_machine to architecture
                    arch_map = {
                        3: "x86",
                        62: "x86_64",
                        40: "arm",
                        183: "arm64",
                        8: "mips",
                        20: "powerpc",
                        2: "sparc",
                    }

                    if machine in arch_map:
                        return arch_map[machine]
        except Exception:
            pass

        # If all else fails, return the default architecture
        return self.architecture if self.architecture != "auto" else "x86_64"

    def disassemble(
        self,
        binary_path: str,
        output_format: str = "text",
        start_address: Optional[int] = None,
        end_address: Optional[int] = None,
        function_name: Optional[str] = None,
    ) -> str:
        """
        Disassemble a binary file.

        Args:
            binary_path: Path to the binary file
            output_format: Output format ('text', 'html', 'json')
            start_address: Start address for disassembly (optional)
            end_address: End address for disassembly (optional)
            function_name: Function name to disassemble (optional)

        Returns:
            Disassembled code or path to output file
        """
        if not os.path.exists(binary_path):
            raise FileNotFoundError(f"Binary file not found: {binary_path}")

        # Auto-detect architecture if set to 'auto'
        if self.architecture == "auto":
            detected_arch = self.detect_architecture(binary_path)
            console.print(f"[green]Detected architecture: {detected_arch}[/green]")
            self.architecture = detected_arch

        # Choose the best available disassembler
        if self.available_tools["radare2"]:
            return self._disassemble_with_radare2(
                binary_path, output_format, start_address, end_address, function_name
            )
        elif self.available_tools["objdump"]:
            return self._disassemble_with_objdump(
                binary_path, output_format, start_address, end_address, function_name
            )
        elif self.available_tools["capstone"]:
            return self._disassemble_with_capstone(
                binary_path, output_format, start_address, end_address
            )
        else:
            raise RuntimeError(
                "No disassembler tools available. Install objdump, radare2, or capstone."
            )

    def _disassemble_with_objdump(
        self,
        binary_path: str,
        output_format: str,
        start_address: Optional[int] = None,
        end_address: Optional[int] = None,
        function_name: Optional[str] = None,
    ) -> str:
        """
        Disassemble a binary file using objdump.

        Args:
            binary_path: Path to the binary file
            output_format: Output format
            start_address: Start address for disassembly
            end_address: End address for disassembly
            function_name: Function name to disassemble

        Returns:
            Disassembled code or path to output file
        """
        # Create output file path
        base_name = os.path.basename(binary_path)
        output_name = f"{os.path.splitext(base_name)[0]}_objdump.asm"
        output_path = os.path.join(self.output_dir, output_name)

        # Build objdump command
        cmd = ["objdump", "--disassemble"]

        # Add architecture-specific options
        if self.architecture == "x86" or self.architecture == "x86_64":
            cmd.append("--x86-asm-syntax=intel")

        # Add function filter if specified
        if function_name:
            cmd.extend(["--disassemble-symbols", function_name])

        # Add binary path
        cmd.append(binary_path)

        try:
            # Run objdump
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            disassembly = result.stdout

            # Filter by address range if specified
            if start_address is not None or end_address is not None:
                filtered_lines = []
                in_range = start_address is None

                for line in disassembly.splitlines():
                    # Check for address in the line
                    if ":" in line and line[0].isdigit():
                        addr_str = line.split(":")[0].strip()
                        try:
                            addr = int(addr_str, 16)
                            if start_address is not None and addr >= start_address:
                                in_range = True
                            if end_address is not None and addr > end_address:
                                in_range = False
                        except ValueError:
                            pass

                    if in_range:
                        filtered_lines.append(line)

                disassembly = "\n".join(filtered_lines)

            # Save to file
            with open(output_path, "w") as f:
                f.write(disassembly)

            # Format output
            if output_format == "html":
                html_output = f"<pre><code class='assembly'>{disassembly}</code></pre>"
                html_path = os.path.join(
                    self.output_dir, f"{os.path.splitext(base_name)[0]}_objdump.html"
                )
                with open(html_path, "w") as f:
                    f.write(html_output)
                return html_path
            elif output_format == "json":
                import json

                json_output = {
                    "tool": "objdump",
                    "architecture": self.architecture,
                    "binary": binary_path,
                    "disassembly": disassembly.splitlines(),
                }
                json_path = os.path.join(
                    self.output_dir, f"{os.path.splitext(base_name)[0]}_objdump.json"
                )
                with open(json_path, "w") as f:
                    json.dump(json_output, f, indent=2)
                return json_path
            else:
                return output_path

        except subprocess.CalledProcessError as e:
            console.print(f"[red]Error running objdump: {e}[/red]")
            console.print(f"[red]Stderr: {e.stderr}[/red]")
            return f"Error: objdump disassembly failed"

    def _disassemble_with_radare2(
        self,
        binary_path: str,
        output_format: str,
        start_address: Optional[int] = None,
        end_address: Optional[int] = None,
        function_name: Optional[str] = None,
    ) -> str:
        """
        Disassemble a binary file using radare2.

        Args:
            binary_path: Path to the binary file
            output_format: Output format
            start_address: Start address for disassembly
            end_address: End address for disassembly
            function_name: Function name to disassemble

        Returns:
            Disassembled code or path to output file
        """
        # Create output file path
        base_name = os.path.basename(binary_path)
        output_name = f"{os.path.splitext(base_name)[0]}_radare2.asm"
        output_path = os.path.join(self.output_dir, output_name)

        # Build radare2 script
        r2_script = []

        # Set architecture if specified
        if self.architecture != "auto":
            if self.architecture == "x86_64":
                r2_script.append("e asm.arch=x86")
                r2_script.append("e asm.bits=64")
            elif self.architecture == "x86":
                r2_script.append("e asm.arch=x86")
                r2_script.append("e asm.bits=32")
            elif self.architecture == "arm":
                r2_script.append("e asm.arch=arm")
                r2_script.append("e asm.bits=32")
            elif self.architecture == "arm64":
                r2_script.append("e asm.arch=arm")
                r2_script.append("e asm.bits=64")
            elif self.architecture == "mips":
                r2_script.append("e asm.arch=mips")

        # Set disassembly options
        r2_script.append("e asm.syntax=intel")  # Use Intel syntax for x86
        r2_script.append("e asm.lines=true")
        r2_script.append("e asm.comments=true")

        # Analyze the binary
        r2_script.append("aa")  # Analyze all

        # Disassemble specific function if specified
        if function_name:
            r2_script.append(f"s sym.{function_name}")
            r2_script.append("pdf")  # Print disassembly of function
        # Disassemble specific address range if specified
        elif start_address is not None:
            r2_script.append(f"s {start_address}")
            if end_address is not None:
                size = end_address - start_address
                r2_script.append(f"pD {size}")  # Print disassembly with size
            else:
                r2_script.append("pdf")  # Print disassembly of function
        # Disassemble all functions
        else:
            r2_script.append("afl~[0]")  # List all functions
            r2_script.append("pdf @@ fcn.*")  # Disassemble all functions

        # Save script to file
        script_path = os.path.join(self.output_dir, "r2_script.txt")
        with open(script_path, "w") as f:
            f.write("\n".join(r2_script))

        try:
            # Run radare2 with the script
            cmd = ["r2", "-q", "-i", script_path, binary_path]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            disassembly = result.stdout

            # Save to file
            with open(output_path, "w") as f:
                f.write(disassembly)

            # Format output
            if output_format == "html":
                html_output = f"<pre><code class='assembly'>{disassembly}</code></pre>"
                html_path = os.path.join(
                    self.output_dir, f"{os.path.splitext(base_name)[0]}_radare2.html"
                )
                with open(html_path, "w") as f:
                    f.write(html_output)
                return html_path
            elif output_format == "json":
                # Run radare2 with JSON output
                json_cmd = ["r2", "-q", "-j", "-i", script_path, binary_path]
                json_result = subprocess.run(
                    json_cmd, capture_output=True, text=True, check=True
                )

                json_path = os.path.join(
                    self.output_dir, f"{os.path.splitext(base_name)[0]}_radare2.json"
                )
                with open(json_path, "w") as f:
                    f.write(json_result.stdout)
                return json_path
            else:
                return output_path

        except subprocess.CalledProcessError as e:
            console.print(f"[red]Error running radare2: {e}[/red]")
            console.print(f"[red]Stderr: {e.stderr}[/red]")
            return f"Error: radare2 disassembly failed"

    def _disassemble_with_capstone(
        self,
        binary_path: str,
        output_format: str,
        start_address: Optional[int] = None,
        end_address: Optional[int] = None,
    ) -> str:
        """
        Disassemble a binary file using Capstone.

        Args:
            binary_path: Path to the binary file
            output_format: Output format
            start_address: Start address for disassembly
            end_address: End address for disassembly

        Returns:
            Disassembled code or path to output file
        """
        try:
            import capstone
        except ImportError:
            raise ImportError(
                "Capstone is not installed. Install it with 'pip install capstone'."
            )

        # Create output file path
        base_name = os.path.basename(binary_path)
        output_name = f"{os.path.splitext(base_name)[0]}_capstone.asm"
        output_path = os.path.join(self.output_dir, output_name)

        # Read binary file
        with open(binary_path, "rb") as f:
            binary_data = f.read()

        # Set up Capstone
        if self.architecture == "x86_64":
            md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
        elif self.architecture == "x86":
            md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
        elif self.architecture == "arm":
            md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_ARM)
        elif self.architecture == "arm64":
            md = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
        elif self.architecture == "mips":
            md = capstone.Cs(capstone.CS_ARCH_MIPS, capstone.CS_MODE_MIPS32)
        else:
            raise ValueError(
                f"Unsupported architecture for Capstone: {self.architecture}"
            )

        # Enable detailed output
        md.detail = True

        # Determine start and end offsets
        start_offset = 0
        end_offset = len(binary_data)

        if start_address is not None:
            start_offset = max(0, start_address)
        if end_address is not None:
            end_offset = min(len(binary_data), end_address)

        # Disassemble
        disassembly_lines = []
        for i, (address, size, mnemonic, op_str) in enumerate(
            md.disasm_lite(binary_data[start_offset:end_offset], start_offset)
        ):
            disassembly_lines.append(f"0x{address:08x}:\t{mnemonic}\t{op_str}")

        disassembly = "\n".join(disassembly_lines)

        # Save to file
        with open(output_path, "w") as f:
            f.write(disassembly)

        # Format output
        if output_format == "html":
            html_output = f"<pre><code class='assembly'>{disassembly}</code></pre>"
            html_path = os.path.join(
                self.output_dir, f"{os.path.splitext(base_name)[0]}_capstone.html"
            )
            with open(html_path, "w") as f:
                f.write(html_output)
            return html_path
        elif output_format == "json":
            import json

            json_output = {
                "tool": "capstone",
                "architecture": self.architecture,
                "binary": binary_path,
                "instructions": [
                    {
                        "address": f"0x{address:08x}",
                        "mnemonic": mnemonic,
                        "operands": op_str,
                    }
                    for address, size, mnemonic, op_str in md.disasm_lite(
                        binary_data[start_offset:end_offset], start_offset
                    )
                ],
            }
            json_path = os.path.join(
                self.output_dir, f"{os.path.splitext(base_name)[0]}_capstone.json"
            )
            with open(json_path, "w") as f:
                json.dump(json_output, f, indent=2)
            return json_path
        else:
            return output_path


def disassemble_binary(
    binary_path: str,
    architecture: str = "auto",
    output_format: str = "text",
    output_dir: Optional[str] = None,
    start_address: Optional[int] = None,
    end_address: Optional[int] = None,
    function_name: Optional[str] = None,
) -> str:
    """
    Disassemble a binary file.

    Args:
        binary_path: Path to the binary file
        architecture: Target architecture ('x86', 'x86_64', 'arm', 'arm64', 'mips', 'auto')
        output_format: Output format ('text', 'html', 'json')
        output_dir: Directory to save disassembled files
        start_address: Start address for disassembly
        end_address: End address for disassembly
        function_name: Function name to disassemble

    Returns:
        Path to the disassembled file
    """
    disassembler = BinaryDisassembler(architecture=architecture, output_dir=output_dir)

    return disassembler.disassemble(
        binary_path=binary_path,
        output_format=output_format,
        start_address=start_address,
        end_address=end_address,
        function_name=function_name,
    )
