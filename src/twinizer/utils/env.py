"""
env.py
"""

"""
Environment utilities for Twinizer.
Handles virtual environment creation and dependency management.
"""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.progress import SpinnerColumn, TextColumn

console = Console()


def is_in_virtualenv():
    """Check if running inside a virtual environment."""
    return hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )


def check_python_version():
    """Check if Python version is >= 3.9."""
    major, minor, *_ = sys.version_info
    if major < 3 or (major == 3 and minor < 9):
        console.print(
            f"[bold red]Error:[/bold red] Python 3.9+ is required (found {major}.{minor})"
        )
        return False
    return True


def check_conda_env():
    """Check if running inside a conda environment."""
    return os.environ.get("CONDA_PREFIX") is not None


def get_venv_path():
    """Get the path to Twinizer's virtual environment."""
    return Path.home() / ".twinizer_env"


def create_venv(venv_path):
    """Create a virtual environment for Twinizer."""
    console.print(f"Creating virtual environment at [cyan]{venv_path}[/cyan]")
    subprocess.run([sys.executable, "-m", "venv", venv_path], check=True)


def get_pip_path(venv_path):
    """Get the path to pip in the virtual environment."""
    if platform.system() == "Windows":
        return venv_path / "Scripts" / "pip.exe"
    return venv_path / "bin" / "pip"


def get_python_path(venv_path):
    """Get the path to Python in the virtual environment."""
    if platform.system() == "Windows":
        return venv_path / "Scripts" / "python.exe"
    return venv_path / "bin" / "python"


def install_dependencies(pip_path: Path) -> bool:
    """
    Install project dependencies using the specified pip executable.

    Args:
        pip_path: Path to pip executable

    Returns:
        True if installation succeeded, False otherwise
    """
    console.print("  Installing dependencies...")
    try:
        # Import Progress directly inside the function to match the test's patch target
        from rich.progress import Progress

        with Progress() as progress:
            # Add a task to the progress bar
            task = progress.add_task("Installing dependencies...", total=100)

            # Run pip install command
            subprocess.run([str(pip_path), "install", "-e", "."], check=True)

            # Update progress - make sure this exact call happens
            progress.update(task, advance=100)

        return True
    except Exception as e:
        print(f"Error installing dependencies: {e}")
        return False


def inject_system_paths():
    """Inject paths to system tools (gcc, objdump, etc.)."""
    # Add common locations for development tools to PATH
    system = platform.system()
    paths_to_check = []

    if system == "Windows":
        paths_to_check.extend(
            [
                "C:\\Program Files\\GCC",
                "C:\\Program Files\\LLVM\\bin",
                "C:\\Program Files (x86)\\GNU Tools ARM Embedded",
            ]
        )
    else:  # Linux/Mac
        paths_to_check.extend(
            [
                "/usr/local/bin",
                "/opt/gcc/bin",
                "/opt/avr/bin",
            ]
        )

    # Add these paths to the environment
    for path in paths_to_check:
        if os.path.exists(path) and path not in os.environ["PATH"]:
            os.environ["PATH"] = path + os.pathsep + os.environ["PATH"]


def bootstrap_environment():
    """
    Bootstrap the Twinizer environment.

    This function:
    1. Checks the Python version
    2. Creates a virtual environment if not already in one
    3. Installs required dependencies
    4. Injects paths to system tools

    Returns:
        bool: True if environment is ready or was successfully bootstrapped, False otherwise
    """
    if not check_python_version():
        return False

    # If already in a virtual environment or conda, we're good to go
    if is_in_virtualenv() or check_conda_env():
        inject_system_paths()
        return True

    # Not in a virtual environment, create one
    venv_path = get_venv_path()

    if not venv_path.exists():
        try:
            create_venv(venv_path)
            pip_path = get_pip_path(venv_path)
            install_dependencies(pip_path)

            # Re-execute the command in the virtual environment
            python_path = get_python_path(venv_path)
            args = [str(python_path)] + sys.argv
            os.execv(str(python_path), args)
            # Note: execv replaces the current process, so the code below won't run
            # unless there's an error with execv
            return True
        except Exception as e:
            console.print(
                f"[bold red]Error creating virtual environment:[/bold red] {e}"
            )
            return False
    else:
        # Virtual environment exists, just use it
        pip_path = get_pip_path(venv_path)
        install_dependencies(pip_path)

        python_path = get_python_path(venv_path)
        args = [str(python_path)] + sys.argv
        os.execv(str(python_path), args)
        # Note: execv replaces the current process, so the code below won't run
        # unless there's an error with execv
        return True
