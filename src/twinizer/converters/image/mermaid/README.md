# Enhanced Mermaid Diagram Generator

This package provides a comprehensive toolkit for creating Mermaid diagrams programmatically with support for all diagram types, advanced styling options, and exporting to various formats.

## Features

- **Multiple Diagram Types**:
  - Flowcharts
  - Class Diagrams
  - Sequence Diagrams
  - Entity-Relationship Diagrams
  - Gantt Charts
  - Pie Charts
  - State Diagrams
  - User Journey Diagrams

- **Theming and Styling**:
  - Built-in theme support (default, dark, forest, neutral)
  - Custom styling for nodes, edges, and other elements
  - Color scheme customization

- **Export Options**:
  - HTML (standalone or inline)
  - PNG (requires Mermaid CLI)
  - JSON representation

- **Utilities**:
  - JSON import/export
  - Diagram validation
  - Helper functions for common operations

## Installation

```bash
pip install enhanced-mermaid
```

## Usage

### Basic Usage

```python
from mermaid import MermaidDiagramGenerator

# Create a generator (you can specify a theme)
generator = MermaidDiagramGenerator(theme='forest')

# Generate a flowchart
nodes = [
    {'id': 'A', 'label': 'Start'},
    {'id': 'B', 'label': 'Process'},
    {'id': 'C', 'label': 'End'},
]
edges = [
    {'from': 'A', 'to': 'B', 'label': 'Next'},
    {'from': 'B', 'to': 'C', 'label': 'Done'},
]

# Generate the diagram
mermaid_code = generator.flowchart.generate(nodes, edges, direction='LR', title='Simple Process')

# Export to HTML
html_code = generator.to_html(mermaid_code)
with open('flowchart.html', 'w') as f:
    f.write(html_code)

# Export to PNG
generator.to_png(mermaid_code, 'flowchart.png', width=800)
```

### Using Convenience Functions

```python
from mermaid import generate_flowchart, to_html, to_png

# Generate a flowchart
nodes = [
    {'id': 'A', 'label': 'Start'},
    {'id': 'B', 'label': 'Process'},
    {'id': 'C', 'label': 'End'},
]
edges = [
    {'from': 'A', 'to': 'B', 'label': 'Next'},
    {'from': 'B', 'to': 'C', 'label': 'Done'},
]

mermaid_code = generate_flowchart(nodes, edges, direction='LR', theme='forest')

# Export to HTML
html_file = save_html(mermaid_code, 'flowchart.html', title='Simple Process')

# Export to PNG
png_file = to_png(mermaid_code, 'flowchart.png', width=800, theme='forest')
```

### Working with JSON Data

```python
from mermaid import from_json

# Define your diagram as JSON
diagram_json = {
    "nodes": [
        {"id": "A", "label": "Start"},
        {"id": "B", "label": "Process"},
        {"id": "C", "label": "End"}
    ],
    "edges": [
        {"from": "A", "to": "B", "label": "Next"},
        {"from": "B", "to": "C", "label": "Done"}
    ],
    "direction": "LR",
    "title": "Simple Process"
}

# Convert JSON to Mermaid diagram
mermaid_code = from_json(diagram_json, diagram_type='flowchart')
```

## Diagram Types

### Flowchart

```python
from mermaid import generate_flowchart

nodes = [
    {'id': 'A', 'label': 'Start', 'shape': 'stadium'},
    {'id': 'B', 'label': 'Process', 'shape': 'rectangle'},
    {'id': 'C', 'label': 'Decision', 'shape': 'diamond'},
    {'id': 'D', 'label': 'End', 'shape': 'stadium'}
]
edges = [
    {'from': 'A', 'to': 'B'},
    {'from': 'B', 'to': 'C'},
    {'from': 'C', 'to': 'D', 'label': 'Yes', 'style': 'solid'},
    {'from': 'C', 'to': 'B', 'label': 'No', 'style': 'dotted'}
]
styles = [
    {'target': 'start', 'style': 'fill:#green,stroke:#black', 'applies_to': ['A', 'D']},
    {'target': 'process', 'style': 'fill:#lightblue,stroke:#black', 'applies_to': ['B']},
    {'target': 'decision', 'style': 'fill:#yellow,stroke:#black', 'applies_to': ['C']}
]

mermaid_code = generate_flowchart(nodes, edges, direction='TD', title='Process Flow', styles=styles)
```

### Class Diagram

```python
from mermaid import generate_class_diagram

classes = [
    {
        'name': 'Animal',
        'attributes': [
            {'name': 'age', 'type': 'int'},
            {'name': 'gender', 'type': 'string'}
        ],
        'methods': [
            {'name': 'eat', 'params': 'food'},
            {'name': 'sleep', 'params': ''}
        ]
    },
    {
        'name': 'Dog',
        'attributes': [
            {'name': 'breed', 'type': 'string'}
        ],
        'methods': [
            {'name': 'bark', 'params': ''}
        ],
        'relationships': [
            {'type': 'inheritance', 'target': 'Animal'}
        ]
    },
    {
        'name': 'Cat',
        'attributes': [
            {'name': 'color', 'type': 'string'}
        ],
        'methods': [
            {'name': 'meow', 'params': ''}
        ],
        'relationships': [
            {'type': 'inheritance', 'target': 'Animal'}
        ]
    }
]

mermaid_code = generate_class_diagram(classes, title='Animal Hierarchy')
```

### Sequence Diagram

```python
from mermaid import generate_sequence_diagram

actors = [
    {'name': 'User', 'type': 'actor'},
    {'name': 'Client', 'type': 'participant'},
    {'name': 'Server', 'type': 'participant'},
    {'name': 'Database', 'type': 'database'}
]

messages = [
    {'from': 'User', 'to': 'Client', 'text': 'Request Data', 'activate': True},
    {'from': 'Client', 'to': 'Server', 'text': 'API Request', 'activate': True},
    {'from': 'Server', 'to': 'Database', 'text': 'Query', 'activate': True},
    {'from': 'Database', 'to': 'Server', 'text': 'Results', 'deactivate': True},
    {'from': 'Server', 'to': 'Client', 'text': 'Response', 'deactivate': True},
    {'from': 'Client', 'to': 'User', 'text': 'Display Data', 'deactivate': True},
    {'from': 'User', 'to': 'User', 'text': 'Process Information', 'note': 'User analyzes the data'}
]

mermaid_code = generate_sequence_diagram(actors, messages, title='Data Request Flow', autonumber=True)
```

## Additional Resources

- [Mermaid Documentation](https://mermaid-js.github.io/mermaid/#/)
- [Mermaid Live Editor](https://mermaid-js.github.io/mermaid-live-editor)
- [Mermaid CLI](https://github.com/mermaid-js/mermaid-cli)

## License

MIT License