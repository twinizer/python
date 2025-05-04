# Hardware Analysis in Twinizer

## Table of Contents
- [Introduction](#introduction)
- [KiCad File Parsing](#kicad-file-parsing)
  - [Schematic Parsing](#schematic-parsing)
  - [PCB Parsing](#pcb-parsing)
  - [BOM Generation](#bom-generation)
  - [Mermaid Diagram Generation](#mermaid-diagram-generation)
- [Altium File Parsing](#altium-file-parsing)
  - [Schematic Parsing](#altium-schematic-parsing)
  - [PCB Parsing](#altium-pcb-parsing)
  - [BOM Generation](#altium-bom-generation)
- [Advanced Usage](#advanced-usage)
- [API Reference](#api-reference)

## Introduction

Twinizer provides comprehensive hardware analysis capabilities that allow you to parse and analyze electronic design files from popular EDA tools like KiCad and Altium Designer. This document covers the main hardware analysis features and provides detailed examples of their usage.

## KiCad File Parsing

Twinizer can parse KiCad schematic (.sch) and PCB (.kicad_pcb) files to extract component information, connections, and other design data.

### Command Line Usage

```bash
# Parse a schematic file
twinizer kicad parse-sch schematic.sch --format json --output schematic.json

# Parse a PCB file
twinizer kicad parse-pcb board.kicad_pcb --format json --output board.json

# Generate a bill of materials
twinizer kicad generate-bom schematic.sch --format csv --output bom.csv

# Convert a schematic to a Mermaid diagram
twinizer kicad to-mermaid schematic.sch --diagram-type flowchart --output schematic.mmd
```

### Python API

```python
from twinizer.hardware.kicad.sch_parser import SchematicParser
from twinizer.hardware.kicad.pcb_parser import PCBParser
from twinizer.hardware.kicad.converters import (
    schematic_to_mermaid, pcb_to_mermaid, generate_bom
)

# Parse a schematic file
sch_parser = SchematicParser("schematic.sch")
schematic_data = sch_parser.parse()

# Access component information
components = schematic_data.get("components", [])
for component in components[:5]:  # Show first 5 components
    print(f"Reference: {component.get('reference')}, Value: {component.get('value')}")

# Access net information
nets = schematic_data.get("nets", [])
print(f"Found {len(nets)} nets")

# Convert to Mermaid diagram
mermaid_diagram = schematic_to_mermaid(
    schematic_data,
    diagram_type="flowchart",
    direction="TB"
)

# Generate bill of materials
bom = generate_bom(
    schematic_data,
    format="csv"
)

# Parse a PCB file
pcb_parser = PCBParser("board.kicad_pcb")
pcb_data = pcb_parser.parse()

# Access module information
modules = pcb_data.get("modules", [])
print(f"Found {len(modules)} modules")
```

### Schematic Parsing

The schematic parser extracts the following information from KiCad schematic files:

- **Components**: Reference designators, values, footprints, datasheets, etc.
- **Nets**: Connections between components
- **Hierarchical Sheets**: Sheet structure and hierarchy
- **Labels and Power Symbols**: Signal labels and power connections
- **Component Properties**: Custom properties and annotations

#### Example: Extracting Component Information

```python
from twinizer.hardware.kicad.sch_parser import SchematicParser

# Parse schematic
parser = SchematicParser("schematic.sch")
schematic_data = parser.parse()

# Get components
components = schematic_data.get("components", [])
print(f"Found {len(components)} components")

# Print component details
for component in components[:10]:  # Show first 10 components
    print(f"Reference: {component.get('reference')}")
    print(f"  Value: {component.get('value')}")
    print(f"  Footprint: {component.get('footprint')}")
    print(f"  Datasheet: {component.get('datasheet')}")
    print(f"  Position: ({component.get('position', {}).get('x')}, {component.get('position', {}).get('y')})")
    print(f"  Fields: {component.get('fields', [])}")
    print()
```

#### Example: Analyzing Nets

```python
from twinizer.hardware.kicad.sch_parser import SchematicParser

# Parse schematic
parser = SchematicParser("schematic.sch")
schematic_data = parser.parse()

# Get nets
nets = schematic_data.get("nets", [])
print(f"Found {len(nets)} nets")

# Print net details
for net in nets[:10]:  # Show first 10 nets
    print(f"Net: {net.get('name')}")
    print(f"  Code: {net.get('code')}")
    print(f"  Connections: {len(net.get('connections', []))}")
    for conn in net.get('connections', [])[:5]:  # Show first 5 connections
        print(f"    {conn.get('component')} pin {conn.get('pin')}")
    print()
```

### PCB Parsing

The PCB parser extracts the following information from KiCad PCB files:

- **Modules**: Footprints and their placements
- **Tracks**: Copper connections between pads
- **Zones**: Copper pours and ground planes
- **Vias**: Through-hole connections between layers
- **Text and Drawings**: Annotations and graphical elements
- **Board Outline**: The physical boundaries of the PCB

#### Example: Extracting Module Information

```python
from twinizer.hardware.kicad.pcb_parser import PCBParser

# Parse PCB
parser = PCBParser("board.kicad_pcb")
pcb_data = parser.parse()

# Get modules
modules = pcb_data.get("modules", [])
print(f"Found {len(modules)} modules")

# Print module details
for module in modules[:10]:  # Show first 10 modules
    print(f"Reference: {module.get('reference')}")
    print(f"  Value: {module.get('value')}")
    print(f"  Layer: {module.get('layer')}")
    print(f"  Position: ({module.get('position', {}).get('x')}, {module.get('position', {}).get('y')})")
    print(f"  Rotation: {module.get('rotation')}")
    print(f"  Pads: {len(module.get('pads', []))}")
    print()
```

#### Example: Analyzing Tracks

```python
from twinizer.hardware.kicad.pcb_parser import PCBParser

# Parse PCB
parser = PCBParser("board.kicad_pcb")
pcb_data = parser.parse()

# Get tracks
tracks = pcb_data.get("tracks", [])
print(f"Found {len(tracks)} tracks")

# Group tracks by layer
tracks_by_layer = {}
for track in tracks:
    layer = track.get("layer")
    if layer not in tracks_by_layer:
        tracks_by_layer[layer] = []
    tracks_by_layer[layer].append(track)

# Print track statistics by layer
for layer, layer_tracks in tracks_by_layer.items():
    print(f"Layer {layer}: {len(layer_tracks)} tracks")
```

### BOM Generation

The BOM generator creates a bill of materials from a schematic file, with the following information:

- **Reference**: Component reference designator
- **Value**: Component value
- **Footprint**: Component footprint
- **Datasheet**: Link to component datasheet
- **Quantity**: Number of components with the same value and footprint
- **Supplier**: Component supplier (if available)
- **Supplier Part Number**: Supplier's part number (if available)
- **Manufacturer**: Component manufacturer (if available)
- **Manufacturer Part Number**: Manufacturer's part number (if available)
- **Description**: Component description (if available)

#### Example: Generating a BOM

```python
from twinizer.hardware.kicad.sch_parser import SchematicParser
from twinizer.hardware.kicad.converters import generate_bom

# Parse schematic
parser = SchematicParser("schematic.sch")
schematic_data = parser.parse()

# Generate BOM in CSV format
bom_csv = generate_bom(
    schematic_data,
    format="csv"
)

# Save to file
with open("bom.csv", "w") as f:
    f.write(bom_csv)

# Generate BOM in JSON format
bom_json = generate_bom(
    schematic_data,
    format="json"
)

# Save to file
with open("bom.json", "w") as f:
    f.write(bom_json)
```

#### Example: Customizing BOM Generation

```python
from twinizer.hardware.kicad.sch_parser import SchematicParser
from twinizer.hardware.kicad.converters import generate_bom

# Parse schematic
parser = SchematicParser("schematic.sch")
schematic_data = parser.parse()

# Generate BOM with custom options
bom_csv = generate_bom(
    schematic_data,
    format="csv",
    group_by=["value", "footprint"],  # Group components by value and footprint
    exclude_references=["TP.*", "MH.*"],  # Exclude test points and mounting holes
    include_fields=["Reference", "Value", "Footprint", "Datasheet", "Supplier", "Cost"],  # Specify fields to include
    sort_by="Reference"  # Sort by reference designator
)

# Save to file
with open("custom_bom.csv", "w") as f:
    f.write(bom_csv)
```

### Mermaid Diagram Generation

Twinizer can convert KiCad schematics to Mermaid diagrams for visualization.

#### Example: Converting a Schematic to a Flowchart

```python
from twinizer.hardware.kicad.sch_parser import SchematicParser
from twinizer.hardware.kicad.converters import schematic_to_mermaid

# Parse schematic
parser = SchematicParser("schematic.sch")
schematic_data = parser.parse()

# Convert to Mermaid flowchart
flowchart = schematic_to_mermaid(
    schematic_data,
    diagram_type="flowchart",
    direction="TB"
)

# Save to file
with open("schematic_flowchart.mmd", "w") as f:
    f.write(flowchart)
```

#### Example: Converting a Schematic to a Class Diagram

```python
from twinizer.hardware.kicad.sch_parser import SchematicParser
from twinizer.hardware.kicad.converters import schematic_to_mermaid

# Parse schematic
parser = SchematicParser("schematic.sch")
schematic_data = parser.parse()

# Convert to Mermaid class diagram
class_diagram = schematic_to_mermaid(
    schematic_data,
    diagram_type="class"
)

# Save to file
with open("schematic_class.mmd", "w") as f:
    f.write(class_diagram)
```

## Altium File Parsing

Twinizer can parse Altium Designer schematic (.SchDoc) and PCB (.PcbDoc) files to extract component information, connections, and other design data.

### Command Line Usage

```bash
# Parse a schematic file
twinizer altium parse-sch schematic.SchDoc --format json --output schematic.json

# Parse a PCB file
twinizer altium parse-pcb board.PcbDoc --format json --output board.json

# Generate a bill of materials
twinizer altium generate-bom project.PrjPcb --format csv --output bom.csv
```

### Python API

```python
from twinizer.hardware.altium.sch_parser import AltiumSchematicParser
from twinizer.hardware.altium.pcb_parser import AltiumPCBParser
from twinizer.hardware.altium.converters import (
    schematic_to_mermaid, pcb_to_mermaid, generate_bom
)

# Parse a schematic file
sch_parser = AltiumSchematicParser("schematic.SchDoc")
schematic_data = sch_parser.parse()

# Access component information
components = schematic_data.get("components", [])
for component in components[:5]:  # Show first 5 components
    print(f"Designator: {component.get('designator')}, Comment: {component.get('comment')}")

# Convert to Mermaid diagram
mermaid_diagram = schematic_to_mermaid(schematic_data)

# Generate bill of materials
bom = generate_bom(schematic_data, format="csv")
```

### Altium Schematic Parsing

The Altium schematic parser extracts the following information from Altium schematic files:

- **Components**: Designators, comments, footprints, etc.
- **Nets**: Connections between components
- **Sheets**: Sheet structure and hierarchy
- **Parameters**: Component parameters and properties
- **Annotations**: Text and graphical elements

#### Example: Extracting Component Information

```python
from twinizer.hardware.altium.sch_parser import AltiumSchematicParser

# Parse schematic
parser = AltiumSchematicParser("schematic.SchDoc")
schematic_data = parser.parse()

# Get components
components = schematic_data.get("components", [])
print(f"Found {len(components)} components")

# Print component details
for component in components[:10]:  # Show first 10 components
    print(f"Designator: {component.get('designator')}")
    print(f"  Comment: {component.get('comment')}")
    print(f"  Footprint: {component.get('footprint')}")
    print(f"  Library: {component.get('library')}")
    print(f"  Position: ({component.get('position', {}).get('x')}, {component.get('position', {}).get('y')})")
    print(f"  Parameters: {component.get('parameters', {})}")
    print()
```

### Altium PCB Parsing

The Altium PCB parser extracts the following information from Altium PCB files:

- **Components**: Designators, comments, footprints, etc.
- **Tracks**: Copper connections between pads
- **Vias**: Through-hole connections between layers
- **Pads**: Component connection points
- **Polygons**: Copper pours and ground planes
- **Text and Drawings**: Annotations and graphical elements
- **Board Outline**: The physical boundaries of the PCB

#### Example: Extracting Component Information

```python
from twinizer.hardware.altium.pcb_parser import AltiumPCBParser

# Parse PCB
parser = AltiumPCBParser("board.PcbDoc")
pcb_data = parser.parse()

# Get components
components = pcb_data.get("components", [])
print(f"Found {len(components)} components")

# Print component details
for component in components[:10]:  # Show first 10 components
    print(f"Designator: {component.get('designator')}")
    print(f"  Comment: {component.get('comment')}")
    print(f"  Layer: {component.get('layer')}")
    print(f"  Position: ({component.get('position', {}).get('x')}, {component.get('position', {}).get('y')})")
    print(f"  Rotation: {component.get('rotation')}")
    print(f"  Pads: {len(component.get('pads', []))}")
    print()
```

### Altium BOM Generation

The BOM generator creates a bill of materials from an Altium project file, with the following information:

- **Designator**: Component designator
- **Comment**: Component comment
- **Footprint**: Component footprint
- **Library**: Component library
- **Quantity**: Number of components with the same comment and footprint
- **Supplier**: Component supplier (if available)
- **Supplier Part Number**: Supplier's part number (if available)
- **Manufacturer**: Component manufacturer (if available)
- **Manufacturer Part Number**: Manufacturer's part number (if available)
- **Description**: Component description (if available)

#### Example: Generating a BOM

```python
from twinizer.hardware.altium.project_parser import AltiumProjectParser
from twinizer.hardware.altium.converters import generate_bom

# Parse project
parser = AltiumProjectParser("project.PrjPcb")
project_data = parser.parse()

# Generate BOM in CSV format
bom_csv = generate_bom(
    project_data,
    format="csv"
)

# Save to file
with open("bom.csv", "w") as f:
    f.write(bom_csv)
```

## Advanced Usage

### Combining KiCad and Altium Analysis

```python
from twinizer.hardware.kicad.sch_parser import SchematicParser as KiCadSchematicParser
from twinizer.hardware.altium.sch_parser import AltiumSchematicParser
from twinizer.hardware.kicad.converters import generate_bom as kicad_generate_bom
from twinizer.hardware.altium.converters import generate_bom as altium_generate_bom

def compare_designs(kicad_sch_path, altium_sch_path, output_dir="comparison"):
    """Compare KiCad and Altium designs."""
    import os
    import json
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Parse KiCad schematic
    kicad_parser = KiCadSchematicParser(kicad_sch_path)
    kicad_data = kicad_parser.parse()
    
    # Parse Altium schematic
    altium_parser = AltiumSchematicParser(altium_sch_path)
    altium_data = altium_parser.parse()
    
    # Generate BOMs
    kicad_bom = kicad_generate_bom(kicad_data, format="json")
    altium_bom = altium_generate_bom(altium_data, format="json")
    
    # Save BOMs
    with open(os.path.join(output_dir, "kicad_bom.json"), "w") as f:
        f.write(kicad_bom)
    
    with open(os.path.join(output_dir, "altium_bom.json"), "w") as f:
        f.write(altium_bom)
    
    # Compare component counts
    kicad_components = kicad_data.get("components", [])
    altium_components = altium_data.get("components", [])
    
    comparison = {
        "kicad_component_count": len(kicad_components),
        "altium_component_count": len(altium_components),
        "kicad_unique_values": len(set(c.get("value") for c in kicad_components)),
        "altium_unique_values": len(set(c.get("comment") for c in altium_components)),
    }
    
    # Save comparison
    with open(os.path.join(output_dir, "comparison.json"), "w") as f:
        json.dump(comparison, f, indent=2)
    
    return comparison

# Usage
comparison = compare_designs("kicad_design.sch", "altium_design.SchDoc", "design_comparison")
print(f"Comparison results: {comparison}")
```

### Design Analysis Pipeline

```python
from twinizer.hardware.kicad.sch_parser import SchematicParser
from twinizer.hardware.kicad.pcb_parser import PCBParser
from twinizer.hardware.kicad.converters import (
    schematic_to_mermaid, pcb_to_mermaid, generate_bom
)
import os
import json

def analyze_kicad_design(sch_path, pcb_path, output_dir="analysis"):
    """Complete KiCad design analysis pipeline."""
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Parse schematic
    sch_parser = SchematicParser(sch_path)
    schematic_data = sch_parser.parse()
    
    # Parse PCB
    pcb_parser = PCBParser(pcb_path)
    pcb_data = pcb_parser.parse()
    
    # Generate BOM
    bom_csv = generate_bom(schematic_data, format="csv")
    with open(os.path.join(output_dir, "bom.csv"), "w") as f:
        f.write(bom_csv)
    
    # Generate Mermaid diagrams
    sch_flowchart = schematic_to_mermaid(
        schematic_data,
        diagram_type="flowchart",
        direction="TB"
    )
    with open(os.path.join(output_dir, "schematic_flowchart.mmd"), "w") as f:
        f.write(sch_flowchart)
    
    sch_class = schematic_to_mermaid(
        schematic_data,
        diagram_type="class"
    )
    with open(os.path.join(output_dir, "schematic_class.mmd"), "w") as f:
        f.write(sch_class)
    
    pcb_diagram = pcb_to_mermaid(pcb_data)
    with open(os.path.join(output_dir, "pcb_diagram.mmd"), "w") as f:
        f.write(pcb_diagram)
    
    # Extract component statistics
    components = schematic_data.get("components", [])
    component_types = {}
    for component in components:
        value = component.get("value")
        if value not in component_types:
            component_types[value] = 0
        component_types[value] += 1
    
    # Save component statistics
    with open(os.path.join(output_dir, "component_stats.json"), "w") as f:
        json.dump(component_types, f, indent=2)
    
    # Extract net statistics
    nets = schematic_data.get("nets", [])
    net_stats = {
        "total_nets": len(nets),
        "nets_by_connection_count": {},
    }
    
    for net in nets:
        conn_count = len(net.get("connections", []))
        if conn_count not in net_stats["nets_by_connection_count"]:
            net_stats["nets_by_connection_count"][conn_count] = 0
        net_stats["nets_by_connection_count"][conn_count] += 1
    
    # Save net statistics
    with open(os.path.join(output_dir, "net_stats.json"), "w") as f:
        json.dump(net_stats, f, indent=2)
    
    # Create summary report
    summary = {
        "schematic": {
            "components": len(components),
            "nets": len(nets),
            "unique_component_values": len(component_types),
        },
        "pcb": {
            "modules": len(pcb_data.get("modules", [])),
            "tracks": len(pcb_data.get("tracks", [])),
            "zones": len(pcb_data.get("zones", [])),
            "vias": len(pcb_data.get("vias", [])),
        },
        "output_files": {
            "bom": os.path.join(output_dir, "bom.csv"),
            "schematic_flowchart": os.path.join(output_dir, "schematic_flowchart.mmd"),
            "schematic_class": os.path.join(output_dir, "schematic_class.mmd"),
            "pcb_diagram": os.path.join(output_dir, "pcb_diagram.mmd"),
            "component_stats": os.path.join(output_dir, "component_stats.json"),
            "net_stats": os.path.join(output_dir, "net_stats.json"),
        }
    }
    
    # Save summary
    with open(os.path.join(output_dir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    
    return summary

# Usage
summary = analyze_kicad_design("design.sch", "design.kicad_pcb", "design_analysis")
print(f"Analysis complete! Summary: {summary}")
```

## API Reference

### KiCad Schematic Parser

```python
class SchematicParser:
    """Parse KiCad schematic files."""
    
    def __init__(self, sch_path):
        """
        Initialize the parser.
        
        Parameters:
        -----------
        sch_path : str
            Path to the KiCad schematic file.
        """
        pass
    
    def parse(self):
        """
        Parse the schematic file.
        
        Returns:
        --------
        dict
            Parsed schematic data containing components, nets, and other information.
        """
        pass
```

### KiCad PCB Parser

```python
class PCBParser:
    """Parse KiCad PCB files."""
    
    def __init__(self, pcb_path):
        """
        Initialize the parser.
        
        Parameters:
        -----------
        pcb_path : str
            Path to the KiCad PCB file.
        """
        pass
    
    def parse(self):
        """
        Parse the PCB file.
        
        Returns:
        --------
        dict
            Parsed PCB data containing modules, tracks, zones, and other information.
        """
        pass
```

### KiCad Converters

```python
def schematic_to_mermaid(schematic_data, diagram_type="flowchart", direction="TB"):
    """
    Convert schematic data to a Mermaid diagram.
    
    Parameters:
    -----------
    schematic_data : dict
        Parsed schematic data from SchematicParser.
    diagram_type : str, optional
        Type of diagram to generate. Can be "flowchart", "class", or "entity".
        Default is "flowchart".
    direction : str, optional
        Direction for flowchart. Can be "TB", "BT", "LR", or "RL".
        Default is "TB".
        
    Returns:
    --------
    str
        Mermaid diagram as a string.
    """
    pass

def pcb_to_mermaid(pcb_data, diagram_type="flowchart", direction="TB"):
    """
    Convert PCB data to a Mermaid diagram.
    
    Parameters:
    -----------
    pcb_data : dict
        Parsed PCB data from PCBParser.
    diagram_type : str, optional
        Type of diagram to generate. Can be "flowchart", "class", or "entity".
        Default is "flowchart".
    direction : str, optional
        Direction for flowchart. Can be "TB", "BT", "LR", or "RL".
        Default is "TB".
        
    Returns:
    --------
    str
        Mermaid diagram as a string.
    """
    pass

def generate_bom(schematic_data, format="csv", group_by=None, exclude_references=None,
                include_fields=None, sort_by=None):
    """
    Generate a bill of materials from schematic data.
    
    Parameters:
    -----------
    schematic_data : dict
        Parsed schematic data from SchematicParser.
    format : str, optional
        Output format. Can be "csv", "json", or "xml". Default is "csv".
    group_by : list, optional
        Fields to group components by. Default is ["value", "footprint"].
    exclude_references : list, optional
        Regular expressions for references to exclude. Default is None.
    include_fields : list, optional
        Fields to include in the BOM. Default is None (include all).
    sort_by : str, optional
        Field to sort by. Default is None.
        
    Returns:
    --------
    str
        BOM in the specified format.
    """
    pass
```

### Altium Schematic Parser

```python
class AltiumSchematicParser:
    """Parse Altium schematic files."""
    
    def __init__(self, sch_path):
        """
        Initialize the parser.
        
        Parameters:
        -----------
        sch_path : str
            Path to the Altium schematic file.
        """
        pass
    
    def parse(self):
        """
        Parse the schematic file.
        
        Returns:
        --------
        dict
            Parsed schematic data containing components, nets, and other information.
        """
        pass
```

### Altium PCB Parser

```python
class AltiumPCBParser:
    """Parse Altium PCB files."""
    
    def __init__(self, pcb_path):
        """
        Initialize the parser.
        
        Parameters:
        -----------
        pcb_path : str
            Path to the Altium PCB file.
        """
        pass
    
    def parse(self):
        """
        Parse the PCB file.
        
        Returns:
        --------
        dict
            Parsed PCB data containing components, tracks, vias, and other information.
        """
        pass
```
