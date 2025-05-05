#!/bin/bash
set -e  # Stop script on first error

# Get project configuration
echo "Getting project configuration..."
PROJECT_CONFIG=$(python3 -c "
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'update'))
try:
    from env_manager import get_project_name, get_package_path, get_project_root
    
    # Ask user for project name if not defined
    project_name = get_project_name(True)
    package_path = get_package_path(True)
    project_root = get_project_root()
    
    print(f\"PROJECT_NAME={project_name}\")
    print(f\"PACKAGE_PATH={package_path}\")
    print(f\"PROJECT_ROOT={project_root}\")
except Exception as e:
    print(f\"PROJECT_NAME=twinizer\")
    print(f\"PACKAGE_PATH=twinizer\")
    print(f\"PROJECT_ROOT=$(pwd)\")
    print(f\"# Error: {e}\", file=sys.stderr)
")

# Process configuration
eval "$PROJECT_CONFIG"
echo "Project name: $PROJECT_NAME"
echo "Package path: $PACKAGE_PATH"
echo "Project root: $PROJECT_ROOT"

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

# Install project dependencies
echo "Installing project dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

# Install test dependencies
echo "Installing test dependencies..."
pip install pytest flake8 black isort mypy tox

# Install the package in development mode
echo "Installing package in development mode..."
pip install -e .

# Run the tests
echo "Running code quality checks and tests..."
python update/test_code.py "$@"

# Store the exit code
EXIT_CODE=$?

# Return the exit code
exit $EXIT_CODE
