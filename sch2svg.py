import re
import os
import schemdraw
from schemdraw import elements as elm


def parse_kicad_sch(file_path):
    """Parse KiCad schematic file and extract component information."""
    components = []
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regular expressions to extract component details
    component_pattern = r'\$Comp\n(.*?)\$EndComp'
    name_pattern = r'L ([\w-]+) (\w+)\n'
    pos_pattern = r'P ([\d-]+) ([\d-]+)'

    # Find all components
    for comp_match in re.finditer(component_pattern, content, re.DOTALL):
        comp_text = comp_match.group(1)

        # Extract component name and reference
        name_match = re.search(name_pattern, comp_text)
        if name_match:
            comp_type = name_match.group(1)
            ref = name_match.group(2)

            # Extract position
            pos_match = re.search(pos_pattern, comp_text)
            pos_x = int(pos_match.group(1)) if pos_match else 0
            pos_y = int(pos_match.group(2)) if pos_match else 0

            components.append({
                'type': comp_type,
                'ref': ref,
                'x': pos_x,
                'y': pos_y
            })

    return components


def create_svg_from_components(components, output_path):
    """Create SVG from parsed components."""
    d = schemdraw.Drawing()

    # Map of KiCad component types to schemdraw elements
    component_map = {
        'CONN_2': elm.Connector2,
        'CONN_3': elm.Connector3,
        'CONN_5X2': elm.MultiConnector,
        'Board': elm.Box,
        '+24V': elm.Source,
        # Add more mappings as needed
    }

    # Normalize coordinates
    min_x = min(c['x'] for c in components) if components else 0
    min_y = min(c['y'] for c in components) if components else 0

    for comp in components:
        # Select appropriate element type
        element_type = component_map.get(comp['type'], elm.Element)

        # Adjust position (you might need to scale coordinates)
        x = (comp['x'] - min_x) / 1000  # Scale down
        y = (comp['y'] - min_y) / 1000  # Scale down

        # Add element to drawing
        with d.at((x, y)):
            elem = element_type().label(comp['ref'])
            d.add(elem)

    # Save as SVG
    d.save(output_path)
    print(f"SVG saved to {output_path}")


def main(input_sch_path, output_svg_path):
    """Main function to convert .sch to .svg"""
    # Parse the schematic
    components = parse_kicad_sch(input_sch_path)

    # Create SVG
    create_svg_from_components(components, output_svg_path)


# Example usage
if __name__ == '__main__':
    input_file = 'mtc.sch'  # Replace with your .sch file
    output_file = 'mtc_schematic.svg'
    main(input_file, output_file)

# Note: This is a basic converter and may require adjustments
# Requires libraries:
# pip install schemdraw
# Limitations:
# - Not all KiCad components are mapped
# - Complex schematics might need manual refinement
# - Coordinate system might need calibration