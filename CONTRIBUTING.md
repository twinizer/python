# Contributing to Twinizer

Thank you for considering contributing to Twinizer! This document outlines the process for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please be respectful and considerate of others.

## How Can I Contribute?

### Reporting Bugs

If you find a bug, please create an issue on our GitHub repository with the following information:

- A clear, descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Any relevant logs or screenshots
- Your environment (OS, Python version, etc.)

### Suggesting Features

We welcome feature suggestions! Please create an issue with:

- A clear, descriptive title
- A detailed description of the proposed feature
- Any relevant examples or use cases
- If possible, an outline of how you envision the implementation

### Pull Requests

We actively welcome your pull requests:

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. If you've changed APIs, update the documentation
4. Ensure the test suite passes
5. Make sure your code follows the existing style
6. Submit your pull request!

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/twinizer.git
   cd twinizer
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```

3. Run tests to ensure everything is working:
   ```bash
   pytest
   ```

## Coding Style

We use the following tools to maintain code quality:

- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting

Before submitting a pull request, please run:

```bash
black src tests
isort src tests
flake8 src tests
```

## Testing

We use pytest for testing. Please write tests for new code you create and ensure all tests pass before submitting a pull request:

```bash
pytest
```

## Documentation

Good documentation is crucial for our project. Please update the documentation when necessary:

- Update docstrings for any new or modified functions, classes, or modules
- Update the README.md if necessary
- Add examples for new features

## Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Reference issues and pull requests liberally after the first line

## Versioning

We follow [Semantic Versioning](https://semver.org/). In general:

- MAJOR version for incompatible API changes
- MINOR version for new functionality in a backwards compatible manner
- PATCH version for backwards compatible bug fixes

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License.

## Questions?

If you have any questions, feel free to create an issue with the "question" label or reach out to the maintainers directly.

Thank you for contributing to Twinizer!
