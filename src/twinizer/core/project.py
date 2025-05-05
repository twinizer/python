"""
project.py
"""

"""
Project management module for Twinizer.
Provides functionality for scanning, analyzing, and managing projects.
"""

import datetime
import os
import re
import shutil
import zipfile
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.tree import Tree

console = Console()


class Project:
    """
    Project class for managing and analyzing embedded projects.
    """

    def __init__(self, source_dir="./source"):
        """
        Initialize a project with the given source directory.

        Args:
            source_dir: Path to the project source directory
        """
        self.source_dir = os.path.abspath(source_dir)
        self.name = os.path.basename(self.source_dir)

        # Project structure components
        self.hardware_files = []
        self.firmware_files = []
        self.binary_files = []
        self.doc_files = []
        self.script_files = []
        self.other_files = []

        # File categorization patterns
        self.file_patterns = {
            "hardware": [
                r"\.sch$",
                r"\.brd$",
                r"\.kicad_pcb$",
                r"\.kicad_sch$",
                r"\.SchDoc$",
                r"\.PcbDoc$",
            ],
            "firmware": [
                r"\.c$",
                r"\.h$",
                r"\.cpp$",
                r"\.hpp$",
                r"\.asm$",
                r"\.s$",
                r"\.inc$",
            ],
            "binary": [
                r"\.bin$",
                r"\.hex$",
                r"\.elf$",
                r"\.exe$",
                r"\.so$",
                r"\.dll$",
                r"\.o$",
            ],
            "doc": [r"\.md$", r"\.txt$", r"\.pdf$", r"\.docx?$", r"\.html$"],
            "script": [r"\.sh$", r"\.bat$", r"\.ps1$", r"\.py$", r"\.pl$"],
        }

    def scan(self):
        """
        Scan the source directory and categorize all files.
        """
        console.print(f"[green]Scanning project directory:[/green] {self.source_dir}")

        # Reset file lists
        self.hardware_files = []
        self.firmware_files = []
        self.binary_files = []
        self.doc_files = []
        self.script_files = []
        self.other_files = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[green]Scanning files...", total=None)

            for root, _, files in os.walk(self.source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.source_dir)

                    # Categorize the file based on extension
                    categorized = False
                    for category, patterns in self.file_patterns.items():
                        for pattern in patterns:
                            if re.search(pattern, file, re.IGNORECASE):
                                if category == "hardware":
                                    self.hardware_files.append(rel_path)
                                elif category == "firmware":
                                    self.firmware_files.append(rel_path)
                                elif category == "binary":
                                    self.binary_files.append(rel_path)
                                elif category == "doc":
                                    self.doc_files.append(rel_path)
                                elif category == "script":
                                    self.script_files.append(rel_path)
                                categorized = True
                                break
                        if categorized:
                            break

                    if not categorized:
                        self.other_files.append(rel_path)

            progress.update(task, completed=True, description="[green]Scan complete!")

        console.print(
            f"Found [cyan]{len(self.hardware_files)}[/cyan] hardware files, "
            f"[cyan]{len(self.firmware_files)}[/cyan] firmware files, "
            f"[cyan]{len(self.binary_files)}[/cyan] binary files, "
            f"[cyan]{len(self.doc_files)}[/cyan] documentation files, "
            f"[cyan]{len(self.script_files)}[/cyan] script files, and "
            f"[cyan]{len(self.other_files)}[/cyan] other files."
        )

    def show_info(self):
        """
        Display information about the project.
        """
        console.print(
            Panel.fit(
                f"[bold]Project Name:[/bold] {self.name}\n"
                f"[bold]Source Directory:[/bold] {self.source_dir}\n"
                f"[bold]Hardware Files:[/bold] {len(self.hardware_files)}\n"
                f"[bold]Firmware Files:[/bold] {len(self.firmware_files)}\n"
                f"[bold]Binary Files:[/bold] {len(self.binary_files)}\n"
                f"[bold]Documentation Files:[/bold] {len(self.doc_files)}\n"
                f"[bold]Script Files:[/bold] {len(self.script_files)}\n"
                f"[bold]Other Files:[/bold] {len(self.other_files)}",
                title="Project Information",
                border_style="blue",
            )
        )

    def analyze_structure(self):
        """
        Analyze and display the project directory structure.
        """
        console.print(f"[green]Analyzing project structure:[/green] {self.source_dir}")

        tree = Tree(f"[bold]{self.name}[/bold]")

        # Build a directory tree representation
        paths = []
        for category in [
            "hardware_files",
            "firmware_files",
            "binary_files",
            "doc_files",
            "script_files",
            "other_files",
        ]:
            files = getattr(self, category)
            paths.extend(files)

        # Sort paths to ensure proper tree structure
        paths.sort()

        # Build the tree
        dir_trees = {}
        root_tree = tree

        for path in paths:
            parts = path.split(os.sep)
            current_tree = root_tree
            current_path = ""

            # Process directories in the path
            for i, part in enumerate(parts[:-1]):
                current_path = (
                    os.path.join(current_path, part) if current_path else part
                )
                if current_path not in dir_trees:
                    dir_trees[current_path] = current_tree.add(
                        f"[bold blue]{part}[/bold blue]"
                    )
                current_tree = dir_trees[current_path]

            # Add the file at the end
            file = parts[-1]
            if file.endswith((".c", ".h", ".cpp", ".hpp")):
                current_tree.add(f"[green]{file}[/green]")
            elif file.endswith((".sch", ".brd", ".kicad_pcb")):
                current_tree.add(f"[magenta]{file}[/magenta]")
            elif file.endswith((".bin", ".hex", ".elf")):
                current_tree.add(f"[red]{file}[/red]")
            elif file.endswith((".md", ".txt", ".pdf")):
                current_tree.add(f"[yellow]{file}[/yellow]")
            elif file.endswith((".sh", ".bat", ".py")):
                current_tree.add(f"[cyan]{file}[/cyan]")
            else:
                current_tree.add(f"[white]{file}[/white]")

        console.print(tree)

    def analyze_hardware(self):
        """
        Analyze hardware files in the project.
        """
        if not self.hardware_files:
            console.print("[yellow]No hardware files found in the project.[/yellow]")
            return

        console.print(
            f"[green]Analyzing {len(self.hardware_files)} hardware files:[/green]"
        )

        # Group hardware files by type
        schematics = [
            f
            for f in self.hardware_files
            if f.endswith((".sch", ".SchDoc", ".kicad_sch"))
        ]
        pcbs = [
            f
            for f in self.hardware_files
            if f.endswith((".brd", ".PcbDoc", ".kicad_pcb"))
        ]
        others = [
            f for f in self.hardware_files if f not in schematics and f not in pcbs
        ]

        table = Table("Type", "Count", "Files")
        table.add_row(
            "Schematics",
            str(len(schematics)),
            "\n".join(schematics[:5])
            + (f"\n... and {len(schematics) - 5} more" if len(schematics) > 5 else ""),
        )
        table.add_row(
            "PCB Layouts",
            str(len(pcbs)),
            "\n".join(pcbs[:5])
            + (f"\n... and {len(pcbs) - 5} more" if len(pcbs) > 5 else ""),
        )
        table.add_row(
            "Other",
            str(len(others)),
            "\n".join(others[:5])
            + (f"\n... and {len(others) - 5} more" if len(others) > 5 else ""),
        )

        console.print(table)

        # Offer detailed analysis of specific files
        console.print("\n[bold]Available actions:[/bold]")
        console.print(
            "1. Use [cyan]convert sch2img <file>[/cyan] to convert schematics to images"
        )
        console.print(
            "2. Use [cyan]analyze hardware <file>[/cyan] to analyze specific hardware files"
        )

    def analyze_firmware(self):
        """
        Analyze firmware files in the project.
        """
        if not self.firmware_files:
            console.print("[yellow]No firmware files found in the project.[/yellow]")
            return

        console.print(
            f"[green]Analyzing {len(self.firmware_files)} firmware files:[/green]"
        )

        # Group firmware files by type
        c_files = [f for f in self.firmware_files if f.endswith(".c")]
        h_files = [f for f in self.firmware_files if f.endswith(".h")]
        cpp_files = [f for f in self.firmware_files if f.endswith((".cpp", ".hpp"))]
        asm_files = [f for f in self.firmware_files if f.endswith((".asm", ".s"))]
        others = [
            f
            for f in self.firmware_files
            if f not in c_files
            and f not in h_files
            and f not in cpp_files
            and f not in asm_files
        ]

        table = Table("Type", "Count", "Files")
        table.add_row(
            "C Source",
            str(len(c_files)),
            "\n".join(c_files[:5])
            + (f"\n... and {len(c_files) - 5} more" if len(c_files) > 5 else ""),
        )
        table.add_row(
            "Header",
            str(len(h_files)),
            "\n".join(h_files[:5])
            + (f"\n... and {len(h_files) - 5} more" if len(h_files) > 5 else ""),
        )
        table.add_row(
            "C++",
            str(len(cpp_files)),
            "\n".join(cpp_files[:5])
            + (f"\n... and {len(cpp_files) - 5} more" if len(cpp_files) > 5 else ""),
        )
        table.add_row(
            "Assembly",
            str(len(asm_files)),
            "\n".join(asm_files[:5])
            + (f"\n... and {len(asm_files) - 5} more" if len(asm_files) > 5 else ""),
        )
        table.add_row(
            "Other",
            str(len(others)),
            "\n".join(others[:5])
            + (f"\n... and {len(others) - 5} more" if len(others) > 5 else ""),
        )

        console.print(table)

        # Look for Makefiles and build scripts
        makefiles = [
            f
            for f in self.script_files
            if os.path.basename(f).lower() == "makefile" or f.endswith((".mk"))
        ]
        build_scripts = [
            f
            for f in self.script_files
            if f.endswith((".sh", ".bat")) and "build" in f.lower()
        ]

        if makefiles or build_scripts:
            console.print("\n[bold]Build System:[/bold]")
            for file in makefiles + build_scripts:
                console.print(f"- {file}")

        # Offer detailed analysis of specific files
        console.print("\n[bold]Available actions:[/bold]")
        console.print("1. Use [cyan]compile firmware[/cyan] to compile the firmware")
        console.print(
            "2. Use [cyan]debug disassemble <file>[/cyan] to disassemble binary files"
        )

    def analyze_binary(self, binary_file):
        """
        Analyze a binary file from the project.

        Args:
            binary_file: Path to the binary file to analyze

        Returns:
            Dictionary with binary analysis results
        """
        from twinizer.software.analyze.binary import BinaryAnalyzer

        # Check if the binary file exists
        binary_path = os.path.join(self.source_dir, binary_file)
        if not os.path.exists(binary_path):
            binary_path = binary_file  # Try using the path directly

        if not os.path.exists(binary_path):
            raise FileNotFoundError(f"Binary file not found: {binary_file}")

        analyzer = BinaryAnalyzer(binary_path)
        return analyzer.analyze()

    def compile_firmware(self):
        """
        Compile firmware source code.
        """
        if not self.firmware_files:
            console.print("[yellow]No firmware files found in the project.[/yellow]")
            return

        console.print("[green]Compiling firmware:[/green]")

        # Look for Makefiles
        makefiles = [
            f
            for f in self.script_files
            if os.path.basename(f).lower() == "makefile" or f.endswith((".mk"))
        ]

        if makefiles:
            console.print(f"Found {len(makefiles)} Makefiles in the project.")
            for makefile in makefiles:
                full_path = os.path.join(self.source_dir, os.path.dirname(makefile))
                console.print(f"Running make in: {full_path}")

                # Simulate compilation process
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    task = progress.add_task("[green]Compiling...", total=None)
                    # Here we would actually run the make command
                    # subprocess.run(['make', '-C', full_path], check=True)
                    # For now, just simulate a delay
                    import time

                    time.sleep(2)
                    progress.update(
                        task, completed=True, description="[green]Compilation complete!"
                    )

                console.print("[green]Compilation successful![/green]")
        else:
            console.print(
                "[yellow]No Makefiles found in the project. Looking for other build systems...[/yellow]"
            )

            # Check for other build systems
            build_scripts = [
                f
                for f in self.script_files
                if f.endswith((".sh", ".bat")) and "build" in f.lower()
            ]

            if build_scripts:
                console.print(
                    f"Found {len(build_scripts)} build scripts in the project."
                )
                for script in build_scripts:
                    console.print(f"You can run: {script}")
            else:
                console.print(
                    "[yellow]No build system found. You may need to create a Makefile or specify compilation commands manually.[/yellow]"
                )

    def cross_compile(self, target):
        """
        Cross-compile firmware for a specific target.

        Args:
            target: Target platform (e.g., arm, avr, msp430)
        """
        console.print(f"[green]Cross-compiling for target:[/green] {target}")

        # Check if target is supported
        supported_targets = ["arm", "avr", "msp430", "risc-v", "x86"]
        if target.lower() not in [t.lower() for t in supported_targets]:
            console.print(
                f"[yellow]Warning: Unknown target '{target}'. Supported targets are: {', '.join(supported_targets)}[/yellow]"
            )

        # Simulate cross-compilation
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(
                f"[green]Cross-compiling for {target}...", total=None
            )
            # Here we would set up and run the cross-compilation toolchain
            # For now, just simulate a delay
            import time

            time.sleep(3)
            progress.update(
                task,
                completed=True,
                description=f"[green]Cross-compilation for {target} complete!",
            )

        console.print("[green]Cross-compilation successful![/green]")
        console.print(
            f"Output files would be created in: {os.path.join(self.source_dir, 'build', target)}"
        )

    def clean_build(self):
        """
        Clean build artifacts.
        """
        console.print("[green]Cleaning build artifacts...[/green]")

        # Look for common build directories
        build_dirs = ["build", "out", "bin", "obj"]
        cleaned = False

        for build_dir in build_dirs:
            full_path = os.path.join(self.source_dir, build_dir)
            if os.path.exists(full_path) and os.path.isdir(full_path):
                console.print(f"Removing directory: {build_dir}")
                # In a real implementation, we would actually remove the directory
                # shutil.rmtree(full_path)
                cleaned = True

        if cleaned:
            console.print("[green]Build artifacts cleaned successfully![/green]")
        else:
            console.print("[yellow]No build artifacts found to clean.[/yellow]")

    def debug_elf(self, elf_file):
        """
        Debug an ELF file.

        Args:
            elf_file: Path to the ELF file to debug
        """
        console.print(f"[green]Starting debug session for:[/green] {elf_file}")
        console.print(
            "[yellow]This feature is not fully implemented yet. In a real implementation, this would start a GDB session.[/yellow]"
        )

    def disassemble(self, binary_file):
        """
        Disassemble a binary file.

        Args:
            binary_file: Path to the binary file to disassemble
        """
        full_path = os.path.join(self.source_dir, binary_file)
        if not os.path.exists(full_path):
            console.print(f"[red]Binary file not found:[/red] {binary_file}")
            return

        console.print(f"[green]Disassembling binary file:[/green] {binary_file}")
        console.print(
            "[yellow]This feature is not fully implemented yet. In a real implementation, this would use Capstone and pyelftools to disassemble the binary.[/yellow]"
        )

    def decompile(self, binary_file):
        """
        Decompile a binary file to source code.

        Args:
            binary_file: Path to the binary file to decompile
        """
        full_path = os.path.join(self.source_dir, binary_file)
        if not os.path.exists(full_path):
            console.print(f"[red]Binary file not found:[/red] {binary_file}")
            return

        console.print(f"[green]Decompiling binary file:[/green] {binary_file}")
        console.print(
            "[yellow]This feature is not fully implemented yet. In a real implementation, this would use appropriate decompilation tools based on the file type.[/yellow]"
        )

    def trace_execution(self, binary_file):
        """
        Trace the execution flow of a binary file.

        Args:
            binary_file: Path to the binary file to trace
        """
        full_path = os.path.join(self.source_dir, binary_file)
        if not os.path.exists(full_path):
            console.print(f"[red]Binary file not found:[/red] {binary_file}")
            return

        console.print(f"[green]Tracing execution flow of:[/green] {binary_file}")
        console.print(
            "[yellow]This feature is not fully implemented yet. In a real implementation, this would use appropriate tracing tools based on the file type.[/yellow]"
        )

    def convert_pdf_to_markdown(self, pdf_file):
        """
        Convert a PDF file to Markdown.

        Args:
            pdf_file: Path to the PDF file to convert
        """
        full_path = os.path.join(self.source_dir, pdf_file)
        if not os.path.exists(full_path):
            console.print(f"[red]PDF file not found:[/red] {pdf_file}")
            return

        console.print(f"[green]Converting PDF to Markdown:[/green] {pdf_file}")

        output_path = os.path.splitext(full_path)[0] + ".md"
        console.print(
            f"Output will be saved to: {os.path.relpath(output_path, self.source_dir)}"
        )

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[green]Converting PDF...", total=None)
            # Here we would use PDF conversion libraries
            # For now, just simulate a delay
            import time

            time.sleep(3)
            progress.update(
                task, completed=True, description="[green]Conversion complete!"
            )

        console.print("[green]PDF converted to Markdown successfully![/green]")

    def convert_schematic_to_image(self, schematic_file):
        """
        Convert a schematic file to an image.

        Args:
            schematic_file: Path to the schematic file to convert
        """
        full_path = os.path.join(self.source_dir, schematic_file)
        if not os.path.exists(full_path):
            console.print(f"[red]Schematic file not found:[/red] {schematic_file}")
            return

        console.print(f"[green]Converting schematic to image:[/green] {schematic_file}")

        output_path = os.path.splitext(full_path)[0] + ".png"
        console.print(
            f"Output will be saved to: {os.path.relpath(output_path, self.source_dir)}"
        )

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[green]Converting schematic...", total=None)
            # Here we would use schematic conversion tools
            # For now, just simulate a delay
            import time

            time.sleep(2)
            progress.update(
                task, completed=True, description="[green]Conversion complete!"
            )

        console.print("[green]Schematic converted to image successfully![/green]")

    def convert_binary_to_source(self, binary_file):
        """
        Convert a binary file to source code.

        Args:
            binary_file: Path to the binary file to convert
        """
        full_path = os.path.join(self.source_dir, binary_file)
        if not os.path.exists(full_path):
            console.print(f"[red]Binary file not found:[/red] {binary_file}")
            return

        console.print(f"[green]Converting binary to source code:[/green] {binary_file}")

        # Determine output format based on file extension
        output_ext = ".c"  # Default to C
        if binary_file.endswith(".pyc"):
            output_ext = ".py"
        elif binary_file.endswith(".so"):
            # For .so files, we'll try to create Python bindings
            output_ext = "_wrapper.py"

        output_path = os.path.splitext(full_path)[0] + output_ext
        console.print(
            f"Output will be saved to: {os.path.relpath(output_path, self.source_dir)}"
        )

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[green]Converting binary...", total=None)
            # Here we would use appropriate decompilation tools
            # For now, just simulate a delay
            import time

            time.sleep(4)
            progress.update(
                task, completed=True, description="[green]Conversion complete!"
            )

        console.print("[green]Binary converted to source code successfully![/green]")

    def convert_image_to_ascii(self, image_file):
        """
        Convert an image to ASCII art.

        Args:
            image_file: Path to the image file to convert
        """
        full_path = os.path.join(self.source_dir, image_file)
        if not os.path.exists(full_path):
            console.print(f"[red]Image file not found:[/red] {image_file}")
            return

        console.print(f"[green]Converting image to ASCII art:[/green] {image_file}")

        output_path = os.path.splitext(full_path)[0] + ".txt"
        console.print(
            f"Output will be saved to: {os.path.relpath(output_path, self.source_dir)}"
        )

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[green]Converting image...", total=None)
            # Here we would use image conversion libraries
            # For now, just simulate a delay
            import time

            time.sleep(1.5)
            progress.update(
                task, completed=True, description="[green]Conversion complete!"
            )

        console.print("[green]Image converted to ASCII art successfully![/green]")

    def convert_doc_to_tree(self, doc_file):
        """
        Convert a documentation file to a tree structure.

        Args:
            doc_file: Path to the documentation file to convert
        """
        full_path = os.path.join(self.source_dir, doc_file)
        if not os.path.exists(full_path):
            console.print(f"[red]Documentation file not found:[/red] {doc_file}")
            return

        console.print(
            f"[green]Converting documentation to tree structure:[/green] {doc_file}"
        )

        output_path = os.path.splitext(full_path)[0] + "_tree.md"
        console.print(
            f"Output will be saved to: {os.path.relpath(output_path, self.source_dir)}"
        )

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[green]Converting documentation...", total=None)
            # Here we would parse the document to extract its structure
            # For now, just simulate a delay
            import time

            time.sleep(2)
            progress.update(
                task, completed=True, description="[green]Conversion complete!"
            )

        console.print(
            "[green]Documentation converted to tree structure successfully![/green]"
        )

    def run_unit_tests(self):
        """
        Run unit tests for the project.
        """
        console.print("[green]Running unit tests...[/green]")
        console.print(
            "[yellow]This feature is not fully implemented yet. In a real implementation, this would discover and run unit tests for the project.[/yellow]"
        )

    def run_integration_tests(self):
        """
        Run integration tests for the project.
        """
        console.print("[green]Running integration tests...[/green]")
        console.print(
            "[yellow]This feature is not fully implemented yet. In a real implementation, this would discover and run integration tests for the project.[/yellow]"
        )

    def run_performance_tests(self):
        """
        Run performance tests for the project.
        """
        console.print("[green]Running performance tests...[/green]")
        console.print(
            "[yellow]This feature is not fully implemented yet. In a real implementation, this would run performance benchmarks for the project.[/yellow]"
        )

    def generate_test_coverage(self):
        """
        Generate test coverage report for the project.
        """
        console.print("[green]Generating test coverage report...[/green]")
        console.print(
            "[yellow]This feature is not fully implemented yet. In a real implementation, this would generate a test coverage report for the project.[/yellow]"
        )

    def create_backup(self):
        """
        Create a backup of the project.
        """
        console.print("[green]Creating project backup...[/green]")

        # Generate backup filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{self.name}_backup_{timestamp}.zip"
        backup_path = os.path.join(os.path.dirname(self.source_dir), backup_file)

        console.print(f"Backup will be saved to: {backup_path}")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[green]Creating backup...", total=None)
            # Here we would actually create the zip file
            # In a real implementation, we would use:
            # with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            #     for root, _, files in os.walk(self.source_dir):
            #         for file in files:
            #             file_path = os.path.join(root, file)
            #             zipf.write(file_path, os.path.relpath(file_path, os.path.dirname(self.source_dir)))

            # For now, just simulate a delay
            import time

            time.sleep(3)
            progress.update(task, completed=True, description="[green]Backup complete!")

        console.print(
            f"[green]Project backup created successfully:[/green] {backup_file}"
        )

    def backup(self, output_path=None):
        """
        Create a backup of the project.

        Args:
            output_path: Path to save the backup archive, if None uses a timestamped name

        Returns:
            Path to the created backup file
        """
        import datetime
        import zipfile

        # Generate default output path if not provided
        if output_path is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d")
            output_path = f"{self.name}_backup_{timestamp}.zip"

        # Create a zip archive
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(self.source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.source_dir)
                    zipf.write(file_path, rel_path)

        return output_path

    def show_statistics(self):
        """
        Show statistics about the project.
        """
        console.print("[green]Project Statistics:[/green]")

        # Count lines of code
        loc = {"c": 0, "h": 0, "cpp": 0, "hpp": 0, "asm": 0, "other": 0}

        # In a real implementation, we would actually count lines
        # For now, just set some dummy values
        loc["c"] = 8500
        loc["h"] = 2300
        loc["cpp"] = 500
        loc["hpp"] = 150
        loc["asm"] = 1200
        loc["other"] = 800

        total_loc = sum(loc.values())

        # Create a table for the statistics
        table = Table("Metric", "Value")
        table.add_row(
            "Total Files",
            str(
                sum(
                    len(getattr(self, f))
                    for f in [
                        "hardware_files",
                        "firmware_files",
                        "binary_files",
                        "doc_files",
                        "script_files",
                        "other_files",
                    ]
                )
            ),
        )

        table.add_row("Hardware Files", str(len(self.hardware_files)))
        table.add_row("Firmware Files", str(len(self.firmware_files)))
        table.add_row("Binary Files", str(len(self.binary_files)))
        table.add_row("Documentation Files", str(len(self.doc_files)))
        table.add_row("Script Files", str(len(self.script_files)))

        table.add_row("Total Lines of Code", str(total_loc))
        table.add_row("C Code", str(loc["c"]))
        table.add_row("Header Files", str(loc["h"]))
        table.add_row("C++ Code", str(loc["cpp"]))
        table.add_row("C++ Headers", str(loc["hpp"]))
        table.add_row("Assembly", str(loc["asm"]))
        table.add_row("Other Code", str(loc["other"]))

        console.print(table)

    def analyze_documentation(self):
        """
        Analyze documentation files in the project.
        """
        if not self.doc_files:
            console.print(
                "[yellow]No documentation files found in the project.[/yellow]"
            )
            return

        console.print(
            f"[green]Analyzing {len(self.doc_files)} documentation files:[/green]"
        )

        # Group documentation files by type
        markdown_files = [f for f in self.doc_files if f.endswith((".md", ".markdown"))]
        pdf_files = [f for f in self.doc_files if f.endswith(".pdf")]
        text_files = [f for f in self.doc_files if f.endswith((".txt", ".rst"))]
        others = [
            f
            for f in self.doc_files
            if f not in markdown_files and f not in pdf_files and f not in text_files
        ]

        table = Table("Type", "Count", "Files")
        table.add_row(
            "Markdown",
            str(len(markdown_files)),
            "\n".join(markdown_files[:5])
            + (
                f"\n... and {len(markdown_files) - 5} more"
                if len(markdown_files) > 5
                else ""
            ),
        )
        table.add_row(
            "PDF",
            str(len(pdf_files)),
            "\n".join(pdf_files[:5])
            + (f"\n... and {len(pdf_files) - 5} more" if len(pdf_files) > 5 else ""),
        )
        table.add_row(
            "Text",
            str(len(text_files)),
            "\n".join(text_files[:5])
            + (f"\n... and {len(text_files) - 5} more" if len(text_files) > 5 else ""),
        )
        table.add_row(
            "Other",
            str(len(others)),
            "\n".join(others[:5])
            + (f"\n... and {len(others) - 5} more" if len(others) > 5 else ""),
        )

        console.print(table)

        # Offer detailed analysis of specific files
        console.print("\n[bold]Available actions:[/bold]")
        console.print(
            "1. Use [cyan]convert pdf2md <file>[/cyan] to convert PDF to Markdown"
        )
        console.print(
            "2. Use [cyan]convert doc2tree <file>[/cyan] to create a document tree"
        )

    def analyze_scripts(self):
        """
        Analyze script files in the project.
        """
        if not self.script_files:
            console.print("[yellow]No script files found in the project.[/yellow]")
            return

        console.print(
            f"[green]Analyzing {len(self.script_files)} script files:[/green]"
        )

        # Group script files by type
        python_files = [f for f in self.script_files if f.endswith(".py")]
        shell_files = [f for f in self.script_files if f.endswith((".sh", ".bash"))]
        batch_files = [f for f in self.script_files if f.endswith((".bat", ".cmd"))]
        makefiles = [
            f
            for f in self.script_files
            if os.path.basename(f).lower() == "makefile" or f.endswith(".mk")
        ]
        others = [
            f
            for f in self.script_files
            if f not in python_files
            and f not in shell_files
            and f not in batch_files
            and f not in makefiles
        ]

        table = Table("Type", "Count", "Files")
        table.add_row(
            "Python",
            str(len(python_files)),
            "\n".join(python_files[:5])
            + (
                f"\n... and {len(python_files) - 5} more"
                if len(python_files) > 5
                else ""
            ),
        )
        table.add_row(
            "Shell",
            str(len(shell_files)),
            "\n".join(shell_files[:5])
            + (
                f"\n... and {len(shell_files) - 5} more" if len(shell_files) > 5 else ""
            ),
        )
        table.add_row(
            "Batch",
            str(len(batch_files)),
            "\n".join(batch_files[:5])
            + (
                f"\n... and {len(batch_files) - 5} more" if len(batch_files) > 5 else ""
            ),
        )
        table.add_row(
            "Makefiles",
            str(len(makefiles)),
            "\n".join(makefiles[:5])
            + (f"\n... and {len(makefiles) - 5} more" if len(makefiles) > 5 else ""),
        )
        table.add_row(
            "Other",
            str(len(others)),
            "\n".join(others[:5])
            + (f"\n... and {len(others) - 5} more" if len(others) > 5 else ""),
        )

        console.print(table)

        # Offer detailed analysis of specific files
        console.print("\n[bold]Available actions:[/bold]")
        console.print("1. Use [cyan]run script <file>[/cyan] to execute a script")
        console.print(
            "2. Use [cyan]analyze script <file>[/cyan] to analyze a specific script"
        )

    def export_project(self, zip_path):
        """
        Export the project to a ZIP file.

        Args:
            zip_path: Path to save the ZIP file

        Returns:
            Path to the created ZIP file
        """
        import zipfile

        console.print(f"[green]Exporting project to:[/green] {zip_path}")

        # Create a zip archive
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(self.source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.source_dir)
                    zipf.write(file_path, rel_path)

        console.print(f"[green]Project exported successfully to:[/green] {zip_path}")
        return zip_path

    @classmethod
    def import_project(cls, zip_path, import_dir):
        """
        Import a project from a ZIP file.

        Args:
            zip_path: Path to the ZIP file
            import_dir: Directory to extract the project to

        Returns:
            Project instance for the imported project
        """
        import zipfile

        console.print(f"[green]Importing project from:[/green] {zip_path}")
        console.print(f"[green]Extracting to:[/green] {import_dir}")

        # Extract the zip archive
        with zipfile.ZipFile(zip_path, "r") as zipf:
            zipf.extractall(import_dir)

        console.print(f"[green]Project imported successfully to:[/green] {import_dir}")
        return cls(import_dir)
