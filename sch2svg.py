import re
import os
import sys
import schemdraw
from schemdraw import elements as elm
from pathlib import Path
from rich.console import Console

console = Console()


def parse_kicad_sch(file_path):
    """Parse KiCad schematic file and extract component and net information."""
    components = []
    nets = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        console.print(f"[red]Error reading file {file_path}:[/red] {e}")
        return components, nets

    # Regular expressions to extract component details
    component_pattern = r'\$Comp\n(.*?)\$EndComp'
    name_pattern = r'L ([\w-]+) (\w+)\n'
    value_pattern = r'F 0 "([^"]*)"'
    pos_pattern = r'P ([\d-]+) ([\d-]+)'

    # Regular expressions to extract nets (wires)
    wire_pattern = r'Wire Wire Line\n([\d-]+) ([\d-]+) ([\d-]+) ([\d-]+)'
    
    # Regular expressions to extract labels
    label_pattern = r'Text Label ([\d-]+) ([\d-]+).*\n(.*?)\n'

    # Find all components
    for comp_match in re.finditer(component_pattern, content, re.DOTALL):
        comp_text = comp_match.group(1)
        try:
            name_match = re.search(name_pattern, comp_text)
            value_match = re.search(value_pattern, comp_text)
            pos_match = re.search(pos_pattern, comp_text)
            
            if name_match and pos_match:
                components.append({
                    'type': name_match.group(1),
                    'ref': name_match.group(2),
                    'value': value_match.group(1) if value_match else '',
                    'x': int(pos_match.group(1)),
                    'y': int(pos_match.group(2))
                })
        except Exception as e:
            console.print(f"[yellow]Warning: Error processing component:[/yellow] {e}")

    # Extract nets
    for wire_match in re.finditer(wire_pattern, content):
        try:
            x1, y1, x2, y2 = map(int, wire_match.groups())
            nets.append({'start': (x1, y1), 'end': (x2, y2)})
        except Exception as e:
            console.print(f"[yellow]Warning: Error processing wire:[/yellow] {e}")
    
    # Extract labels
    labels = []
    for label_match in re.finditer(label_pattern, content):
        try:
            x, y, text = label_match.groups()
            labels.append({
                'x': int(x),
                'y': int(y),
                'text': text.strip()
            })
        except Exception as e:
            console.print(f"[yellow]Warning: Error processing label:[/yellow] {e}")

    console.print(f"[green]Extracted:[/green] {len(components)} components, {len(nets)} nets, {len(labels)} labels")
    return components, nets, labels


def create_svg_from_components(components, nets, labels, output_path, theme='default'):
    """Create SVG from parsed components and nets with optional theme."""
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
    
    d = schemdraw.Drawing()

    # Expanded map of KiCad component types to schemdraw elements
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
        min_x = min(c['x'] for c in components)
        min_y = min(c['y'] for c in components)
        max_x = max(c['x'] for c in components)
        max_y = max(c['y'] for c in components)
        
        # Also consider nets and labels
        if nets:
            min_x = min(min_x, min(min(n['start'][0], n['end'][0]) for n in nets))
            min_y = min(min_y, min(min(n['start'][1], n['end'][1]) for n in nets))
            max_x = max(max_x, max(max(n['start'][0], n['end'][0]) for n in nets))
            max_y = max(max_y, max(max(n['start'][1], n['end'][1]) for n in nets))
        
        if labels:
            min_x = min(min_x, min(l['x'] for l in labels))
            min_y = min(min_y, min(l['y'] for l in labels))
            max_x = max(max_x, max(l['x'] for l in labels))
            max_y = max(max_y, max(l['y'] for l in labels))
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
        # Determine the element type based on component type or reference
        comp_type = comp['type']
        ref = comp['ref']
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
        if comp.get('value'):
            label += f"\n{comp['value']}"

        # Adjust position
        x = (comp['x'] - min_x) * scale
        y = (comp['y'] - min_y) * scale

        # Ensure unique position
        base_pos = (x, y)
        pos = base_pos
        offset = 0
        while pos in used_positions:
            offset += 0.5
            pos = (x + offset, y + offset)
        used_positions.add(pos)

        # Add element to drawing
        try:
            if callable(element_type):
                d += element_type().at(pos).label(label)
            else:
                # For pre-configured elements like Connector
                d += element_type.at(pos).label(label)
        except Exception as e:
            console.print(f"[yellow]Warning: Error adding component {ref}:[/yellow] {e}")
            # Fallback to block if specific element fails
            d += elm.Block().at(pos).label(label)

    # Draw nets (connections)
    for net in nets:
        start_x = (net['start'][0] - min_x) * scale
        start_y = (net['start'][1] - min_y) * scale
        end_x = (net['end'][0] - min_x) * scale
        end_y = (net['end'][1] - min_y) * scale
        
        start = (start_x, start_y)
        end = (end_x, end_y)
        
        try:
            d += elm.Line().at(start).to(end)
        except Exception as e:
            console.print(f"[yellow]Warning: Error drawing net:[/yellow] {e}")

    # Add labels
    for label in labels:
        x = (label['x'] - min_x) * scale
        y = (label['y'] - min_y) * scale
        
        try:
            d += elm.Label().at((x, y)).label(label['text'])
        except Exception as e:
            console.print(f"[yellow]Warning: Error adding label:[/yellow] {e}")

    # Save as SVG
    d.save(output_path)
    console.print(f"[green]SVG saved to:[/green] {output_path}")
    return output_path


def process_folder(input_folder, output_folder=None, theme='default'):
    """Process all .sch files in a folder and generate SVGs."""
    input_folder = Path(input_folder).resolve()
    if not input_folder.is_dir():
        console.print(f"[red]Error: {input_folder} is not a valid directory.[/red]")
        return []

    # If no output folder provided, use input folder
    if output_folder is None:
        output_folder = input_folder
    else:
        output_folder = Path(output_folder).resolve()
        os.makedirs(output_folder, exist_ok=True)

    # Find all .sch files in the folder (non-recursive)
    sch_files = list(input_folder.glob("*.sch"))
    if not sch_files:
        console.print(f"[yellow]No .sch files found in {input_folder}.[/yellow]")
        return []

    # Generate SVGs for each .sch file
    svg_files = []
    for sch_file in sch_files:
        output_svg_path = output_folder / sch_file.with_suffix(".svg").name
        console.print(f"[blue]Processing[/blue] {sch_file} -> {output_svg_path}")
        components, nets, labels = parse_kicad_sch(sch_file)
        svg_path = create_svg_from_components(components, nets, labels, output_svg_path, theme)
        svg_files.append(svg_path)

    return svg_files


def generate_html(svg_files, output_html_path):
    """Generate an HTML file embedding all SVG files."""
    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <title>KiCad Schematics to SVG</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        h2 { color: #666; margin-top: 30px; }
        .svg-container { 
            border: 1px solid #ddd; 
            padding: 10px; 
            margin-bottom: 20px;
            background-color: white;
        }
        svg { max-width: 100%; height: auto; }
    </style>
</head>
<body>
    <h1>KiCad Schematics Converted to SVG</h1>
""")

        for svg_file in svg_files:
            rel_path = os.path.basename(svg_file)
            f.write(f'    <h2>{rel_path}</h2>\n')
            f.write('    <div class="svg-container">\n')
            try:
                with open(svg_file, "r", encoding="utf-8") as svg_f:
                    svg_content = svg_f.read()
                f.write(f'        {svg_content}\n')
            except Exception as e:
                f.write(f'        <p>Error embedding {rel_path}: {e}</p>\n')
            f.write('    </div>\n')

        f.write("</body>\n</html>")
    console.print(f"[green]HTML file generated:[/green] {output_html_path}")
    return output_html_path


def convert_schematic_to_svg(schematic_path, output_path=None, theme='default', generate_html_output=False):
    """Convert a KiCad schematic to SVG format."""
    schematic_path = Path(schematic_path).resolve()
    
    if not schematic_path.exists():
        console.print(f"[red]Error: Schematic file {schematic_path} does not exist.[/red]")
        return None
    
    if not output_path:
        output_path = schematic_path.with_suffix(".svg")
    else:
        output_path = Path(output_path).resolve()
    
    # Parse and convert
    components, nets, labels = parse_kicad_sch(schematic_path)
    svg_path = create_svg_from_components(components, nets, labels, output_path, theme)
    
    # Generate HTML if requested
    if generate_html_output:
        html_path = output_path.with_suffix(".html")
        generate_html([svg_path], html_path)
        return svg_path, html_path
    
    return svg_path


def main(input_path, output_path=None, theme='default', generate_html_output=True):
    """Main function to process .sch files or folders."""
    input_path = Path(input_path).resolve()
    
    if output_path:
        output_path = Path(output_path).resolve()

    if input_path.is_file() and input_path.suffix.lower() == ".sch":
        # Single .sch file
        if not output_path:
            output_path = input_path.with_suffix(".svg")
        
        svg_path = convert_schematic_to_svg(input_path, output_path, theme, False)
        
        if generate_html_output:
            html_path = output_path.with_suffix(".html")
            generate_html([svg_path], html_path)
            console.print(f"[green]Process complete.[/green] SVG: {svg_path}, HTML: {html_path}")
        else:
            console.print(f"[green]Process complete.[/green] SVG: {svg_path}")
            
    elif input_path.is_dir():
        # Folder containing .sch files
        if not output_path:
            output_path = input_path
        
        svg_files = process_folder(input_path, output_path, theme)
        
        if svg_files and generate_html_output:
            html_path = output_path / "kicad_schematics.html"
            generate_html(svg_files, html_path)
            console.print(f"[green]Process complete.[/green] Generated {len(svg_files)} SVG files and HTML index: {html_path}")
        elif svg_files:
            console.print(f"[green]Process complete.[/green] Generated {len(svg_files)} SVG files")
        else:
            console.print("[yellow]No SVG files were generated.[/yellow]")
    else:
        console.print(f"[red]Error: {input_path} is not a valid .sch file or directory.[/red]")


# Command-line usage
if __name__ == '__main__':
    if len(sys.argv) < 2:
        console.print("[yellow]Usage: python sch2svg.py <input_path> [output_path] [--theme theme_name] [--no-html][/yellow]")
        console.print("  input_path: Path to a .sch file or directory containing .sch files")
        console.print("  output_path: Optional path for output SVG/HTML files")
        console.print("  --theme: Optional theme (default, dark, blue, minimal)")
        console.print("  --no-html: Skip HTML generation")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = None
    theme = 'default'
    generate_html_output = True
    
    # Parse arguments
    if len(sys.argv) > 2 and not sys.argv[2].startswith('--'):
        output_path = sys.argv[2]
    
    for arg in sys.argv:
        if arg.startswith('--theme='):
            theme = arg.split('=')[1]
        elif arg == '--no-html':
            generate_html_output = False

    main(input_path, output_path, theme, generate_html_output)
