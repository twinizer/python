#!/bin/bash
set -e  # Stop script on first error

# Skip clear screen which requires TERM to be set
# clear
echo "Starting publication process..."

# Get project configuration
echo "Getting project configuration..."
PROJECT_CONFIG=$(python3 -c "
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'update'))
try:
    from env_manager import get_project_name, get_package_path, get_project_root, get_version_files
    
    # Ask user for project name if not defined
    project_name = get_project_name(True)
    package_path = get_package_path(True)
    
    # Get version files - use only pyproject.toml which is usually accessible
    version_files = []
    project_root = get_project_root()
    
    # Check pyproject.toml
    pyproject_path = os.path.join(project_root, 'pyproject.toml')
    if os.path.exists(pyproject_path) and os.access(pyproject_path, os.W_OK):
        version_files.append(pyproject_path)
    
    # Check main package __init__.py
    init_path = os.path.join(project_root, 'src', project_name, '__init__.py')
    if os.path.exists(init_path) and os.access(init_path, os.W_OK):
        version_files.append(init_path)
    
    # Check other modules that might have version info
    for module in ['code_analyzer', 'converters/image/mermaid']:
        module_init = os.path.join(project_root, 'src', project_name, module, '__init__.py')
        if os.path.exists(module_init) and os.access(module_init, os.W_OK):
            version_files.append(module_init)
    
    print(f\"PROJECT_NAME={project_name}\")
    print(f\"PACKAGE_PATH={package_path}\")
    print(f\"VERSION_FILES={';'.join(version_files)}\")
except Exception as e:
    print(f\"PROJECT_NAME=twinizer\")
    print(f\"PACKAGE_PATH=twinizer\")
    print(f\"VERSION_FILES=pyproject.toml\")
    print(f\"# Error: {e}\", file=sys.stderr)
")

# Process configuration
eval "$PROJECT_CONFIG"
echo "Project name: $PROJECT_NAME"
echo "Package path: $PACKAGE_PATH"
echo "Version files: $VERSION_FILES"

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
    for file in "${FILES[@]}"; do
        if [ -w "$file" ]; then
            echo "Updating version in file: $file"
            python update/src.py -f "$file" --type patch || echo "Failed to update version in file $file"
        else
            echo "Skipped file $file (no write permission)"
        fi
    done
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

echo "Publication process completed successfully!"
