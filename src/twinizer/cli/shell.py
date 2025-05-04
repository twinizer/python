"""
Interactive shell for Twinizer.
Provides a command-line interface with tab completion and history.
"""

import os
import sys
from pathlib import Path
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from twinizer.core.project import Project

console = Console()


class TwinizerShell:
    """Interactive shell for Twinizer."""

    COMMANDS = {
        'analyze': {
            'help': 'Analyze project structure and files',
            'subcommands': {
                'structure': 'Analyze project directory structure',
                'hardware': 'Analyze hardware files (schematics, PCB)',
                'firmware': 'Analyze firmware files',
                'binary': 'Analyze binary files',
            }
        },
        'compile': {
            'help': 'Compile project source files',
            'subcommands': {
                'firmware': 'Compile firmware source code',
                'cross': 'Cross-compile for specific target',
                'clean': 'Clean build artifacts',
            }
        },
        'debug': {
            'help': 'Debug firmware or analyze binary',
            'subcommands': {
                'elf': 'Debug ELF file',
                'disassemble': 'Disassemble binary file',
                'decompile': 'Decompile binary to source code',
                'trace': 'Trace execution flow',
            }
        },
        'convert': {
            'help': 'Convert between file formats',
            'subcommands': {
                'pdf2md': 'Convert PDF to Markdown',
                'sch2img': 'Convert schematic to image',
                'bin2source': 'Convert binary to source code',
                'image2ascii': 'Convert image to ASCII art',
                'doc2tree': 'Convert documentation to tree structure',
            }
        },
        'test': {
            'help': 'Run tests on firmware or hardware',
            'subcommands': {
                'unit': 'Run unit tests',
                'integration': 'Run integration tests',
                'performance': 'Run performance benchmarks',
                'coverage': 'Generate test coverage report',
            }
        },
        'project': {
            'help': 'Project management commands',
            'subcommands': {
                'info': 'Show project information',
                'scan': 'Scan project directory',
                'backup': 'Create project backup',
                'stats': 'Show project statistics',
            }
        },
        'help': {
            'help': 'Show help information',
        },
        'exit': {
            'help': 'Exit the shell',
        }
    }

    def __init__(self, context):
        """Initialize the shell."""
        self.context = context
        self.source_dir = context.get('source_dir', './source')
        self.project = Project(self.source_dir)

        # Create command completer
        all_commands = []
        for cmd, info in self.COMMANDS.items():
            all_commands.append(cmd)
            if 'subcommands' in info:
                for subcmd in info['subcommands']:
                    all_commands.append(f"{cmd} {subcmd}")

        self.completer = WordCompleter(all_commands, ignore_case=True)

        # Set up history file
        history_file = os.path.join(Path.home(), '.twinizer_history')
        self.history = FileHistory(history_file)

        # Create prompt session
        self.session = PromptSession(
            completer=self.completer,
            history=self.history,
            style=Style.from_dict({
                'prompt': 'ansiblue bold',
            }),
        )

    def run(self):
        """Run the interactive shell."""
        # Scan the project first
        self.project.scan()

        while True:
            try:
                text = self.session.prompt(
                    HTML(f'<ansiblue><b>twinizer ({os.path.basename(self.source_dir)})></b></ansiblue> ')
                )

                if text.strip():
                    self.process_command(text)
            except KeyboardInterrupt:
                continue
            except EOFError:
                break

    def process_command(self, command_line):
        """Process a command line input."""
        parts = command_line.strip().split()
        if not parts:
            return

        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []

        if command == 'exit' or command == 'quit':
            console.print("[yellow]Exiting Twinizer...[/yellow]")
            sys.exit(0)
        elif command == 'help':
            self.show_help(args[0] if args else None)
        elif command in self.COMMANDS:
            self.execute_command(command, args)
        else:
            console.print(f"[bold red]Unknown command:[/bold red] {command}")
            console.print("Type [bold]help[/bold] to see available commands.")

    def show_help(self, command=None):
        """Show help for commands."""
        if command and command in self.COMMANDS:
            # Show help for specific command
            cmd_info = self.COMMANDS[command]
            console.print(Panel.fit(
                f"[bold]{command}[/bold]: {cmd_info['help']}\n",
                title=f"Help: {command}",
                border_style="blue"
            ))

            if 'subcommands' in cmd_info:
                table = Table("Subcommand", "Description")
                for subcmd, desc in cmd_info['subcommands'].items():
                    table.add_row(subcmd, desc)
                console.print(table)
        else:
            # Show general help
            table = Table("Command", "Description")
            for cmd, info in self.COMMANDS.items():
                table.add_row(cmd, info['help'])

            console.print(Panel.fit(
                "Available commands:",
                title="Twinizer Help",
                border_style="blue"
            ))
            console.print(table)
            console.print("\nType [bold]help <command>[/bold] for detailed information about a command.")

    def execute_command(self, command, args):
        """Execute a command with its arguments."""
        # This would map to actual command implementations
        if command == 'analyze':
            if not args:
                console.print("[yellow]Please specify what to analyze: structure, hardware, firmware, binary[/yellow]")
                return

            subcmd = args[0]
            if subcmd == 'structure':
                self.project.analyze_structure()
            elif subcmd == 'hardware':
                self.project.analyze_hardware()
            elif subcmd == 'firmware':
                self.project.analyze_firmware()
            elif subcmd == 'binary':
                if len(args) < 2:
                    console.print("[yellow]Please specify a binary file to analyze[/yellow]")
                    return
                self.project.analyze_binary(args[1])
            else:
                console.print(f"[bold red]Unknown analyze subcommand:[/bold red] {subcmd}")

        elif command == 'compile':
            if not args:
                console.print("[yellow]Please specify what to compile: firmware, cross, clean[/yellow]")
                return

            subcmd = args[0]
            if subcmd == 'firmware':
                self.project.compile_firmware()
            elif subcmd == 'cross':
                if len(args) < 2:
                    console.print("[yellow]Please specify target platform[/yellow]")
                    return
                self.project.cross_compile(args[1])
            elif subcmd == 'clean':
                self.project.clean_build()
            else:
                console.print(f"[bold red]Unknown compile subcommand:[/bold red] {subcmd}")

        elif command == 'debug':
            if not args:
                console.print("[yellow]Please specify debug mode: elf, disassemble, decompile, trace[/yellow]")
                return

            subcmd = args[0]
            if subcmd == 'elf':
                if len(args) < 2:
                    console.print("[yellow]Please specify an ELF file to debug[/yellow]")
                    return
                self.project.debug_elf(args[1])
            elif subcmd == 'disassemble':
                if len(args) < 2:
                    console.print("[yellow]Please specify a binary file to disassemble[/yellow]")
                    return
                self.project.disassemble(args[1])
            elif subcmd == 'decompile':
                if len(args) < 2:
                    console.print("[yellow]Please specify a binary file to decompile[/yellow]")
                    return
                self.project.decompile(args[1])
            elif subcmd == 'trace':
                if len(args) < 2:
                    console.print("[yellow]Please specify a binary file to trace[/yellow]")
                    return
                self.project.trace_execution(args[1])
            else:
                console.print(f"[bold red]Unknown debug subcommand:[/bold red] {subcmd}")

        elif command == 'convert':
            if not args:
                console.print(
                    "[yellow]Please specify conversion type: pdf2md, sch2img, bin2source, image2ascii, doc2tree[/yellow]")
                return

            subcmd = args[0]
            if subcmd == 'pdf2md':
                if len(args) < 2:
                    console.print("[yellow]Please specify a PDF file to convert[/yellow]")
                    return
                self.project.convert_pdf_to_markdown(args[1])
            elif subcmd == 'sch2img':
                if len(args) < 2:
                    console.print("[yellow]Please specify a schematic file to convert[/yellow]")
                    return
                self.project.convert_schematic_to_image(args[1])
            elif subcmd == 'bin2source':
                if len(args) < 2:
                    console.print("[yellow]Please specify a binary file to convert[/yellow]")
                    return
                self.project.convert_binary_to_source(args[1])
            elif subcmd == 'image2ascii':
                if len(args) < 2:
                    console.print("[yellow]Please specify an image file to convert[/yellow]")
                    return
                self.project.convert_image_to_ascii(args[1])
            elif subcmd == 'doc2tree':
                if len(args) < 2:
                    console.print("[yellow]Please specify a documentation file to convert[/yellow]")
                    return
                self.project.convert_doc_to_tree(args[1])
            else:
                console.print(f"[bold red]Unknown convert subcommand:[/bold red] {subcmd}")

        elif command == 'test':
            if not args:
                console.print("[yellow]Please specify test type: unit, integration, performance, coverage[/yellow]")
                return

            subcmd = args[0]
            if subcmd == 'unit':
                self.project.run_unit_tests()
            elif subcmd == 'integration':
                self.project.run_integration_tests()
            elif subcmd == 'performance':
                self.project.run_performance_tests()
            elif subcmd == 'coverage':
                self.project.generate_test_coverage()
            else:
                console.print(f"[bold red]Unknown test subcommand:[/bold red] {subcmd}")

        elif command == 'project':
            if not args:
                console.print("[yellow]Please specify project command: info, scan, backup, stats[/yellow]")
                return

            subcmd = args[0]
            if subcmd == 'info':
                self.project.show_info()
            elif subcmd == 'scan':
                self.project.scan()
            elif subcmd == 'backup':
                self.project.create_backup()
            elif subcmd == 'stats':
                self.project.show_statistics()
            else:
                console.print(f"[bold red]Unknown project subcommand:[/bold red] {subcmd}")