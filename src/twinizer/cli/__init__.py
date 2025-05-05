"""
Command-line interface for the Twinizer package.

This module provides the main CLI entry point for the Twinizer package,
integrating all the available commands.
"""

import importlib
import os
import sys
from typing import List, Optional

import click
from rich.console import Console

console = Console()


@click.group(help="Twinizer: A toolkit for digital twin creation and manipulation")
@click.version_option()
def cli():
    """Main entry point for the Twinizer CLI."""
    pass


# Import and register all command groups
def register_commands():
    """Dynamically import and register all command groups."""
    commands_dir = os.path.join(os.path.dirname(__file__), "commands")

    # Skip if the commands directory doesn't exist yet
    if not os.path.exists(commands_dir):
        return

    for filename in os.listdir(commands_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = filename[:-3]  # Remove .py extension

            try:
                # Import the module
                module = importlib.import_module(f"twinizer.cli.commands.{module_name}")

                # Find and register command groups
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, click.Group) and attr_name.endswith("_group"):
                        cli.add_command(attr)

            except (ImportError, AttributeError) as e:
                console.print(
                    f"[yellow]Warning: Failed to load command module {module_name}: {e}[/yellow]"
                )


# Register commands
register_commands()

# Explicitly register the generate-report command for backward compatibility
try:
    from twinizer.cli.commands.generate_report import generate_report_command

    cli.add_command(generate_report_command)
except (ImportError, AttributeError) as e:
    console.print(
        f"[yellow]Warning: Failed to load generate-report command: {e}[/yellow]"
    )


# Add built-in commands
@cli.command(name="list-commands", help="List all available commands")
def list_commands():
    """List all available commands."""
    console.print("[bold green]Available Commands:[/bold green]")

    for command in cli.commands.values():
        console.print(f"[bold]{command.name}[/bold]: {command.help}")

        if isinstance(command, click.Group):
            for subcommand in command.commands.values():
                console.print(
                    f"  [bold]{command.name} {subcommand.name}[/bold]: {subcommand.help}"
                )


@cli.command()
def run():
    """Run the interactive shell mode."""
    # Use fully qualified import path for bootstrap_environment to make patching more reliable in tests
    import twinizer.utils.env
    from twinizer.cli.shell import TwinizerShell

    twinizer.utils.env.bootstrap_environment()

    # Create shell and run
    shell = TwinizerShell({})  # Pass an empty context dictionary
    shell.run()


def main():
    """Run the CLI application."""
    try:
        cli()
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
