#!/bin/bash

# Run tests
echo "Running tests..."
pytest tests/ || { echo "Tests failed"; exit 1; }

# Check code style
echo "Checking code style..."
black --check src/ examples/ tests/
isort --check-only src/ examples/ tests/
flake8 src/ examples/ tests/
tox -e py312

