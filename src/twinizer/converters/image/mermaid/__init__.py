"""
Mermaid diagram generation and conversion package.

This package provides comprehensive functionality for generating Mermaid diagrams
and converting them to various formats (HTML, PNG, etc.).
"""

__version__ = "0.1.51"

# Import from base module
from .base import BaseDiagramGenerator

# Import constants
from .constants import (
    COLOR_SCHEMES,
    EDGE_STYLES,
    ER_CARDINALITIES,
    NODE_SHAPES,
    SEQUENCE_ARROWS,
    STATE_STYLES,
    THEMES,
)

# Import converters
from .converters import (
    batch_convert_to_png,
    create_html_page,
    from_json,
    install_mmdc,
    save_html,
    to_html,
    to_json,
    to_png,
)

# Import diagram generators
from .diagrams import (
    ClassDiagramGenerator,
    ERDiagramGenerator,
    FlowchartGenerator,
    GanttChartGenerator,
    JourneyDiagramGenerator,
    PieChartGenerator,
    SequenceDiagramGenerator,
    StateDiagramGenerator,
    generate_class_diagram,
    generate_er_diagram,
    generate_flowchart,
    generate_gantt_chart,
    generate_journey_diagram,
    generate_pie_chart,
    generate_sequence_diagram,
    generate_state_diagram,
)

# Import utility functions
from .utils import add_theme_directive, escape_text, format_style_string, sanitize_id


# Create a class that provides access to all diagram types
class MermaidDiagramGenerator:
    """
    Unified generator for all types of Mermaid diagrams.

    This class provides access to all diagram generators through a unified interface.
    """

    def __init__(self, theme: str = "default"):
        """
        Initialize the Mermaid diagram generator.

        Args:
            theme: Theme name for the diagrams ('default', 'dark', 'forest', 'neutral')
        """
        self.theme = theme

        # Initialize generators for each diagram type
        self.flowchart = FlowchartGenerator(theme)
        self.class_diagram = ClassDiagramGenerator(theme)
        self.sequence = SequenceDiagramGenerator(theme)
        self.er = ERDiagramGenerator(theme)
        self.gantt = GanttChartGenerator(theme)
        self.pie = PieChartGenerator(theme)
        self.state = StateDiagramGenerator(theme)
        self.journey = JourneyDiagramGenerator(theme)

    def from_json(self, json_data, diagram_type="auto"):
        """Generate a diagram from JSON data."""
        return from_json(json_data, diagram_type, self.theme)

    def to_html(self, mermaid_code, inline_style=False):
        """Convert a diagram to HTML."""
        return to_html(mermaid_code, inline_style)

    def to_png(
        self,
        mermaid_code,
        output_path,
        width=800,
        height=None,
        background_color="#ffffff",
    ):
        """Convert a diagram to PNG."""
        return to_png(
            mermaid_code, output_path, width, height, background_color, self.theme
        )


# Define the public API
__all__ = [
    # Main classes
    "MermaidDiagramGenerator",
    "BaseDiagramGenerator",
    # Generator classes
    "FlowchartGenerator",
    "ClassDiagramGenerator",
    "SequenceDiagramGenerator",
    "ERDiagramGenerator",
    "GanttChartGenerator",
    "PieChartGenerator",
    "StateDiagramGenerator",
    "JourneyDiagramGenerator",
    # Generator functions
    "generate_flowchart",
    "generate_class_diagram",
    "generate_sequence_diagram",
    "generate_er_diagram",
    "generate_gantt_chart",
    "generate_pie_chart",
    "generate_state_diagram",
    "generate_journey_diagram",
    # Converter functions
    "from_json",
    "to_json",
    "to_html",
    "save_html",
    "create_html_page",
    "to_png",
    "batch_convert_to_png",
    # Utility functions
    "sanitize_id",
    "format_style_string",
    "escape_text",
    "add_theme_directive",
    "install_mmdc",
    # Constants
    "NODE_SHAPES",
    "EDGE_STYLES",
    "SEQUENCE_ARROWS",
    "COLOR_SCHEMES",
    "THEMES",
    "ER_CARDINALITIES",
    "STATE_STYLES",
]
