#!/bin/bash
set -e  # Stop script on first error

# Skip clear screen which requires TERM to be set
echo "Starting version update process..."

# Create a temporary Python script to get project configuration
TMP_SCRIPT=$(mktemp)
cat > "$TMP_SCRIPT" << 'EOF'
#!/usr/bin/env python3
import sys
import os
import re
from pathlib import Path

def get_project_root():
    """Returns the path to the project root directory."""
    return Path(os.getcwd())

def detect_project_name():
    """Automatically detect project name from various sources."""
    project_root = get_project_root()
    candidates = []
    
    # Method 1: Check pyproject.toml
    pyproject_path = project_root / "pyproject.toml"
    if pyproject_path.exists():
        try:
            with open(pyproject_path, 'r', encoding='utf-8') as f:
                content = f.read()
                match = re.search(r'name\s*=\s*[\'"]([^\'"]+)[\'"]', content)
                if match:
                    candidates.append(match.group(1))
        except:
            pass
    
    # Method 2: Check setup.py
    setup_path = project_root / "setup.py"
    if setup_path.exists():
        try:
            with open(setup_path, 'r', encoding='utf-8') as f:
                content = f.read()
                match = re.search(r'name\s*=\s*[\'"]([^\'"]+)[\'"]', content)
                if match:
                    candidates.append(match.group(1))
        except:
            pass
    
    # Method 3: Check src directory for Python packages
    src_path = project_root / "src"
    if src_path.exists() and src_path.is_dir():
        for item in src_path.iterdir():
            if item.is_dir() and (item / "__init__.py").exists():
                candidates.append(item.name)
    
    # Method 4: Use directory name as a fallback
    candidates.append(project_root.name)
    
    # Remove duplicates while preserving order
    unique_candidates = []
    for candidate in candidates:
        if candidate not in unique_candidates:
            unique_candidates.append(candidate)
    
    return unique_candidates[0] if unique_candidates else ""

def detect_package_path(project_name):
    """Detect possible package path for a given project name."""
    project_root = get_project_root()
    
    # Method 1: src/project_name
    src_path = project_root / "src" / project_name
    if src_path.exists() and src_path.is_dir():
        return f"src/{project_name}"
    
    # Method 2: project_name directly in root
    root_path = project_root / project_name
    if root_path.exists() and root_path.is_dir():
        return project_name
    
    return f"src/{project_name}"  # Default fallback

def find_version_files(project_name, package_path):
    """Find files that contain version information with proper permissions."""
    project_root = get_project_root()
    version_files = []
    
    # Check common configuration files
    config_files = [
        project_root / "pyproject.toml",
        project_root / "setup.py",
        project_root / "setup.cfg",
    ]
    
    for file_path in config_files:
        if file_path.exists() and file_path.is_file() and os.access(file_path, os.R_OK | os.W_OK):
            version_files.append(str(file_path))
    
    # Check main package __init__.py
    if package_path:
        init_file = project_root / package_path / "__init__.py"
        if init_file.exists() and os.access(init_file, os.R_OK | os.W_OK):
            version_files.append(str(init_file))
    
    return version_files

def main():
    try:
        # Auto-detect project name
        project_name = detect_project_name()
        
        # Auto-detect package path
        package_path = detect_package_path(project_name)
        
        # Find version files with proper permissions
        version_files = find_version_files(project_name, package_path)
        
        # Output results in a format that can be sourced by bash
        print(f"PROJECT_NAME='{project_name}'")
        print(f"PACKAGE_PATH='{package_path}'")
        print(f"VERSION_FILES='{';'.join(version_files)}'")
        
    except Exception as e:
        print(f"# Error: {e}", file=sys.stderr)
        project_dir = os.path.basename(os.getcwd())
        print(f"PROJECT_NAME='{project_dir}'")
        print(f"PACKAGE_PATH='src/{project_dir}'")
        print(f"VERSION_FILES=''")

if __name__ == "__main__":
    main()
EOF

# Run the temporary script to get project configuration
echo "Detecting project configuration..."
source <(python3 "$TMP_SCRIPT")
rm "$TMP_SCRIPT"

echo "Project name: $PROJECT_NAME"
echo "Package path: $PACKAGE_PATH"
echo "Files to update version in:"
if [ -n "$VERSION_FILES" ]; then
    IFS=';' read -ra FILES <<< "$VERSION_FILES"
    for file in "${FILES[@]}"; do
        echo "  - $file"
    done
else
    echo "  No files found with proper permissions"
fi

# Check if virtualenv is already activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Creating and activating virtual environment..."
    # Create virtualenv if it doesn't exist
    if [ ! -d "venv" ]; then
        python -m venv venv
    fi
    source venv/bin/activate
else
    echo "Virtual environment already active: $VIRTUAL_ENV"
fi

# Make sure we have the latest tools
echo "Upgrading build tools..."
pip install --upgrade pip build twine

# Check if we're in virtualenv
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Error: Failed to activate virtual environment!"
    exit 1
fi

# Install project dependencies
echo "Installing project dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

# Uninstall and reinstall package in edit mode
echo "Reinstalling package in development mode..."
pip uninstall -y "$PROJECT_NAME" || true
pip install -e .

# Update version in source files
echo "Updating version number..."
if [ -n "$VERSION_FILES" ]; then
    IFS=';' read -ra FILES <<< "$VERSION_FILES"
    updated_files=0
    for file in "${FILES[@]}"; do
        if [ -w "$file" ]; then
            echo "Updating version in file: $file"
            if python update/src.py -f "$file" --type patch; then
                updated_files=$((updated_files+1))
            else
                echo "Failed to update version in file $file"
            fi
        else
            echo "Skipped file $file (no write permission)"
        fi
    done
    
    if [ $updated_files -eq 0 ]; then
        echo "Warning: No files were updated. Check file permissions."
    else
        echo "Successfully updated version in $updated_files files."
    fi
else
    echo "No files to update version"
    echo "Using default version from CHANGELOG.md"
fi

# Generate entry in CHANGELOG.md
echo "Generating entry in CHANGELOG.md..."
if [ -f "CHANGELOG.md" ] && [ ! -w "CHANGELOG.md" ]; then
    echo "Warning: No write permission to CHANGELOG.md file"
    echo "Creating temporary file CHANGELOG.md.new"
    python update/changelog.py --output CHANGELOG.md.new || echo "Failed to generate entry in CHANGELOG.md"
else
    python update/changelog.py || echo "Failed to generate entry in CHANGELOG.md"
fi

# Run code quality checks and tests
echo "Running code quality checks and tests..."
echo "This step ensures your code meets quality standards and all tests pass."
bash update/test.sh --fix || {
    echo "Code quality checks or tests failed. Please fix the issues before publishing."
    echo "You can run './update/test.sh --fix' to automatically fix some issues."
    exit 1
}
echo "All code quality checks and tests passed!"

# Publish to GitHub
echo "Push changes..."
bash update/git.sh || {
    echo "Failed to push changes to GitHub."
    exit 1
}

# Publish to PyPI
echo "Publishing to PyPI..."
bash update/pypi.sh || {
    echo "Failed to publish to PyPI."
    exit 1
}

echo "Version update process completed successfully!"
