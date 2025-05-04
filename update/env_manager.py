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
from pathlib import Path
from typing import Dict, Optional, Any


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


def get_project_name(prompt: bool = True) -> str:
    """
    Gets the project name from the .env file or pyproject.toml.
    If the name is not defined, asks the user.
    
    Args:
        prompt: Whether to ask the user if the name is not defined.
        
    Returns:
        Project name.
    """
    # First check in .env
    project_name = get_env_var("PROJECT_NAME", None, False)
    if project_name:
        return project_name
    
    # If not in .env, check in pyproject.toml
    pyproject_path = get_project_root() / "pyproject.toml"
    if pyproject_path.exists():
        with open(pyproject_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Try to find the project name using regex
        match = re.search(r'name\s*=\s*[\'"]([^\'"]+)[\'"]', content)
        if match:
            project_name = match.group(1)
            
            # Save to .env
            env_vars = load_env_file()
            env_vars["PROJECT_NAME"] = project_name
            save_env_file(env_vars)
            
            return project_name
    
    # If still not found, ask the user
    if prompt:
        return get_env_var("PROJECT_NAME", "twinizer", True)
    
    # If all else fails, return the default value
    return "twinizer"


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
    package_path = get_env_var("PACKAGE_PATH", "", False)
    if package_path:
        return package_path
    
    # If not in .env, try to detect automatically
    project_name = get_project_name(False)
    
    # Check if the package is in src/project_name
    src_path = get_project_root() / "src" / project_name
    if src_path.exists():
        package_path = f"src/{project_name}"
        
        # Save to .env
        env_vars = load_env_file()
        env_vars["PACKAGE_PATH"] = package_path
        save_env_file(env_vars)
        
        return package_path
    
    # Check if the package is directly in the project root directory
    root_path = get_project_root() / project_name
    if root_path.exists():
        package_path = project_name
        
        # Save to .env
        env_vars = load_env_file()
        env_vars["PACKAGE_PATH"] = package_path
        save_env_file(env_vars)
        
        return package_path
    
    # If still not found, ask the user
    if prompt:
        return get_env_var("PACKAGE_PATH", project_name, True)
    
    # If all else fails, return the default value
    return project_name


def get_version_files():
    """Get a list of files that contain version information."""
    project_name = get_project_name()
    package_path = get_package_path()
    
    # Convert relative package path to absolute
    if package_path:
        package_path = os.path.join(get_project_root(), package_path)
    else:
        package_path = os.path.join(get_project_root(), project_name)
    
    # Common files that contain version information
    version_files = [
        os.path.join(get_project_root(), "pyproject.toml"),
    ]
    
    # Add package-specific files
    init_file = os.path.join(package_path, "__init__.py")
    version_file = os.path.join(package_path, "_version.py")
    
    if os.path.exists(init_file):
        version_files.append(init_file)
    
    if os.path.exists(version_file):
        version_files.append(version_file)
    
    # Filter out files that don't exist
    return [f for f in version_files if os.path.exists(f)]


if __name__ == "__main__":
    # Create .env file if it doesn't exist
    env_file = get_project_root() / ".env"
    create_env_file_if_not_exists(env_file)
    
    # Print project information
    print(f"Project name: {get_project_name()}")
    print(f"Package path: {get_package_path()}")
    print(f"Version files: {get_version_files()}")
