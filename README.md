# Twinizer

## Overview

Twinizer is a comprehensive toolkit for creating and manipulating digital twins of hardware and software systems. It provides a collection of converters, analyzers, and utilities to transform various input formats into useful representations for digital twin applications.

## Features

### Hardware Analysis
- **KiCad Integration**: Parse and convert KiCad schematics and PCB layouts
- **KiCad Docker Integration**: Convert KiCad files to various formats (SVG, PNG, PDF, DXF, HPGL, PS, EPS) and analyze projects using Docker
- **Altium Integration**: Support for Altium Designer files
- **3D Model Generation**: Convert PCB designs to 3D models

### Software Analysis
- **Dependency Analysis**: Analyze project dependencies across various languages and build systems
- **Decompilation**: Convert binary files to higher-level representations
- **Disassembly**: Disassemble binary files into assembly code

### Converters
- **PDF to Markdown**: Convert PDF documents to Markdown format
- **Image Processing**:
  - ASCII Art: Convert images to ASCII art
  - Mermaid Diagrams: Generate Mermaid diagrams from images
  - 3D Models: Convert images to height maps, normal maps, 3D meshes, and point clouds
- **Binary to Source**: Convert binary files to source code representations

## Installation

### Using pip

```bash
pip install twinizer
```

### From Source

```bash
git clone https://github.com/yourusername/twinizer.git
cd twinizer
pip install -e .
```

### Dependencies

Twinizer has several optional dependencies that enable specific features:

```bash
# For image processing features
pip install matplotlib

# For KiCad integration (required for hardware analysis)
# KiCad must be installed on your system for full functionality

# For KiCad Docker integration
# Docker must be installed and running on your system

# For PDF conversion
pip install pdfminer.six

# For all optional dependencies
pip install twinizer[all]
```

## Usage

### Command Line Interface

Twinizer provides a comprehensive command-line interface for all its functionality:

```bash
# Show help and available commands
twinizer --help

# Analyze project structure
twinizer analyze structure --source-dir /path/to/project

# Convert between file formats
twinizer convert pdf-to-markdown /path/to/document.pdf --output document.md

# Work with KiCad files
twinizer kicad sch-to-mermaid /path/to/schematic.sch --diagram-type flowchart --output schematic.mmd
twinizer kicad sch-to-bom /path/to/schematic.sch --format csv --output bom.csv
twinizer kicad pcb-to-mermaid /path/to/pcb.kicad_pcb --diagram-type flowchart --output pcb.mmd

# Work with KiCad files using Docker
twinizer kicad-docker convert /path/to/schematic.kicad_sch --format svg --output schematic.svg
twinizer kicad-docker convert /path/to/schematic.kicad_sch --format pdf --color-theme dark --paper-size A3 --orientation landscape
twinizer kicad-docker analyze /path/to/kicad_project --format html --output report.html
twinizer kicad-docker formats
```

## Project Structure

```
twinizer/
├── src/
│   ├── twinizer/
│   │   ├── cli/               # Command-line interface
│   │   │   └── commands/      # CLI command modules
│   │   ├── converters/        # File format converters
│   │   │   ├── pdf2md/        # PDF to Markdown conversion
│   │   │   ├── image/         # Image processing
│   │   │   └── bin2source/    # Binary to source code conversion
│   │   ├── hardware/          # Hardware analysis
│   │   │   ├── kicad/         # KiCad file parsing
│   │   │   └── altium/        # Altium file parsing
│   │   ├── software/          # Software analysis
│   │   │   ├── analyze/       # Code analysis
│   │   │   ├── decompile/     # Decompilation
│   │   │   └── disassemble/   # Disassembly
│   │   └── utils/             # Utility functions
├── scripts/                   # Utility scripts
├── tests/                     # Test suite
├── docs/                      # Documentation
├── examples/                  # Example code
├── pyproject.toml             # Project configuration
└── README.md                  # This file
```

## Examples

See the `examples/` directory for example scripts demonstrating various features of Twinizer.

## Contributing

Contributions are welcome! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) file for detailed guidelines on how to contribute to this project.

### Development Workflow

This project uses GitHub Actions for continuous integration. On each push to the main branch and pull requests, the pipeline will:
- Run tests on multiple Python versions
- Check code formatting with Black
- Verify import ordering with isort
- Run linting with flake8
- Build the package

### Documentation

The project documentation is available on GitHub Pages at [https://yourusername.github.io/twinizer/](https://yourusername.github.io/twinizer/).

Documentation is written in Markdown with Mermaid diagram support. To contribute to the documentation:
1. Edit the files in the `docs/` directory
2. Submit a pull request
3. Once merged, the documentation will be automatically updated on GitHub Pages

## License

This project is licensed under the MIT License - see the LICENSE file for details.
