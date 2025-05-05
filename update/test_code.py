#!/usr/bin/env python3
"""
Code quality and testing script for Python projects.
This script runs various code quality checks and unit tests.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from rich.console import Console
from rich.table import Table

# Add path to the update directory to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from env_manager import get_project_name, get_package_path, get_project_root
except ImportError:
    print("Cannot import env_manager module. Using default values.")
    def get_project_name():
        return "twinizer"
    def get_package_path():
        return "twinizer"
    def get_project_root():
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Initialize rich console
console = Console()

def run_command(cmd: List[str], cwd: Optional[str] = None) -> Tuple[int, str, str]:
    """
    Run a command and return exit code, stdout, and stderr.
    
    Args:
        cmd: Command to run as a list of strings
        cwd: Working directory to run the command in
        
    Returns:
        Tuple of (exit_code, stdout, stderr)
    """
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=cwd
        )
        stdout, stderr = process.communicate()
        return process.returncode, stdout, stderr
    except Exception as e:
        return 1, "", str(e)

def check_tool_installed(tool: str) -> bool:
    """
    Check if a tool is installed.
    
    Args:
        tool: Name of the tool to check
        
    Returns:
        True if tool is installed, False otherwise
    """
    try:
        subprocess.run(
            [sys.executable, "-m", tool, "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def install_tool(tool: str) -> bool:
    """
    Install a Python tool using pip.
    
    Args:
        tool: Name of the tool to install
        
    Returns:
        True if installation was successful, False otherwise
    """
    console.print(f"[yellow]Installing {tool}...[/yellow]")
    exit_code, _, _ = run_command([sys.executable, "-m", "pip", "install", tool])
    return exit_code == 0

def ensure_tool(tool: str) -> bool:
    """
    Ensure a tool is installed, installing it if necessary.
    
    Args:
        tool: Name of the tool to ensure is installed
        
    Returns:
        True if tool is available, False otherwise
    """
    if check_tool_installed(tool):
        return True
    return install_tool(tool)

def run_flake8(src_dir: str) -> Dict[str, Any]:
    """
    Run flake8 linting.
    
    Args:
        src_dir: Directory to run flake8 on
        
    Returns:
        Dictionary with results
    """
    if not ensure_tool("flake8"):
        return {"success": False, "message": "Failed to install flake8"}
    
    console.print("[bold]Running flake8 linting...[/bold]")
    
    # Run flake8 for syntax errors and undefined names
    exit_code, stdout, stderr = run_command(
        [sys.executable, "-m", "flake8", src_dir, "--count", "--select=E9,F63,F7,F82", "--show-source", "--statistics"]
    )
    
    if exit_code != 0:
        console.print("[red]Critical linting errors found:[/red]")
        console.print(stdout)
        return {"success": False, "message": "Critical linting errors found", "output": stdout}
    
    # Run flake8 for warnings (exit-zero)
    exit_code, stdout, stderr = run_command(
        [sys.executable, "-m", "flake8", src_dir, "--count", "--exit-zero", "--max-complexity=10", "--max-line-length=127", "--statistics"]
    )
    
    if stdout.strip():
        console.print("[yellow]Linting warnings found (non-critical):[/yellow]")
        console.print(stdout)
    
    return {"success": True, "message": "Flake8 checks passed", "warnings": stdout}

def run_black(src_dir: str, check_only: bool = True) -> Dict[str, Any]:
    """
    Run black code formatter.
    
    Args:
        src_dir: Directory to run black on
        check_only: Only check if code is formatted correctly, don't modify
        
    Returns:
        Dictionary with results
    """
    if not ensure_tool("black"):
        return {"success": False, "message": "Failed to install black"}
    
    console.print("[bold]Running black code formatter...[/bold]")
    
    cmd = [sys.executable, "-m", "black"]
    if check_only:
        cmd.append("--check")
    cmd.append(src_dir)
    
    exit_code, stdout, stderr = run_command(cmd)
    
    if exit_code != 0:
        if check_only:
            console.print("[yellow]Code formatting issues found:[/yellow]")
            console.print(stdout)
            return {"success": False, "message": "Code formatting issues found", "output": stdout}
        else:
            console.print("[yellow]Error while formatting code:[/yellow]")
            console.print(stderr)
            return {"success": False, "message": "Error while formatting code", "output": stderr}
    
    return {"success": True, "message": "Black formatting check passed" if check_only else "Code formatted successfully"}

def run_isort(src_dir: str, check_only: bool = True) -> Dict[str, Any]:
    """
    Run isort import sorter.
    
    Args:
        src_dir: Directory to run isort on
        check_only: Only check if imports are sorted correctly, don't modify
        
    Returns:
        Dictionary with results
    """
    if not ensure_tool("isort"):
        return {"success": False, "message": "Failed to install isort"}
    
    console.print("[bold]Running isort import sorter...[/bold]")
    
    cmd = [sys.executable, "-m", "isort"]
    if check_only:
        cmd.append("--check-only")
    cmd.extend(["--profile", "black", src_dir])
    
    exit_code, stdout, stderr = run_command(cmd)
    
    if exit_code != 0:
        if check_only:
            console.print("[yellow]Import sorting issues found:[/yellow]")
            console.print(stdout)
            return {"success": False, "message": "Import sorting issues found", "output": stdout}
        else:
            console.print("[yellow]Error while sorting imports:[/yellow]")
            console.print(stderr)
            return {"success": False, "message": "Error while sorting imports", "output": stderr}
    
    return {"success": True, "message": "Import sorting check passed" if check_only else "Imports sorted successfully"}

def run_mypy(src_dir: str) -> Dict[str, Any]:
    """
    Run mypy type checking.
    
    Args:
        src_dir: Directory to run mypy on
        
    Returns:
        Dictionary with results
    """
    if not ensure_tool("mypy"):
        return {"success": False, "message": "Failed to install mypy"}
    
    console.print("[bold]Running mypy type checking...[/bold]")
    
    exit_code, stdout, stderr = run_command(
        [sys.executable, "-m", "mypy", src_dir, "--ignore-missing-imports"]
    )
    
    if exit_code != 0:
        console.print("[yellow]Type checking issues found:[/yellow]")
        console.print(stdout)
        return {"success": False, "message": "Type checking issues found", "output": stdout}
    
    return {"success": True, "message": "Type checking passed"}

def run_pytest(src_dir: str) -> Dict[str, Any]:
    """
    Run pytest unit tests.
    
    Args:
        src_dir: Directory to run pytest on
        
    Returns:
        Dictionary with results
    """
    if not ensure_tool("pytest"):
        return {"success": False, "message": "Failed to install pytest"}
    
    console.print("[bold]Running pytest unit tests...[/bold]")
    
    exit_code, stdout, stderr = run_command(
        [sys.executable, "-m", "pytest", "-v"]
    )
    
    if exit_code != 0:
        console.print("[red]Unit tests failed:[/red]")
        console.print(stdout)
        return {"success": False, "message": "Unit tests failed", "output": stdout}
    
    console.print("[green]Unit tests passed![/green]")
    return {"success": True, "message": "Unit tests passed", "output": stdout}

def run_tox() -> Dict[str, Any]:
    """
    Run tox for multi-environment testing.
    
    Returns:
        Dictionary with results
    """
    if not ensure_tool("tox"):
        return {"success": False, "message": "Failed to install tox"}
    
    console.print("[bold]Running tox multi-environment tests...[/bold]")
    
    exit_code, stdout, stderr = run_command(["tox"])
    
    if exit_code != 0:
        console.print("[red]Tox tests failed:[/red]")
        console.print(stdout)
        return {"success": False, "message": "Tox tests failed", "output": stdout}
    
    console.print("[green]Tox tests passed![/green]")
    return {"success": True, "message": "Tox tests passed", "output": stdout}

def run_all_tests(src_dir: str, fix: bool = False, run_tox_tests: bool = False) -> Dict[str, Any]:
    """
    Run all tests and code quality checks.
    
    Args:
        src_dir: Directory to run tests on
        fix: Whether to fix issues automatically
        run_tox_tests: Whether to run tox tests
        
    Returns:
        Dictionary with results
    """
    results = {}
    
    # Run flake8
    results["flake8"] = run_flake8(src_dir)
    
    # Run black
    results["black"] = run_black(src_dir, check_only=not fix)
    
    # Run isort
    results["isort"] = run_isort(src_dir, check_only=not fix)
    
    # Run mypy
    # results["mypy"] = run_mypy(src_dir)
    
    # Run pytest
    results["pytest"] = run_pytest(src_dir)
    
    # Run tox if requested
    if run_tox_tests:
        results["tox"] = run_tox()
    
    # Print summary
    console.print("\n[bold]Test Summary:[/bold]")
    table = Table(show_header=True, header_style="bold")
    table.add_column("Test")
    table.add_column("Status")
    table.add_column("Message")
    
    all_passed = True
    for name, result in results.items():
        status = "[green]PASS[/green]" if result["success"] else "[red]FAIL[/red]"
        if not result["success"]:
            all_passed = False
        table.add_row(name, status, result["message"])
    
    console.print(table)
    
    if all_passed:
        console.print("[green bold]All tests passed![/green bold]")
    else:
        console.print("[red bold]Some tests failed![/red bold]")
    
    return {"success": all_passed, "results": results}

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Run code quality checks and tests")
    parser.add_argument("--src", help="Source directory to test", default=None)
    parser.add_argument("--fix", action="store_true", help="Fix issues automatically")
    parser.add_argument("--tox", action="store_true", help="Run tox tests")
    args = parser.parse_args()
    
    # Get source directory
    if args.src:
        src_dir = args.src
    else:
        project_root = get_project_root()
        package_path = get_package_path()
        src_dir = os.path.join(project_root, "src", package_path) if os.path.exists(os.path.join(project_root, "src", package_path)) else os.path.join(project_root, package_path)
    
    if not os.path.exists(src_dir):
        console.print(f"[red]Error: Source directory {src_dir} does not exist![/red]")
        return 1
    
    console.print(f"[bold]Testing code in {src_dir}[/bold]")
    
    results = run_all_tests(src_dir, fix=args.fix, run_tox_tests=args.tox)
    
    return 0 if results["success"] else 1

if __name__ == "__main__":
    sys.exit(main())
