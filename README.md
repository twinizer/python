# Twinizer

## Overview

Twinizer is a comprehensive toolkit for creating and manipulating digital twins of hardware and software systems. It provides a collection of converters, analyzers, and utilities to transform various input formats into useful representations for digital twin applications.

## Features

### Hardware Analysis
- **KiCad Integration**: Parse and convert KiCad schematics and PCB layouts
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

## Usage

### Command Line Interface

Twinizer provides a comprehensive command-line interface for all its functionality:

```bash
# Show available commands
twinizer list-commands

# Convert an image to ASCII art
twinizer image to-ascii input.jpg --width 80

# Generate a 3D mesh from an image
twinizer image to-mesh input.jpg --output output.obj

# Analyze software dependencies
twinizer software analyze-deps /path/to/project

# Parse a KiCad schematic
twinizer kicad parse-sch schematic.sch --format json
```

### Python API

You can also use Twinizer as a Python library:

```python
from twinizer.converters.image.ascii import AsciiArtConverter
from twinizer.converters.image.image_to_3d import image_to_mesh
from twinizer.software.analyze.dependency import DependencyAnalyzer

# Convert image to ASCII art
converter = AsciiArtConverter()
ascii_art = converter.convert("input.jpg", width=80)

# Generate 3D mesh from image
mesh_path = image_to_mesh("input.jpg", scale_z=0.1, output_format="obj")

# Analyze project dependencies
analyzer = DependencyAnalyzer("/path/to/project")
dependencies = analyzer.analyze()
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

## Dependencies

Twinizer has the following core dependencies:

- Python 3.8+
- Click: Command-line interface
- Rich: Terminal formatting
- Pillow: Image processing
- NumPy: Numerical operations

Optional dependencies for specific features:

- trimesh: 3D mesh processing
- scikit-image: Advanced image processing
- matplotlib: Visualization
- PyPDF2: PDF processing

## Examples

See the `examples/` directory for example scripts demonstrating various features of Twinizer.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
