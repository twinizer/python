#!/bin/bash

# Ensure script fails on any error
set -e

# Get project configuration
echo "Getting project configuration..."
PROJECT_CONFIG=$(python -c "
import sys
sys.path.append('update')
from env_manager import get_project_name

# Get project name
project_name = get_project_name(False)
print(f\"PROJECT_NAME={project_name}\")
")

# Process configuration
eval "$PROJECT_CONFIG"
echo "Project name: $PROJECT_NAME"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting PyPI publication process...${NC}"

# Check if virtualenv is already activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Make sure we have the latest tools
echo -e "${GREEN}Updating build tools...${NC}"
pip install --upgrade pip build twine

# Check if we're in virtualenv
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${RED}Error: Failed to activate virtual environment!${NC}"
    echo -e "It is recommended to publish changes to GitHub first (bash update/git.sh)."
    exit 1
fi

echo -e "${GREEN}Checking Git repository status...${NC}"
if [[ -n $(git status --porcelain) ]]; then
    echo -e "${YELLOW}Warning: Uncommitted changes detected in the repository.${NC}"
    echo -e "It is recommended to publish changes to GitHub first (bash update/git.sh)."
    echo -e "Continuing publication process despite uncommitted changes..."
fi

# Clean up previous builds
echo -e "${GREEN}Cleaning previous builds...${NC}"
rm -rf build/ dist/ *.egg-info/

# Build the package
echo -e "${GREEN}Building package...${NC}"
python -m build

# Check the distribution
echo -e "${GREEN}Checking distribution package...${NC}"
twine check dist/*

# Upload to PyPI
echo -e "${GREEN}Uploading package to PyPI...${NC}"
twine upload dist/*

echo -e "${GREEN}Package $PROJECT_NAME has been successfully published on PyPI!${NC}"