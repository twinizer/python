#!/usr/bin/env python3
"""
Configuration file for version update scripts.
This file contains project-specific settings that are used by the update scripts.
"""

import os
import configparser
import re
from pathlib import Path

# Import env_manager module
try:
    from env_manager import get_project_name, get_package_path, get_project_root
except ImportError:
    # If import fails, add update directory to path
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from env_manager import get_project_name, get_package_path, get_project_root


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


# Project configuration
PROJECT_CONFIG = {
    "name": get_project_name(),
    "package_path": get_package_path(),
    "version_files": get_version_files(),
}

if __name__ == "__main__":
    # Print the configuration when run directly
    print(f"Project name: {PROJECT_CONFIG['name']}")
    print(f"Package path: {PROJECT_CONFIG['package_path']}")
    print("Version files:")
    for file in PROJECT_CONFIG['version_files']:
        print(f"  - {file}")
