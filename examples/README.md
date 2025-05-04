# Twinizer Examples

This directory contains example scripts demonstrating various features of the Twinizer package. These examples show how to use the Python API for different functionalities.

## Available Examples

### Image Processing

- **[image_to_ascii.py](image_to_ascii.py)**: Convert images to ASCII art in different formats
- **[image_to_3d.py](image_to_3d.py)**: Convert images to 3D representations (height maps, normal maps, meshes, point clouds)

### Hardware Analysis

- **[kicad_parsing.py](kicad_parsing.py)**: Parse KiCad schematic and PCB files, convert to other formats

### Software Analysis

- **[software_analysis.py](software_analysis.py)**: Analyze software projects (dependencies, decompilation, disassembly)

### Document Conversion

- **[pdf_to_markdown.py](pdf_to_markdown.py)**: Convert PDF documents to Markdown format

## Running the Examples

All examples can be run directly from the command line. Each example supports the `--help` flag to show available options.

### Prerequisites

Make sure you have installed the Twinizer package and its dependencies:

```bash
pip install -e .
```

Or install with optional dependencies for full functionality:

```bash
pip install -e .[all]
```

### Example Usage

#### Convert an image to ASCII art:

```bash
python examples/image_to_ascii.py path/to/image.jpg --width 80 --format ansi
```

#### Convert an image to a 3D mesh:

```bash
python examples/image_to_3d.py path/to/image.jpg --scale-z 0.2 --format obj
```

#### Analyze software dependencies:

```bash
python examples/software_analysis.py analyze-deps path/to/project --format json --output deps.json
```

#### Parse a KiCad schematic:

```bash
python examples/kicad_parsing.py parse-sch path/to/schematic.sch --format mermaid --output schematic.md
```

#### Convert a PDF to Markdown:

```bash
python examples/pdf_to_markdown.py path/to/document.pdf --output document.md --extract-images --toc
```

## Example Output

The examples will either display the results in the terminal or save them to the specified output file. For visual outputs like ASCII art or Mermaid diagrams, the results will be displayed in the terminal if no output file is specified.

## Creating Your Own Scripts

You can use these examples as templates for creating your own scripts. The basic pattern is:

1. Import the required modules from Twinizer
2. Create an instance of the appropriate class
3. Call the methods with the desired parameters
4. Process or display the results

For more details, refer to the [Twinizer documentation](../docs/).
