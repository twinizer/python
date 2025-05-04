#!/usr/bin/env python3
"""
KiCad Schematic to SVG Converter

This script converts KiCad schematic files to SVG format using schemdraw.
It can also generate HTML files with embedded SVGs for easy viewing.
"""

import os
import sys
import argparse
from typing import Optional, Tuple, List, Dict, Any, Union

try:
    import schemdraw
    from schemdraw import elements as elm
    SCHEMDRAW_AVAILABLE = True
except ImportError:
    SCHEMDRAW_AVAILABLE = False

try:
    from rich.console import Console
    console = Console()
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    console = None

# Try to import from Twinizer if available
try:
    from twinizer.hardware.kicad.sch_parser import SchematicParser
    from twinizer.hardware.kicad.converters import SchematicToSVG, convert_kicad_to_svg
    TWINIZER_AVAILABLE = True
except ImportError:
    TWINIZER_AVAILABLE = False


def print_message(message: str, style: str = None):
    """Print a message with style if rich is available, otherwise print normally."""
    if RICH_AVAILABLE and console:
        console.print(message, style=style)
    else:
        print(message)


def parse_schematic(schematic_path: str) -> Dict:
    """
    Parse a KiCad schematic file and extract components and nets.
    
    Args:
        schematic_path: Path to the KiCad schematic file
        
    Returns:
        Dictionary with components and nets
    """
    if TWINIZER_AVAILABLE:
        parser = SchematicParser(schematic_path)
        parser.parse()
        return {
            'components': parser.components,
            'nets': parser.nets
        }
    else:
        # Fallback implementation if Twinizer is not available
        components = []
        nets = []
        
        try:
            with open(schematic_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract components
            import re
            
            # Find component sections
            comp_sections = re.findall(r'\(symbol \(lib_id "[^"]+"\).+?\n  \)', content, re.DOTALL)
            
            for section in comp_sections:
                # Extract component properties
                lib_id_match = re.search(r'\(lib_id "([^"]+)"\)', section)
                ref_match = re.search(r'\(property "Reference" "([^"]+)"\)', section)
                value_match = re.search(r'\(property "Value" "([^"]+)"\)', section)
                at_match = re.search(r'\(at ([0-9.-]+) ([0-9.-]+)', section)
                
                if lib_id_match and ref_match and at_match:
                    lib_id = lib_id_match.group(1)
                    reference = ref_match.group(1)
                    value = value_match.group(1) if value_match else ""
                    x = float(at_match.group(1))
                    y = float(at_match.group(2))
                    
                    components.append({
                        'lib_id': lib_id,
                        'reference': reference,
                        'value': value,
                        'x': x,
                        'y': y
                    })
            
            # Extract nets (connections)
            wire_sections = re.findall(r'\(wire.+?\n  \)', content, re.DOTALL)
            
            # Create a mapping of positions to component references
            pos_to_ref = {}
            for comp in components:
                pos_to_ref[(comp['x'], comp['y'])] = comp['reference']
            
            # Process wires to create nets
            for i, section in enumerate(wire_sections):
                pts_match = re.search(r'\(pts \(xy ([0-9.-]+) ([0-9.-]+)\) \(xy ([0-9.-]+) ([0-9.-]+)\)\)', section)
                if pts_match:
                    x1, y1 = float(pts_match.group(1)), float(pts_match.group(2))
                    x2, y2 = float(pts_match.group(3)), float(pts_match.group(4))
                    
                    # Find components connected by this wire
                    connections = []
                    for (x, y), ref in pos_to_ref.items():
                        # Simple proximity check (not perfect but works for basic cases)
                        if ((abs(x - x1) < 10 and abs(y - y1) < 10) or 
                            (abs(x - x2) < 10 and abs(y - y2) < 10)):
                            connections.append(ref)
                    
                    if len(connections) >= 2:
                        nets.append({
                            'name': f"Net_{i}",
                            'connections': connections
                        })
            
            return {
                'components': components,
                'nets': nets
            }
        except Exception as e:
            print_message(f"Error parsing schematic: {e}", style="red")
            return {'components': [], 'nets': []}


def create_svg_from_components(components: List[Dict], nets: List[Dict], 
                              output_path: str, theme: str = 'default') -> str:
    """
    Create an SVG diagram from components and nets.
    
    Args:
        components: List of component dictionaries
        nets: List of net dictionaries
        output_path: Path to save the SVG file
        theme: Theme to use for the SVG output
        
    Returns:
        Path to the output SVG file
    """
    if not SCHEMDRAW_AVAILABLE:
        print_message("Error: schemdraw package is not installed. Please install it with:", style="red")
        print_message("pip install schemdraw", style="yellow")
        return ""
    
    # Set theme
    if theme == 'dark':
        schemdraw.theme('dark')
    elif theme == 'blue':
        schemdraw.theme(bgcolor='aliceblue', fgcolor='black')
    elif theme == 'minimal':
        schemdraw.theme(bgcolor='white', fgcolor='black', 
                       color='black', lw=1, fontsize=10)
    else:  # default
        schemdraw.theme('default')
    
    # Create the drawing
    d = schemdraw.Drawing()
    
    # Component type to schemdraw element mapping
    component_map = {
        # Connectors
        'CONN_2': elm.Connector(num=2),
        'CONN_3': elm.Connector(num=3),
        'CONN_4': elm.Connector(num=4),
        'CONN_5X2': elm.Connector(num=10, cols=2),
        'Conn_01x02': elm.Connector(num=2),
        'Conn_01x03': elm.Connector(num=3),
        'Conn_01x04': elm.Connector(num=4),
        'Conn_02x05': elm.Connector(num=10, cols=2),
        
        # Basic components
        'R': elm.Resistor,
        'C': elm.Capacitor,
        'CP': elm.Capacitor(polar=True),
        'L': elm.Inductor,
        'D': elm.Diode,
        'LED': elm.LED,
        'Q_NPN': elm.BjtNpn,
        'Q_PNP': elm.BjtPnp,
        'MOSFET_N': elm.NFet,
        'MOSFET_P': elm.PFet,
        
        # Power symbols
        '+24V': elm.SourceV,
        '+12V': elm.SourceV,
        '+5V': elm.SourceV,
        '+3V3': elm.SourceV,
        'GND': elm.Ground,
        'GNDA': elm.Ground,
        'GNDREF': elm.Ground,
        
        # ICs and specialized components
        'Opamp': elm.Opamp,
        'Opamp_Dual': elm.Opamp2,
        'Regulator_Linear': elm.Vdd,
        'Crystal': elm.Crystal,
        'Speaker': elm.Speaker,
        'Microphone': elm.Mic,
        'Transformer': elm.Transformer,
        
        # Default fallbacks for common prefixes
        'U': elm.Ic,
        'IC': elm.Ic,
        'X': elm.Block,
        'SW': elm.Switch,
        'J': elm.Connector,
        'P': elm.Connector,
        'BT': elm.Battery,
        'F': elm.Fuse,
    }
    
    # Normalize coordinates
    if components:
        min_x = min(c.get('x', 0) for c in components if 'x' in c)
        min_y = min(c.get('y', 0) for c in components if 'y' in c)
        max_x = max(c.get('x', 0) for c in components if 'x' in c)
        max_y = max(c.get('y', 0) for c in components if 'y' in c)
    else:
        min_x = min_y = max_x = max_y = 0
    
    # Scale factors - ensure we don't divide by zero
    width = max_x - min_x
    height = max_y - min_y
    
    x_scale = 20 / width if width > 0 else 1
    y_scale = 20 / height if height > 0 else 1
    
    # Use the smaller scale to maintain aspect ratio
    scale = min(x_scale, y_scale)
    
    # Keep track of unique positions to avoid overlapping
    used_positions = set()
    
    # Draw components
    for comp in components:
        # Get component properties
        comp_type = comp.get('lib_id', '').split(':')[-1]
        ref = comp.get('reference', 'UNKNOWN')
        value = comp.get('value', '')
        x = comp.get('x', 0)
        y = comp.get('y', 0)
        
        prefix = ref[0] if ref and len(ref) > 0 else ''
        
        # Try to get element type from the map
        element_type = None
        
        # First try exact match
        if comp_type in component_map:
            element_type = component_map[comp_type]
        # Then try prefix match for reference
        elif prefix in component_map:
            element_type = component_map[prefix]
        # Default to a block
        else:
            element_type = elm.Block
        
        # Get label from reference and value
        label = f"{ref}"
        if value:
            label += f"\n{value}"
        
        # Adjust position
        x_pos = (x - min_x) * scale
        y_pos = (y - min_y) * scale
        
        # Ensure unique position
        base_pos = (x_pos, y_pos)
        pos = base_pos
        offset = 0
        while pos in used_positions:
            offset += 0.5
            pos = (x_pos + offset, y_pos + offset)
        used_positions.add(pos)
        
        # Add element to drawing
        try:
            if callable(element_type):
                d += element_type().at(pos).label(label)
            else:
                # For pre-configured elements like Connector
                d += element_type.at(pos).label(label)
        except Exception as e:
            print_message(f"Warning: Error adding component {ref}: {e}", style="yellow")
            # Fallback to block if specific element fails
            d += elm.Block().at(pos).label(label)
    
    # Draw connections
    for net in nets:
        connections = net.get('connections', [])
        if len(connections) >= 2:
            for i in range(len(connections) - 1):
                # Find component positions for the connection endpoints
                start_comp = next((c for c in components if c.get('reference') == connections[i]), None)
                end_comp = next((c for c in components if c.get('reference') == connections[i+1]), None)
                
                if start_comp and end_comp:
                    start_x = (start_comp.get('x', 0) - min_x) * scale
                    start_y = (start_comp.get('y', 0) - min_y) * scale
                    end_x = (end_comp.get('x', 0) - min_x) * scale
                    end_y = (end_comp.get('y', 0) - min_y) * scale
                    
                    try:
                        d += elm.Line().at((start_x, start_y)).to((end_x, end_y))
                    except Exception as e:
                        print_message(f"Warning: Error drawing connection: {e}", style="yellow")
    
    # Save as SVG
    d.save(output_path)
    print_message(f"SVG saved to: {output_path}", style="green")
    
    return output_path


def generate_html(svg_path: str, schematic_path: str) -> str:
    """
    Generate an HTML file with the SVG embedded.
    
    Args:
        svg_path: Path to the SVG file
        schematic_path: Path to the original schematic file
        
    Returns:
        Path to the HTML file
    """
    html_path = f"{os.path.splitext(svg_path)[0]}.html"
    
    try:
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(f"""<!DOCTYPE html>
<html>
<head>
    <title>KiCad Schematic: {os.path.basename(schematic_path)}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .svg-container {{ 
            border: 1px solid #ddd; 
            padding: 10px; 
            margin-bottom: 20px;
            background-color: white;
        }}
        svg {{ max-width: 100%; height: auto; }}
    </style>
</head>
<body>
    <h1>KiCad Schematic: {os.path.basename(schematic_path)}</h1>
    <div class="svg-container">
""")
            
            # Embed the SVG
            try:
                with open(svg_path, "r", encoding="utf-8") as svg_f:
                    svg_content = svg_f.read()
                f.write(f'        {svg_content}\n')
            except Exception as e:
                f.write(f'        <p>Error embedding SVG: {e}</p>\n')
            
            f.write("""    </div>
</body>
</html>""")
        
        print_message(f"HTML file generated: {html_path}", style="green")
        return html_path
    except Exception as e:
        print_message(f"Error generating HTML: {e}", style="red")
        return ""


def main():
    """Main function to handle command-line arguments and run the conversion."""
    parser = argparse.ArgumentParser(description='Convert KiCad schematic to SVG')
    parser.add_argument('schematic_file', help='Path to KiCad schematic file')
    parser.add_argument('--output', '-o', help='Output SVG file path')
    parser.add_argument('--theme', '-t', choices=['default', 'dark', 'blue', 'minimal'], 
                        default='default', help='Theme for the SVG output')
    parser.add_argument('--html', '-h', action='store_true', help='Generate HTML file with embedded SVG')
    
    args = parser.parse_args()
    
    # Check if schemdraw is installed
    if not SCHEMDRAW_AVAILABLE:
        print_message("Error: schemdraw package is not installed. Please install it with:", style="red")
        print_message("pip install schemdraw", style="yellow")
        sys.exit(1)
    
    # Prepare output path
    if args.output is None:
        base_path = os.path.splitext(args.schematic_file)[0]
        output_path = f"{base_path}.svg"
    else:
        output_path = args.output
    
    try:
        # Use Twinizer if available
        if TWINIZER_AVAILABLE:
            result = convert_kicad_to_svg(args.schematic_file, output_path, args.theme, args.html)
            
            if args.html:
                svg_path, html_path = result
                print_message(f"SVG file created: {svg_path}", style="green")
                print_message(f"HTML file created: {html_path}", style="green")
            else:
                print_message(f"SVG file created: {result}", style="green")
        else:
            # Fallback to built-in implementation
            data = parse_schematic(args.schematic_file)
            svg_path = create_svg_from_components(data['components'], data['nets'], output_path, args.theme)
            
            if args.html and svg_path:
                html_path = generate_html(svg_path, args.schematic_file)
                if html_path:
                    print_message(f"HTML file created: {html_path}", style="green")
    
    except Exception as e:
        print_message(f"Error during conversion: {e}", style="red")
        sys.exit(1)


if __name__ == "__main__":
    main()
