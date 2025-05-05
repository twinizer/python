"""
main.py
"""

"""
CLI Application for Twinizer.
Provides the main command-line interface and command registration.
"""

import os
import sys

import click
from rich.console import Console
from rich.panel import Panel

from twinizer import __version__
from twinizer.cli.commands import (
    analyze,
    image_group,
    kicad_deps_group,
    kicad_docker_group,
    kicad_group,
)

# Create console for rich output
console = Console()


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(
    __version__, "-v", "--version", message="Twinizer version %(version)s"
)
@click.pass_context
def cli(ctx):
    """
    Twinizer - A comprehensive environment for hardware and firmware reverse engineering.

    Twinizer integrates tools for reverse engineering, compilation, debugging,
    documentation conversion, and workflow automation for embedded projects.
    """
    # Initialize the context object
    ctx.ensure_object(dict)
    ctx.obj["source_dir"] = os.environ.get(
        "TWINIZER_SOURCE_DIR", os.path.join(os.getcwd(), "source")
    )


@cli.command()
@click.pass_context
def run(ctx):
    """
    Run the interactive Twinizer shell.
    """
    # Bootstrap the environment (create venv if needed, install dependencies)
    # Use fully qualified import path for bootstrap_environment to make patching more reliable in tests
    import twinizer.utils.env

    twinizer.utils.env.bootstrap_environment()

    # Display welcome message
    console.print(
        Panel.fit(
            "[bold blue]Twinizer[/bold blue] [dim]v{version}[/dim]\n\n"
            "A comprehensive environment for hardware and firmware reverse engineering.\n"
            f"Source directory: [cyan]{ctx.obj['source_dir']}[/cyan]",
            title="Welcome to Twinizer",
            border_style="blue",
        )
    )

    # Start the interactive shell
    from twinizer.cli.shell import TwinizerShell

    shell = TwinizerShell(ctx.obj)
    shell.run()


# Register commands
from twinizer.cli.commands import (
    analyze,
    image_group,
    kicad_deps_group,
    kicad_docker_group,
    kicad_group,
)

cli.add_command(analyze)
cli.add_command(kicad_group)
cli.add_command(kicad_deps_group)
cli.add_command(image_group)
cli.add_command(kicad_docker_group)


def main():
    """
    Main entry point for the CLI.
    """
    return cli(obj={})


if __name__ == "__main__":
    main()
