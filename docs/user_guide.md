# Twinizer User Guide

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Command Line Interface](#command-line-interface)
- [Image Processing](#image-processing)
  - [ASCII Art Conversion](#ascii-art-conversion)
  - [Mermaid Diagram Generation](#mermaid-diagram-generation)
  - [3D Model Generation](#3d-model-generation)
- [Document Conversion](#document-conversion)
  - [PDF to Markdown](#pdf-to-markdown)
- [Hardware Analysis](#hardware-analysis)
  - [KiCad File Parsing](#kicad-file-parsing)
  - [KiCad Batch Processing](#kicad-batch-processing)
  - [Altium File Parsing](#altium-file-parsing)
- [Software Analysis](#software-analysis)
  - [Dependency Analysis](#dependency-analysis)
  - [Binary Decompilation](#binary-decompilation)
  - [Binary Disassembly](#binary-disassembly)
- [Advanced Usage](#advanced-usage)
  - [Combining Multiple Features](#combining-multiple-features)
  - [Extending Twinizer](#extending-twinizer)

## Introduction

Twinizer is a comprehensive toolkit for creating and manipulating digital twins of hardware and software systems. It provides a collection of converters, analyzers, and utilities to transform various input formats into useful representations for digital twin applications.

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

### Optional Dependencies

For full functionality, install all optional dependencies:

```bash
pip install -e .[all]
```

Or install specific feature sets:

```bash
# For image processing features
pip install -e .[image]

# For PDF processing features
pip install -e .[pdf]

# For 3D model generation
pip install -e .[3d]

# For software analysis features
pip install -e .[software]
```

## Command Line Interface

Twinizer provides a comprehensive command-line interface for all its functionality. The main entry point is the `twinizer` command.

### Listing Available Commands

```bash
twinizer list-commands
```

This will display all available commands and their descriptions.

### Command Structure

Twinizer commands follow a hierarchical structure:

```
twinizer <command-group> <command> [options]
```

For example:

```bash
twinizer image to-ascii input.jpg --width 80
```

Here, `image` is the command group, `to-ascii` is the command, and `--width 80` is an option.

### Getting Help

To get help for a specific command group or command:

```bash
twinizer <command-group> --help
twinizer <command-group> <command> --help
```

## Image Processing

### ASCII Art Conversion

The ASCII art converter transforms images into text-based art using various character sets.

#### CLI Usage

```bash
twinizer image to-ascii input.jpg --width 80 --format text
```

Options:
- `--width`: Width of ASCII art in characters (default: 80)
- `--height`: Height of ASCII art in characters (optional)
- `--format`: Output format (`text`, `html`, or `ansi`) (default: `text`)
- `--charset`: Character set to use (`standard`, `simple`, `blocks`, or `extended`) (default: `standard`)
- `--invert`: Invert brightness (flag)
- `--output`: Output file path (optional)

#### Python API

```python
from twinizer.converters.image.ascii import AsciiArtConverter

# Create converter
converter = AsciiArtConverter()

# Convert image to ASCII art
ascii_art = converter.convert(
    image_path="input.jpg",
    width=80,
    height=None,  # Auto-calculate based on aspect ratio
    output_format="text",  # "text", "html", or "ansi"
    charset="standard",  # "standard", "simple", "blocks", or "extended"
    invert=False,
    output_path=None  # If provided, saves to file
)

print(ascii_art)
```

#### Character Sets

- `standard`: Uses a range of ASCII characters based on brightness
- `simple`: Uses only a few characters for a cleaner look
- `blocks`: Uses Unicode block characters for higher resolution
- `extended`: Uses extended ASCII characters for more detail

#### Output Formats

- `text`: Plain text output
- `html`: HTML output with styling for web display
- `ansi`: Colored terminal output using ANSI escape codes

### Mermaid Diagram Generation

The Mermaid diagram generator converts images to Mermaid.js diagrams of various types.

#### CLI Usage

```bash
twinizer image to-mermaid input.jpg --diagram-type flowchart --direction TB
```

Options:
- `--diagram-type`: Type of diagram to generate (`flowchart`, `sequence`, `class`, `entity`, or `state`) (default: `flowchart`)
- `--threshold`: Threshold for edge detection (0-255) (default: 128)
- `--simplify`: Simplification factor (0-1) (default: 0.05)
- `--direction`: Direction for flowchart (`TB`, `BT`, `LR`, or `RL`) (default: `TB`)
- `--output`: Output file path (optional)

#### Python API

```python
from twinizer.converters.image.mermaid import MermaidDiagramGenerator

# Create generator
generator = MermaidDiagramGenerator()

# Convert image to flowchart
flowchart = generator.image_to_flowchart(
    image_path="input.jpg",
    threshold=128,
    simplify=0.05,
    direction="TB"  # "TB", "BT", "LR", or "RL"
)

print(flowchart)

# Convert image to sequence diagram
sequence = generator.image_to_sequence(
    image_path="input.jpg",
    threshold=128,
    simplify=0.05
)

print(sequence)

# Convert image to class diagram
class_diagram = generator.image_to_class(
    image_path="input.jpg",
    threshold=128,
    simplify=0.05
)

print(class_diagram)
```

#### Diagram Types

- `flowchart`: Node and edge based diagrams
- `sequence`: Sequence diagrams showing interactions between components
- `class`: Class diagrams showing relationships between classes
- `entity`: Entity-relationship diagrams
- `state`: State diagrams showing state transitions

### 3D Model Generation

The 3D model generator converts images to various 3D representations.

#### CLI Usage

```bash
twinizer image to-heightmap input.jpg --invert --blur 1.0 --scale 1.0
twinizer image to-normalmap input.jpg --strength 1.0
twinizer image to-mesh input.jpg --scale-z 0.1 --format obj
twinizer image to-pointcloud input.jpg --scale-z 0.1 --sample-ratio 0.1
```

Options for `to-mesh`:
- `--scale-z`: Scale factor for height values (default: 0.1)
- `--invert`: Invert height values (flag)
- `--blur`: Blur sigma (0 for no blur) (default: 1.0)
- `--format`: Output format (`obj`, `stl`, or `ply`) (default: `obj`)
- `--smooth/--no-smooth`: Smooth the mesh (default: `--smooth`)
- `--simplify/--no-simplify`: Simplify the mesh (default: `--no-simplify`)
- `--output`: Output file path (optional)

#### Python API

```python
from twinizer.converters.image.image_to_3d import (
    ImageTo3DConverter, image_to_heightmap, image_to_normalmap,
    image_to_mesh, image_to_point_cloud
)

# Using the convenience functions
heightmap_path = image_to_heightmap(
    image_path="input.jpg",
    invert=False,
    blur_sigma=1.0,
    scale_factor=1.0
)

normalmap_path = image_to_normalmap(
    image_path="input.jpg",
    strength=1.0
)

mesh_path = image_to_mesh(
    image_path="input.jpg",
    scale_z=0.1,
    invert=False,
    blur_sigma=1.0,
    smooth=True,
    simplify=False,
    output_format="obj"
)

pointcloud_path = image_to_point_cloud(
    image_path="input.jpg",
    scale_z=0.1,
    sample_ratio=0.1,
    output_format="ply"
)

# Using the class-based API for more control
converter = ImageTo3DConverter(output_dir="output")

# Convert image to height map
heightmap_path = converter.image_to_heightmap(
    image_path="input.jpg",
    invert=False,
    blur_sigma=1.0,
    scale_factor=1.0
)

# Convert height map to mesh
mesh_path = converter.heightmap_to_mesh(
    heightmap_path=heightmap_path,
    scale_z=0.1,
    smooth=True,
    simplify=False,
    output_format="obj"
)
```

#### 3D Output Formats

- `obj`: Wavefront OBJ format (widely supported)
- `stl`: STL format (common for 3D printing)
- `ply`: Stanford PLY format (point cloud and mesh)
- `xyz`: Simple point cloud format (points only)

## Document Conversion

### PDF to Markdown

The PDF to Markdown converter extracts text, images, and structure from PDF documents and converts them to Markdown format.

#### CLI Usage

```bash
twinizer pdf to-markdown input.pdf --output output.md --ocr --extract-images --toc
```

Options:
- `--output`: Output file path (optional)
- `--images-dir`: Directory to save extracted images (optional)
- `--ocr`: Use OCR for text extraction (flag)
- `--extract-images`: Extract images from PDF (flag)
- `--toc`: Generate table of contents (flag)

#### Python API

```python
from twinizer.converters.pdf2md import PDFToMarkdownConverter

# Create converter
converter = PDFToMarkdownConverter(
    use_ocr=True,  # Use OCR for text extraction
    extract_images=True,  # Extract images from PDF
    images_dir="images"  # Directory to save extracted images
)

# Convert PDF to Markdown
markdown = converter.convert(
    pdf_path="input.pdf",
    generate_toc=True  # Generate table of contents
)

# Save to file
with open("output.md", "w", encoding="utf-8") as f:
    f.write(markdown)

# To get extracted images as well
markdown, extracted_images = converter.convert(
    pdf_path="input.pdf",
    generate_toc=True,
    return_images=True  # Return list of extracted image paths
)

print(f"Extracted {len(extracted_images)} images")
```

#### Features

##### OCR (Optical Character Recognition)

When `use_ocr=True`, the converter uses Tesseract OCR to extract text from images and scanned pages. This is useful for PDFs that contain scanned documents or text embedded in images.

```python
# Create converter with OCR enabled
converter = PDFToMarkdownConverter(use_ocr=True)

# Convert PDF to Markdown
markdown = converter.convert("scanned_document.pdf")
```

##### Image Extraction

When `extract_images=True`, the converter extracts images from the PDF and saves them to the specified directory. It then creates Markdown image links to these extracted images.

```python
# Create converter with image extraction enabled
converter = PDFToMarkdownConverter(
    extract_images=True,
    images_dir="images"  # Directory to save extracted images
)

# Convert PDF to Markdown
markdown = converter.convert("document_with_images.pdf")
```

##### Table of Contents Generation

When `generate_toc=True`, the converter generates a table of contents based on the headings detected in the document.

```python
# Create converter
converter = PDFToMarkdownConverter()

# Convert PDF to Markdown with table of contents
markdown = converter.convert(
    pdf_path="document.pdf",
    generate_toc=True
)
```

##### Table Conversion

The converter automatically detects tables in the PDF and converts them to Markdown tables.

```python
# Example of a converted table in Markdown
"""
| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| Cell 1   | Cell 2   | Cell 3   |
| Cell 4   | Cell 5   | Cell 6   |
"""
```

##### Combining with Image Processing

You can combine PDF extraction with image processing to further analyze extracted images:

```python
from twinizer.converters.pdf2md import PDFToMarkdownConverter
from twinizer.converters.image.mermaid import MermaidDiagramGenerator

# Extract images from PDF
pdf_converter = PDFToMarkdownConverter(extract_images=True)
markdown, extracted_images = pdf_converter.convert("document.pdf", return_images=True)

# Convert diagrams to Mermaid
mermaid_generator = MermaidDiagramGenerator()
for image_path in extracted_images:
    # Check if image might be a diagram
    if image_path.endswith(('.png', '.jpg', '.jpeg')):
        try:
            # Try to convert to flowchart
            mermaid_diagram = mermaid_generator.image_to_flowchart(image_path)
            
            # Save Mermaid diagram
            diagram_path = image_path.replace('.png', '.mmd').replace('.jpg', '.mmd').replace('.jpeg', '.mmd')
            with open(diagram_path, 'w') as f:
                f.write(mermaid_diagram)
                
            print(f"Converted {image_path} to Mermaid diagram: {diagram_path}")
        except Exception as e:
            print(f"Failed to convert {image_path} to Mermaid: {e}")
```

## Hardware Analysis

### KiCad File Parsing

The KiCad parser extracts information from KiCad schematic (.sch) and PCB (.kicad_pcb) files.

#### CLI Usage

```bash
# Parse a schematic file
twinizer kicad parse-sch schematic.sch --format json --output schematic.json

# Parse a PCB file
twinizer kicad parse-pcb board.kicad_pcb --format json --output board.json

# Generate a bill of materials
twinizer kicad sch-to-bom schematic.sch --format csv --output bom.csv

# Convert a schematic to a Mermaid diagram
twinizer kicad sch-to-mermaid schematic.sch --diagram-type flowchart --output schematic.mmd

# Convert a PCB to a Mermaid diagram
twinizer kicad pcb-to-mermaid board.kicad_pcb --diagram-type flowchart --output pcb.mmd

# Convert a PCB to a 3D model
twinizer kicad pcb-to-3d board.kicad_pcb --format step --output board.step

# Konwersja schematu KiCad na diagram Mermaid z automatycznym ładowaniem zależności
twinizer kicad-deps sch-to-mermaid schematic.sch --diagram-type flowchart --output schematic.mmd

# Generowanie BOM ze schematu KiCad z automatycznym ładowaniem zależności
twinizer kicad-deps sch-to-bom schematic.sch --format csv --output bom.csv
```

#### Python API

```python
from twinizer.hardware.kicad.sch_parser import SchematicParser
from twinizer.hardware.kicad.pcb_parser import PCBParser
from twinizer.hardware.kicad.converters import (
    SchematicToMermaid, SchematicToBOM, PCBToMermaid, PCBTo3DModel
)

# Parse schematic
parser = SchematicParser("schematic.sch")
schematic_data = parser.parse()

# Get components
components = schematic_data.get("components", [])
print(f"Found {len(components)} components")

# Convert schematic to Mermaid diagram
converter = SchematicToMermaid("schematic.sch")
flowchart = converter.to_flowchart("schematic.mmd")

# Generate bill of materials
bom_converter = SchematicToBOM("schematic.sch")
bom_csv = bom_converter.to_csv("bom.csv")

# Parse PCB
pcb_parser = PCBParser("board.kicad_pcb")
pcb_data = pcb_parser.parse()

# Get modules
modules = pcb_data.get("modules", [])
print(f"Found {len(modules)} modules")

# Convert PCB to Mermaid diagram
pcb_converter = PCBToMermaid("board.kicad_pcb")
pcb_diagram = pcb_converter.to_flowchart("pcb.mmd")

# Convert PCB to 3D model
model_converter = PCBTo3DModel("board.kicad_pcb")
model_path = model_converter.to_step("board.step")
```

#### Features

##### Schematic Parsing

The schematic parser extracts the following information:
- Components (reference, value, footprint, datasheet, etc.)
- Nets (connections between components)
- Hierarchical sheets
- Labels and power symbols
- Component properties

##### PCB Parsing

The PCB parser extracts the following information:
- Modules (footprints)
- Tracks (copper connections)
- Zones (copper pours)
- Vias
- Text and drawings
- Board outline

##### Mermaid Diagram Generation

The converter can generate various types of Mermaid diagrams from KiCad files:
- Flowchart: Shows components and connections
- Class diagram: Shows component hierarchy
- Entity-relationship diagram: Shows relationships between components

##### Bill of Materials Generation

The BOM generator creates a bill of materials from a schematic file, with the following information:
- Reference
- Value
- Footprint
- Datasheet
- Quantity
- Supplier
- Supplier part number
- Manufacturer
- Manufacturer part number
- Description

### KiCad Batch Processing

Twinizer provides powerful batch processing capabilities for KiCad files, allowing you to convert multiple schematic and PCB files at once.

#### Batch Processing Commands

##### Batch Convert Schematics to Mermaid Diagrams

```bash
twinizer kicad batch-sch-to-mermaid --input-dir /path/to/schematics --output-dir /path/to/output --diagram-type flowchart --output-format mmd --recursive
```

Options:
- `--input-dir`, `-i`: Input directory containing schematic files (required)
- `--output-dir`, `-o`: Output directory for Mermaid diagrams (required)
- `--diagram-type`, `-d`: Type of diagram to generate (`flowchart`, `class`, or `er`) (default: `flowchart`)
- `--output-format`, `-f`: Output format (`mmd` or `svg`) (default: `mmd`)
- `--recursive`, `-r`: Search recursively in subdirectories (flag)
- `--max-workers`, `-w`: Maximum number of worker processes (default: number of CPU cores)
- `--verbose`, `-v`: Enable verbose output (flag)

##### Batch Convert Schematics to BOMs

```bash
twinizer kicad batch-sch-to-bom --input-dir /path/to/schematics --output-dir /path/to/output --output-format csv --recursive
```

Options:
- `--input-dir`, `-i`: Input directory containing schematic files (required)
- `--output-dir`, `-o`: Output directory for BOMs (required)
- `--output-format`, `-f`: Output format (`csv`, `json`, or `xlsx`) (default: `csv`)
- `--recursive`, `-r`: Search recursively in subdirectories (flag)
- `--max-workers`, `-w`: Maximum number of worker processes (default: number of CPU cores)
- `--verbose`, `-v`: Enable verbose output (flag)

##### Batch Convert PCBs to Mermaid Diagrams

```bash
twinizer kicad batch-pcb-to-mermaid --input-dir /path/to/pcbs --output-dir /path/to/output --diagram-type flowchart --output-format mmd --recursive
```

Options:
- `--input-dir`, `-i`: Input directory containing PCB files (required)
- `--output-dir`, `-o`: Output directory for Mermaid diagrams (required)
- `--diagram-type`, `-d`: Type of diagram to generate (`flowchart`, `class`, or `er`) (default: `flowchart`)
- `--output-format`, `-f`: Output format (`mmd` or `svg`) (default: `mmd`)
- `--recursive`, `-r`: Search recursively in subdirectories (flag)
- `--max-workers`, `-w`: Maximum number of worker processes (default: number of CPU cores)
- `--verbose`, `-v`: Enable verbose output (flag)

##### Batch Convert PCBs to 3D Models

```bash
twinizer kicad batch-pcb-to-3d --input-dir /path/to/pcbs --output-dir /path/to/output --format step --recursive
```

Options:
- `--input-dir`, `-i`: Input directory containing PCB files (required)
- `--output-dir`, `-o`: Output directory for 3D models (required)
- `--format`, `-f`: Output format (`step`, `stl`, `wrl`, or `obj`) (default: `step`)
- `--recursive`, `-r`: Search recursively in subdirectories (flag)
- `--max-workers`, `-w`: Maximum number of worker processes (default: number of CPU cores)
- `--verbose`, `-v`: Enable verbose output (flag)

##### Universal Batch Processing Command

For more flexibility, use the universal batch processing command:

```bash
twinizer kicad batch-process --input-dir /path/to/files --output-dir /path/to/output --file-types both --sch-conversion mermaid --pcb-conversion 3d --recursive
```

Options:
- `--input-dir`, `-i`: Input directory containing KiCad files (required)
- `--output-dir`, `-o`: Output directory for processed files (required)
- `--file-types`, `-t`: Types of files to process (`sch`, `pcb`, or `both`) (default: `both`)
- `--sch-conversion`: Conversion type for schematic files (`mermaid`, `bom`, or `json`) (default: `mermaid`)
- `--pcb-conversion`: Conversion type for PCB files (`mermaid`, `3d`, or `json`) (default: `mermaid`)
- `--sch-format`: Output format for schematic conversion (default: `mmd`)
- `--pcb-format`: Output format for PCB conversion (default: `mmd`)
- `--sch-diagram`: Diagram type for schematic Mermaid conversion (`flowchart`, `class`, or `er`) (default: `flowchart`)
- `--pcb-diagram`: Diagram type for PCB Mermaid conversion (`flowchart`, `class`, or `er`) (default: `flowchart`)
- `--recursive`, `-r`: Search recursively in subdirectories (flag)
- `--max-workers`, `-w`: Maximum number of worker processes (default: number of CPU cores)
- `--verbose`, `-v`: Enable verbose output (flag)

#### Python API for Batch Processing

You can also use the batch processing API in your Python code:

```python
from twinizer.hardware.kicad.batch_processing import (
    batch_process_schematics, batch_process_pcbs, batch_process_hardware_files
)

# Batch process schematics to Mermaid diagrams
output_files = batch_process_schematics(
    input_dir="/path/to/schematics",
    output_dir="/path/to/output",
    conversion_type="mermaid",
    output_format="mmd",
    diagram_type="flowchart",
    recursive=True,
    max_workers=4
)

# Batch process PCBs to 3D models
output_files = batch_process_pcbs(
    input_dir="/path/to/pcbs",
    output_dir="/path/to/output",
    conversion_type="3d",
    output_format="step",
    recursive=True,
    max_workers=4
)

# Batch process both schematics and PCBs
results = batch_process_hardware_files(
    input_dir="/path/to/files",
    output_dir="/path/to/output",
    file_types=["sch", "pcb"],
    conversion_types={"sch": "mermaid", "pcb": "3d"},
    output_formats={"sch": "mmd", "pcb": "step"},
    diagram_types={"sch": "flowchart", "pcb": "flowchart"},
    recursive=True,
    max_workers=4
)

# Results is a dictionary with file types as keys and lists of output files as values
sch_output_files = results["sch"]
pcb_output_files = results["pcb"]
```

#### Example Workflow

Here's a complete example workflow for batch processing KiCad files:

1. Convert all schematics in a project to Mermaid diagrams:

```bash
twinizer kicad batch-sch-to-mermaid --input-dir /path/to/project --output-dir /path/to/output/mermaid --recursive --verbose
```

2. Generate BOMs for all schematics:

```bash
twinizer kicad batch-sch-to-bom --input-dir /path/to/project --output-dir /path/to/output/bom --output-format csv --recursive --verbose
```

3. Convert all PCBs to 3D models:

```bash
twinizer kicad batch-pcb-to-3d --input-dir /path/to/project --output-dir /path/to/output/3d --format step --recursive --verbose
```

4. Or do all of the above in one command:

```bash
twinizer kicad batch-process --input-dir /path/to/project --output-dir /path/to/output --sch-conversion mermaid --pcb-conversion 3d --recursive --verbose
```

### Altium File Parsing

The Altium parser extracts information from Altium Designer files.

#### CLI Usage

```bash
twinizer altium parse-sch schematic.SchDoc --format json --output schematic.json
twinizer altium parse-pcb board.PcbDoc --format json --output board.json
twinizer altium generate-bom project.PrjPcb --format csv --output bom.csv
```

#### Python API

```python
from twinizer.hardware.altium.sch_parser import AltiumSchematicParser
from twinizer.hardware.altium.pcb_parser import AltiumPCBParser
from twinizer.hardware.altium.converters import (
    schematic_to_mermaid, pcb_to_mermaid, generate_bom
)

# Parse schematic
parser = AltiumSchematicParser("schematic.SchDoc")
schematic_data = parser.parse()

# Get components
components = schematic_data.get("components", [])
print(f"Found {len(components)} components")

# Convert schematic to Mermaid diagram
mermaid_diagram = schematic_to_mermaid(schematic_data)

# Generate bill of materials
bom = generate_bom(schematic_data, format="csv")
```

## Software Analysis

### Dependency Analysis

The dependency analyzer extracts and visualizes dependencies in software projects.

#### CLI Usage

```bash
twinizer software analyze-deps /path/to/project --format json --output deps.json
```

Options:
- `--format`: Output format (`text`, `json`, `xml`, or `dot`) (default: `text`)
- `--output`: Output file path (optional)
- `--include-dev`: Include development dependencies (flag)
- `--max-depth`: Maximum depth for recursive dependencies (default: 3)

#### Python API

```python
from twinizer.software.analyze.dependency import DependencyAnalyzer

# Create analyzer
analyzer = DependencyAnalyzer("/path/to/project")

# Detect project type
project_type = analyzer.detect_project_type()
print(f"Detected project type: {project_type}")

# Analyze dependencies
dependencies = analyzer.analyze(
    include_dev=False,  # Include development dependencies
    max_depth=3  # Maximum depth for recursive dependencies
)

# Display dependency tree
analyzer.display_tree(dependencies)

# Save results
analyzer.save_results(
    dependencies,
    output_path="deps.json",
    output_format="json"
)
```

#### Supported Project Types

The dependency analyzer supports various project types:
- Python (requirements.txt, setup.py, pyproject.toml)
- JavaScript/Node.js (package.json)
- Java (pom.xml, build.gradle)
- C/C++ (CMakeLists.txt, Makefile)
- Rust (Cargo.toml)
- Go (go.mod)

#### Output Formats

- `text`: Plain text tree representation
- `json`: JSON format for further processing
- `xml`: XML format for integration with other tools
- `dot`: GraphViz DOT format for visualization

### Binary Decompilation

The binary decompiler converts binary files to higher-level representations.

#### CLI Usage

```bash
twinizer software decompile binary.elf --format c --output decompiled.c
```

Options:
- `--format`: Output format (`c`, `cpp`, or `pseudocode`) (default: `c`)
- `--decompiler`: Decompiler to use (`ghidra`, `ida`, `retdec`, or `auto`) (default: `auto`)
- `--function`: Function to decompile (optional)
- `--output`: Output file path (optional)

#### Python API

```python
from twinizer.software.decompile.elf import ELFDecompiler

# Create decompiler
decompiler = ELFDecompiler("binary.elf")

# Get binary info
binary_info = decompiler.get_binary_info()
print(f"Architecture: {binary_info.get('architecture')}")
print(f"Endianness: {binary_info.get('endianness')}")
print(f"Bit width: {binary_info.get('bit_width')}")

# List functions
functions = decompiler.list_functions()
for func in functions[:10]:  # Show first 10 functions
    print(f"Function: {func.get('name')}, Address: {func.get('address')}")

# Decompile entire binary
decompiled_code = decompiler.decompile(
    output_format="c",
    decompiler_tool="auto",
    output_path=None
)

# Decompile specific function
decompiled_function = decompiler.decompile(
    output_format="c",
    decompiler_tool="auto",
    function_name="main",
    output_path=None
)
```

#### Supported Decompilers

- `ghidra`: Uses Ghidra's headless analyzer
- `ida`: Uses IDA Pro's command-line interface
- `retdec`: Uses RetDec decompiler
- `auto`: Automatically selects the best available decompiler

#### Output Formats

- `c`: C code
- `cpp`: C++ code
- `pseudocode`: High-level pseudocode

### Binary Disassembly

The binary disassembler converts binary files to assembly code.

#### CLI Usage

```bash
twinizer software disassemble binary.elf --format text --output disassembled.asm
```

Options:
- `--format`: Output format (`text`, `html`, or `json`) (default: `text`)
- `--disassembler`: Disassembler to use (`objdump`, `radare2`, `capstone`, or `auto`) (default: `auto`)
- `--function`: Function to disassemble (optional)
- `--output`: Output file path (optional)

#### Python API

```python
from twinizer.software.disassemble.binary import BinaryDisassembler

# Create disassembler
disassembler = BinaryDisassembler("binary.elf")

# Get binary info
binary_info = disassembler.get_binary_info()
print(f"Architecture: {binary_info.get('architecture')}")
print(f"Endianness: {binary_info.get('endianness')}")
print(f"Bit width: {binary_info.get('bit_width')}")

# List functions
functions = disassembler.list_functions()
for func in functions[:10]:  # Show first 10 functions
    print(f"Function: {func.get('name')}, Address: {func.get('address')}")

# Disassemble entire binary
disassembled_code = disassembler.disassemble(
    output_format="text",
    disassembler_tool="auto",
    output_path=None
)

# Disassemble specific function
disassembled_function = disassembler.disassemble(
    output_format="text",
    disassembler_tool="auto",
    function_name="main",
    output_path=None
)
```

#### Supported Disassemblers

- `objdump`: Uses GNU objdump
- `radare2`: Uses radare2's command-line interface
- `capstone`: Uses Capstone disassembly framework
- `auto`: Automatically selects the best available disassembler

#### Output Formats

- `text`: Plain text assembly code
- `html`: HTML-formatted assembly code with syntax highlighting
- `json`: JSON format for further processing

## Advanced Usage

### Combining Multiple Features

Twinizer's modular design allows you to combine multiple features for complex workflows.

#### Example: Hardware and Software Analysis Pipeline

```python
from twinizer.hardware.kicad.sch_parser import SchematicParser
from twinizer.hardware.kicad.converters import generate_bom
from twinizer.software.analyze.dependency import DependencyAnalyzer
from twinizer.converters.pdf2md import PDFToMarkdownConverter

# Parse hardware schematic
sch_parser = SchematicParser("project.sch")
schematic_data = sch_parser.parse()

# Generate BOM
bom = generate_bom(schematic_data, format="csv")
with open("bom.csv", "w") as f:
    f.write(bom)

# Analyze software dependencies
dep_analyzer = DependencyAnalyzer("firmware/")
dependencies = dep_analyzer.analyze()
dep_analyzer.save_results(dependencies, "dependencies.json", "json")

# Convert documentation
pdf_converter = PDFToMarkdownConverter(extract_images=True)
markdown = pdf_converter.convert("documentation.pdf")
with open("documentation.md", "w", encoding="utf-8") as f:
    f.write(markdown)

print("Analysis pipeline completed successfully!")
```

#### Example: Image Processing Pipeline

```python
from twinizer.converters.image.ascii import AsciiArtConverter
from twinizer.converters.image.mermaid import MermaidDiagramGenerator
from twinizer.converters.image.image_to_3d import ImageTo3DConverter

# Create converters
ascii_converter = AsciiArtConverter()
mermaid_generator = MermaidDiagramGenerator()
model_converter = ImageTo3DConverter(output_dir="3d_models")

# Process image in multiple ways
image_path = "input.jpg"

# Convert to ASCII art
ascii_art = ascii_converter.convert(
    image_path=image_path,
    width=80,
    output_format="html",
    output_path="output.html"
)

# Convert to Mermaid diagram
mermaid_diagram = mermaid_generator.image_to_flowchart(
    image_path=image_path,
    output_path="output.mmd"
)

# Convert to 3D model
heightmap_path = model_converter.image_to_heightmap(image_path)
mesh_path = model_converter.heightmap_to_mesh(
    heightmap_path=heightmap_path,
    output_format="obj"
)

print(f"Generated ASCII art: output.html")
print(f"Generated Mermaid diagram: output.mmd")
print(f"Generated 3D model: {mesh_path}")
```

### Extending Twinizer

Twinizer is designed to be extensible. You can add new converters, parsers, or analyzers by following the existing patterns.

#### Example: Creating a Custom Converter

```python
from twinizer.converters.base import BaseConverter
from PIL import Image
import numpy as np

class CustomImageConverter(BaseConverter):
    """Custom image converter example."""
    
    def __init__(self, output_dir=None):
        """Initialize the converter."""
        super().__init__(output_dir)
    
    def convert(self, image_path, output_path=None, **kwargs):
        """Convert image using custom algorithm."""
        # Load image
        img = Image.open(image_path)
        
        # Convert to numpy array
        img_array = np.array(img)
        
        # Apply custom processing
        processed = self._custom_process(img_array, **kwargs)
        
        # Create output image
        output_img = Image.fromarray(processed)
        
        # Save or return
        if output_path:
            output_img.save(output_path)
            return output_path
        else:
            return output_img
    
    def _custom_process(self, img_array, factor=1.0):
        """Custom processing algorithm."""
        # Example: adjust brightness
        return np.clip(img_array * factor, 0, 255).astype(np.uint8)

# Usage
converter = CustomImageConverter()
result = converter.convert("input.jpg", factor=1.2, output_path="output.jpg")
```

#### Example: Creating a Custom CLI Command

```python
# In your_module.py
import click
from rich.console import Console

console = Console()

@click.group(name="custom", help="Custom commands")
def custom_group():
    """Custom command group."""
    pass

@custom_group.command(name="process", help="Process something")
@click.argument("input_path", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--parameter", "-p", type=float, default=1.0, help="Processing parameter")
def process_command(input_path, output, parameter):
    """Process something with custom logic."""
    try:
        # Your processing logic here
        console.print(f"Processing {input_path} with parameter {parameter}")
        
        # Example result
        result = f"Processed content: {input_path} * {parameter}"
        
        # Save or display result
        if output:
            with open(output, "w") as f:
                f.write(result)
            console.print(f"[green]Result saved to: {output}[/green]")
        else:
            console.print(result)
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback
        console.print(traceback.format_exc())
        return 1

# Then register in twinizer/cli/commands/custom.py
# This will be automatically picked up by the CLI
```

## Conclusion

This user guide covers the main features and capabilities of the Twinizer package. For more detailed information, refer to the API documentation or the example scripts in the `examples/` directory.

If you encounter any issues or have questions, please open an issue on the GitHub repository or contact the maintainers.
