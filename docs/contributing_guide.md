# Contributing to Twinizer

This guide provides detailed information on how to contribute to the Twinizer project, including our development workflow, documentation process, and GitHub integration.

## Development Workflow

### GitHub Actions Pipeline

Twinizer uses GitHub Actions for continuous integration. Our pipeline automatically runs on each push to the main branch and on pull requests.

The pipeline performs the following checks:

```mermaid
graph TD
    A[Push to Repository] --> B[GitHub Actions Trigger]
    B --> C[Install Dependencies]
    C --> D[Run Tests on Python 3.9, 3.10, 3.11]
    C --> E[Check Code Formatting with Black]
    C --> F[Verify Import Ordering with isort]
    C --> G[Run Linting with flake8]
    C --> H[Build Python Package]
    D & E & F & G & H --> I{All Checks Pass?}
    I -->|Yes| J[Pipeline Success]
    I -->|No| K[Pipeline Failure]
```

### Local Development Setup

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

### Code Style

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

## Documentation

### GitHub Pages

Our documentation is hosted on GitHub Pages at [https://yourusername.github.io/twinizer/](https://yourusername.github.io/twinizer/).

The site is automatically built from the Markdown files in the `docs/` directory and the project's README.md.

### Mermaid Diagrams

Twinizer documentation supports Mermaid diagrams, which are automatically rendered when viewed on GitHub or GitHub Pages.

To add a Mermaid diagram to your documentation:

````markdown
```mermaid
graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]
```
````

### Documentation Structure

The documentation is organized as follows:

```mermaid
graph TD
    A[docs/] --> B[user_guide.md]
    A --> C[hardware_analysis.md]
    A --> D[image_processing.md]
    A --> E[pdf_to_markdown.md]
    A --> F[kicad_docker.md]
    A --> G[contributing_guide.md]
    A --> H[programator/]
    A --> I[twinizer/]
```

## Pull Request Process

1. Fork the repo and create your branch from `main`
2. Make your changes, following our code style guidelines
3. Add tests for any new functionality
4. Update documentation as needed
5. Ensure all tests pass and the GitHub Actions pipeline succeeds
6. Submit your pull request with a clear description of the changes

## Release Process

Twinizer follows [Semantic Versioning](https://semver.org/):

- MAJOR version for incompatible API changes
- MINOR version for new functionality in a backwards compatible manner
- PATCH version for backwards compatible bug fixes

The release process is as follows:

```mermaid
graph TD
    A[Merge Changes to Main] --> B[Update Version Number]
    B --> C[Update CHANGELOG.md]
    C --> D[Create GitHub Release]
    D --> E[Publish to PyPI]
```

## Questions and Support

If you have questions or need support, please:

1. Check the existing documentation
2. Look for similar issues in the GitHub issue tracker
3. Create a new issue with the "question" label if needed

Thank you for contributing to Twinizer!
