#!/bin/bash

echo "Publishing new version to GitHub..."

# Pobierz konfigurację projektu
echo "Pobieranie konfiguracji projektu..."
PROJECT_CONFIG=$(python -c "
import sys
sys.path.append('update')
from env_manager import get_project_name

# Pobierz nazwę projektu
project_name = get_project_name(False)
print(f\"PROJECT_NAME={project_name}\")
")

# Przetwórz konfigurację
eval "$PROJECT_CONFIG"
echo "Nazwa projektu: $PROJECT_NAME"

# Function to extract latest version from CHANGELOG.md
get_latest_version() {
    # Extract the first version number found in CHANGELOG.md
    version=$(grep -m 1 "## \[.*\]" CHANGELOG.md | grep -o "\[.*\]" | tr -d "[]")
    echo $version
}

# Function to extract latest changes from CHANGELOG.md
get_latest_changes() {
    # Read CHANGELOG.md and extract content between first and second version headers
    awk '/^## \[/{i++}i==1{print}i==2{exit}' CHANGELOG.md | tail -n +2
}

# Get version and changes
VERSION=$(get_latest_version)
if [ -z "$VERSION" ]; then
    echo "Error: Could not find version in CHANGELOG.md"
    exit 1
fi

echo "Found version: $VERSION"

# Store changes in a temporary file
TEMP_FILE=$(mktemp)
get_latest_changes > "$TEMP_FILE"

if [ ! -s "$TEMP_FILE" ]; then
    echo "Error: Could not extract changes from CHANGELOG.md"
    rm "$TEMP_FILE"
    exit 1
fi

echo -e "\nChanges to be published:"
cat "$TEMP_FILE"

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "Error: Not a git repository"
    rm "$TEMP_FILE"
    exit 1
fi

# Check if git status is clean
echo "Check if we're in a clean git state"
if [[ -n $(git status --porcelain) ]]; then
    echo "Working directory is not clean. Committing changes..."
    # Add all changes
    git add .
    
    # Create commit with changelog entry
    git commit -m "Release version $VERSION

$(cat "$TEMP_FILE")"
fi

# Pobierz najnowsze zmiany z repozytorium zdalnego
echo "Pobieranie zmian z repozytorium zdalnego..."
git pull origin main || { echo "Nie udało się pobrać zmian. Kontynuowanie..."; }

# Sprawdź, czy tag już istnieje
if git rev-parse "v$VERSION" >/dev/null 2>&1; then
    echo "Tag v$VERSION już istnieje. Usuwanie istniejącego tagu..."
    git tag -d "v$VERSION"
    git push origin --delete "v$VERSION" || true
fi

# Create and push tag
git tag -a "v$VERSION" -m "Version $VERSION

$(cat "$TEMP_FILE")"

# Push changes and tags
echo "Pushing changes and tags to GitHub..."
git push origin main || { 
    echo "Nie udało się wypchnąć zmian. Próba ponowna po pobraniu zmian..."
    git pull origin main
    git push origin main || { echo "Nie udało się wypchnąć zmian po synchronizacji. Przerywanie."; exit 1; }
}
git push origin "v$VERSION"

# Cleanup
rm "$TEMP_FILE"

echo "Successfully published version $VERSION"
