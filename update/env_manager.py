#!/usr/bin/env python3
"""
Module for managing project environment variables.
Allows reading and writing variables to the .env file
and interacting with the user to set variable values.
"""

import os
import re
import sys
import shutil
import glob
from pathlib import Path
from typing import Dict, Optional, Any, List, Tuple


def get_project_root() -> Path:
    """Returns the path to the project root directory."""
    # Assuming this script is in the update directory
    return Path(__file__).parent.parent


def create_env_file_if_not_exists(env_file: Path = None) -> None:
    """
    Creates a .env file if it doesn't exist.
    
    Args:
        env_file: Path to the .env file. If None, uses the default path.
    """
    if env_file is None:
        env_file = get_project_root() / ".env"
    
    if not env_file.exists():
        # Check if .env.example exists
        env_example = get_project_root() / ".env.example"
        
        if env_example.exists():
            # Copy .env.example to .env
            shutil.copy2(env_example, env_file)
            print(f"Created file {env_file} based on {env_example}")
        else:
            # Create an empty .env file
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write("# Project Configuration\n")
                f.write("PROJECT_NAME=\n")
                f.write("PACKAGE_PATH=\n")
            print(f"Created empty file {env_file}")


def load_env_file(env_file: Path = None) -> Dict[str, str]:
    """
    Loads environment variables from the .env file.
    
    Args:
        env_file: Path to the .env file. If None, uses the default path.
        
    Returns:
        Dictionary with environment variables.
    """
    if env_file is None:
        env_file = get_project_root() / ".env"
    
    # Create .env file if it doesn't exist
    create_env_file_if_not_exists(env_file)
    
    env_vars = {}
    
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                if '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    
    return env_vars


def save_env_file(env_vars: Dict[str, str], env_file: Path = None) -> None:
    """
    Saves environment variables to the .env file.
    
    Args:
        env_vars: Dictionary with environment variables.
        env_file: Path to the .env file. If None, uses the default path.
    """
    if env_file is None:
        env_file = get_project_root() / ".env"
    
    # Create .env file if it doesn't exist
    create_env_file_if_not_exists(env_file)
    
    # Preserve comments and formatting from the existing file
    existing_lines = []
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            existing_lines = f.readlines()
    
    # Prepare new lines with current values
    new_lines = []
    processed_keys = set()
    
    for line in existing_lines:
        line = line.rstrip('\n')
        if not line or line.startswith('#'):
            new_lines.append(line)
            continue
        
        if '=' in line:
            key, _ = line.split('=', 1)
            key = key.strip()
            if key in env_vars:
                new_lines.append(f"{key}={env_vars[key]}")
                processed_keys.add(key)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    # Add new variables that weren't in the file
    for key, value in env_vars.items():
        if key not in processed_keys:
            new_lines.append(f"{key}={value}")
    
    # Save the file
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines) + '\n')


def get_env_var(key: str, default: Any = None, prompt: bool = True) -> str:
    """
    Gets the value of an environment variable.
    If the variable doesn't exist, asks the user for its value.
    
    Args:
        key: Name of the environment variable.
        default: Default value if the variable doesn't exist.
        prompt: Whether to ask the user for the value if the variable doesn't exist.
        
    Returns:
        Value of the environment variable.
    """
    env_vars = load_env_file()
    
    if key in env_vars and env_vars[key]:
        return env_vars[key]
    
    if prompt:
        if default:
            value = input(f"Enter value for {key} [{default}]: ").strip()
            if not value:
                value = default
        else:
            value = input(f"Enter value for {key}: ").strip()
            while not value:
                print("Value cannot be empty.")
                value = input(f"Enter value for {key}: ").strip()
    else:
        value = default
    
    if value:
        env_vars[key] = value
        save_env_file(env_vars)
    
    return value


def detect_project_name() -> List[str]:
    """
    Automatically detect project name from various sources.
    
    Returns:
        List of potential project names, ordered by likelihood.
    """
    project_root = get_project_root()
    candidates = []
    
    # Method 1: Check pyproject.toml
    pyproject_path = project_root / "pyproject.toml"
    if pyproject_path.exists():
        with open(pyproject_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Try to find the project name using regex
        match = re.search(r'name\s*=\s*[\'"]([^\'"]+)[\'"]', content)
        if match:
            candidates.append(match.group(1))
    
    # Method 2: Check setup.py
    setup_path = project_root / "setup.py"
    if setup_path.exists():
        with open(setup_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Try to find the project name using regex
        match = re.search(r'name\s*=\s*[\'"]([^\'"]+)[\'"]', content)
        if match:
            candidates.append(match.group(1))
    
    # Method 3: Check setup.cfg
    setup_cfg_path = project_root / "setup.cfg"
    if setup_cfg_path.exists():
        with open(setup_cfg_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Try to find the project name using regex
        match = re.search(r'name\s*=\s*([^\n]+)', content)
        if match:
            candidates.append(match.group(1).strip())
    
    # Method 4: Check src directory for Python packages
    src_path = project_root / "src"
    if src_path.exists() and src_path.is_dir():
        # Look for directories with __init__.py files
        for item in src_path.iterdir():
            if item.is_dir() and (item / "__init__.py").exists():
                candidates.append(item.name)
    
    # Method 5: Look for directories with __init__.py in the project root
    for item in project_root.iterdir():
        if item.is_dir() and not item.name.startswith('.') and not item.name == 'src':
            if (item / "__init__.py").exists():
                candidates.append(item.name)
    
    # Method 6: Use directory name as a fallback
    candidates.append(project_root.name)
    
    # Remove duplicates while preserving order
    unique_candidates = []
    for candidate in candidates:
        if candidate not in unique_candidates:
            unique_candidates.append(candidate)
    
    return unique_candidates


def detect_package_paths(project_name: str) -> List[str]:
    """
    Detect possible package paths for a given project name.
    
    Args:
        project_name: The name of the project.
        
    Returns:
        List of potential package paths, ordered by likelihood.
    """
    project_root = get_project_root()
    candidates = []
    
    # Method 1: src/project_name
    src_path = project_root / "src" / project_name
    if src_path.exists() and src_path.is_dir():
        candidates.append(f"src/{project_name}")
    
    # Method 2: project_name directly in root
    root_path = project_root / project_name
    if root_path.exists() and root_path.is_dir():
        candidates.append(project_name)
    
    # Method 3: Look for any directory with __init__.py
    for init_file in glob.glob(str(project_root) + "/**/__init__.py", recursive=True):
        package_path = os.path.dirname(init_file)
        rel_path = os.path.relpath(package_path, str(project_root))
        if rel_path not in candidates and rel_path != ".":
            candidates.append(rel_path)
    
    return candidates


def get_project_name(prompt: bool = True) -> str:
    """
    Gets the project name from the .env file or detects it automatically.
    If the name is not defined, asks the user.
    
    Args:
        prompt: Whether to ask the user if the name is not defined.
        
    Returns:
        Project name.
    """
    # First check in .env
    env_vars = load_env_file()
    if "PROJECT_NAME" in env_vars and env_vars["PROJECT_NAME"]:
        return env_vars["PROJECT_NAME"]
    
    # If not in .env, try to detect automatically
    candidates = detect_project_name()
    
    if candidates:
        project_name = candidates[0]  # Use the most likely candidate
        
        # Save to .env
        env_vars["PROJECT_NAME"] = project_name
        save_env_file(env_vars)
        
        return project_name
    
    # If still not found, ask the user
    if prompt:
        return get_env_var("PROJECT_NAME", "", True)
    
    # If all else fails, return empty string
    return ""


def get_package_path(prompt: bool = True) -> str:
    """
    Gets the path to the package directory.
    If the path is not defined, tries to detect it automatically.
    
    Args:
        prompt: Whether to ask the user if the path is not defined.
        
    Returns:
        Path to the package directory (relative to the project root directory).
    """
    # First check in .env
    env_vars = load_env_file()
    if "PACKAGE_PATH" in env_vars and env_vars["PACKAGE_PATH"]:
        return env_vars["PACKAGE_PATH"]
    
    # If not in .env, try to detect automatically
    project_name = get_project_name(False)
    
    if project_name:
        candidates = detect_package_paths(project_name)
        
        if candidates:
            package_path = candidates[0]  # Use the most likely candidate
            
            # Save to .env
            env_vars["PACKAGE_PATH"] = package_path
            save_env_file(env_vars)
            
            return package_path
    
    # If still not found, ask the user
    if prompt:
        return get_env_var("PACKAGE_PATH", project_name if project_name else "", True)
    
    # If all else fails, return the project name or empty string
    return project_name if project_name else ""


def get_version_files() -> List[str]:
    """
    Get a list of files that contain version information.
    
    Returns:
        List of absolute paths to files containing version information.
    """
    project_root = get_project_root()
    project_name = get_project_name()
    package_path = get_package_path()
    
    # Convert relative package path to absolute
    if package_path:
        package_path = os.path.join(project_root, package_path)
    elif project_name:
        package_path = os.path.join(project_root, project_name)
    else:
        package_path = ""
    
    version_files = []
    
    # Check common configuration files
    config_files = [
        os.path.join(project_root, "pyproject.toml"),
        os.path.join(project_root, "setup.py"),
        os.path.join(project_root, "setup.cfg"),
    ]
    
    for file_path in config_files:
        if os.path.exists(file_path) and os.path.isfile(file_path):
            version_files.append(file_path)
    
    # If we have a package path, check for version in Python files
    if package_path and os.path.exists(package_path):
        # Check main __init__.py
        init_file = os.path.join(package_path, "__init__.py")
        if os.path.exists(init_file):
            version_files.append(init_file)
        
        # Check _version.py
        version_file = os.path.join(package_path, "_version.py")
        if os.path.exists(version_file):
            version_files.append(version_file)
        
        # Check version.py
        version_file = os.path.join(package_path, "version.py")
        if os.path.exists(version_file):
            version_files.append(version_file)
        
        # Look for __init__.py files in subdirectories that might contain version info
        for root, dirs, files in os.walk(package_path):
            if "__init__.py" in files:
                init_path = os.path.join(root, "__init__.py")
                # Check if the file contains a version string
                with open(init_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if re.search(r'__version__\s*=', content):
                    version_files.append(init_path)
    
    return version_files


def find_all_version_files() -> List[str]:
    """
    Find all files in the project that might contain version information.
    This is a more exhaustive search than get_version_files().
    
    Returns:
        List of absolute paths to files that might contain version information.
    """
    project_root = get_project_root()
    version_files = []
    
    # Check common configuration files first
    config_files = [
        os.path.join(project_root, "pyproject.toml"),
        os.path.join(project_root, "setup.py"),
        os.path.join(project_root, "setup.cfg"),
    ]
    
    for file_path in config_files:
        if os.path.exists(file_path) and os.path.isfile(file_path) and os.access(file_path, os.R_OK | os.W_OK):
            version_files.append(file_path)
    
    # Search for Python files with version information
    for root, dirs, files in os.walk(project_root):
        # Skip virtual environments and hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'venv' and d != 'env' and d != '__pycache__']
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                # Check if we have read and write permissions
                if not os.access(file_path, os.R_OK | os.W_OK):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check if the file contains version information
                    if re.search(r'__version__\s*=', content) or re.search(r'version\s*=', content):
                        version_files.append(file_path)
                except (UnicodeDecodeError, IOError, PermissionError):
                    # Skip binary files or files that can't be read
                    pass
    
    return version_files


if __name__ == "__main__":
    # Create .env file if it doesn't exist
    env_file = get_project_root() / ".env"
    create_env_file_if_not_exists(env_file)
    
    # Print project information
    project_name = get_project_name()
    package_path = get_package_path()
    version_files = get_version_files()
    
    print(f"Project name: {project_name}")
    print(f"Package path: {package_path}")
    print(f"Version files: {version_files}")
