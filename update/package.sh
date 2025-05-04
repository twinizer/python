#!/bin/bash

# Build script for inspectomat Hardware library

echo "Building inspectomat Hardware Library..."

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info/


# Build package
echo "Building package..."
python -m build

# Create documentation
echo "Generating documentation..."
sphinx-apidoc -o docs/source src/inspectomat_hardware
cd docs && make html && cd ..

echo "Build complete!"
echo "Distribution packages available in dist/"
echo "Documentation available in docs/_build/html/"