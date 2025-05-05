"""
html.py
"""

"""
HTML export for Mermaid diagrams.

This module provides functionality to convert Mermaid diagrams to HTML.
"""

from typing import Dict, Optional


def to_html(
    mermaid_code: str,
    inline_style: bool = False,
    title: str = "Mermaid Diagram",
    theme: Optional[str] = None,
    background_color: str = "#ffffff",
) -> str:
    """
    Convert a Mermaid diagram to HTML.

    Args:
        mermaid_code: Mermaid diagram code
        inline_style: Whether to include the Mermaid library inline
        title: Title for the HTML page
        theme: Theme for the diagram (will override any theme in the diagram)
        background_color: Background color for the diagram

    Returns:
        HTML string with the rendered diagram
    """
    # Clean up the Mermaid code
    mermaid_code = mermaid_code.strip()

    # Create the HTML
    html_parts = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        f"    <title>{title}</title>",
        '    <meta charset="UTF-8">',
        '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
    ]

    # Add CSS
    html_parts.extend(
        [
            "    <style>",
            "        body {",
            '            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;',
            f"            background-color: {background_color};",
            "            margin: 0;",
            "            padding: 20px;",
            "        }",
            "        .container {",
            "            max-width: 1200px;",
            "            margin: 0 auto;",
            "        }",
            "        h1 {",
            "            font-size: 24px;",
            "            margin-bottom: 20px;",
            "        }",
            "        .mermaid {",
            "            display: flex;",
            "            justify-content: center;",
            "            margin: 20px 0;",
            "        }",
            "    </style>",
        ]
    )

    # Add Mermaid library
    if inline_style:
        # Include a minified version of the Mermaid library inline
        # This is just a placeholder - in reality you would include the actual minified library
        html_parts.append("    <script>")
        html_parts.append("        // Mermaid library code would be here")
        html_parts.append("    </script>")
    else:
        # Include from CDN
        html_parts.append(
            '    <script src="https://cdn.jsdelivr.net/npm/mermaid@9/dist/mermaid.min.js"></script>'
        )

    # Add initialization script
    init_options = {}
    if theme:
        init_options["theme"] = theme

    init_options_str = ", ".join([f"{k}: '{v}'" for k, v in init_options.items()])

    html_parts.extend(
        [
            "    <script>",
            '        document.addEventListener("DOMContentLoaded", function() {',
            f"            mermaid.initialize({{ startOnLoad: true, {init_options_str} }});",
            "        });",
            "    </script>",
            "</head>",
            "<body>",
            '    <div class="container">',
            f"        <h1>{title}</h1>",
            '        <div class="mermaid">',
        ]
    )

    # Add the Mermaid code
    html_parts.append(mermaid_code)

    # Close the HTML
    html_parts.extend(
        [
            "        </div>",
            "    </div>",
            "</body>",
            "</html>",
        ]
    )

    return "\n".join(html_parts)


def save_html(
    mermaid_code: str,
    output_path: str,
    inline_style: bool = False,
    title: str = "Mermaid Diagram",
    theme: Optional[str] = None,
    background_color: str = "#ffffff",
) -> str:
    """
    Convert a Mermaid diagram to HTML and save to a file.

    Args:
        mermaid_code: Mermaid diagram code
        output_path: Path to save the HTML file
        inline_style: Whether to include the Mermaid library inline
        title: Title for the HTML page
        theme: Theme for the diagram (will override any theme in the diagram)
        background_color: Background color for the diagram

    Returns:
        Path to the output HTML file
    """
    html = to_html(mermaid_code, inline_style, title, theme, background_color)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return output_path


def create_html_page(
    diagrams: Dict[str, str],
    output_path: str,
    title: str = "Mermaid Diagrams",
    description: str = "",
    theme: Optional[str] = None,
) -> str:
    """
    Create an HTML page with multiple Mermaid diagrams.

    Args:
        diagrams: Dictionary mapping diagram IDs to Mermaid code
        output_path: Path to save the HTML file
        title: Title for the HTML page
        description: Description for the HTML page
        theme: Theme for the diagrams

    Returns:
        Path to the output HTML file
    """
    # Clean up the Mermaid code
    for diagram_id in diagrams:
        diagrams[diagram_id] = diagrams[diagram_id].strip()

    # Create the HTML
    html_parts = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        f"    <title>{title}</title>",
        '    <meta charset="UTF-8">',
        '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
        "    <style>",
        "        body {",
        '            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;',
        "            background-color: #f5f5f5;",
        "            margin: 0;",
        "            padding: 20px;",
        "        }",
        "        .container {",
        "            max-width: 1200px;",
        "            margin: 0 auto;",
        "        }",
        "        h1 {",
        "            font-size: 28px;",
        "            margin-bottom: 10px;",
        "        }",
        "        h2 {",
        "            font-size: 22px;",
        "            margin-top: 30px;",
        "            padding-bottom: 10px;",
        "            border-bottom: 1px solid #ddd;",
        "        }",
        "        .description {",
        "            margin-bottom: 30px;",
        "            color: #555;",
        "        }",
        "        .diagram-container {",
        "            background-color: white;",
        "            border-radius: 5px;",
        "            padding: 20px;",
        "            margin-bottom: 30px;",
        "            box-shadow: 0 2px 4px rgba(0,0,0,0.1);",
        "        }",
        "        .mermaid {",
        "            display: flex;",
        "            justify-content: center;",
        "            margin: 20px 0;",
        "        }",
        "    </style>",
    ]
    html_parts.append(
        '    <script src="https://cdn.jsdelivr.net/npm/mermaid@9/dist/mermaid.min.js"></script>'
    )

    # Add initialization script
    init_options = {}
    if theme:
        init_options["theme"] = theme

    init_options_str = ", ".join([f"{k}: '{v}'" for k, v in init_options.items()])

    html_parts.extend(
        [
            "    <script>",
            '        document.addEventListener("DOMContentLoaded", function() {',
            f"            mermaid.initialize({{ startOnLoad: true, {init_options_str} }});",
            "        });",
            "    </script>",
            "</head>",
            "<body>",
            '    <div class="container">',
            f"        <h1>{title}</h1>",
        ]
    )

    # Add description if provided
    if description:
        html_parts.append(f'        <div class="description">{description}</div>')

    # Add each diagram
    for diagram_id, mermaid_code in diagrams.items():
        html_parts.extend(
            [
                '        <div class="diagram-container">',
                f"            <h2>{diagram_id}</h2>",
                '            <div class="mermaid">',
                mermaid_code,
                "            </div>",
                "        </div>",
            ]
        )

    # Close the HTML
    html_parts.extend(
        [
            "    </div>",
            "</body>",
            "</html>",
        ]
    )

    # Write the HTML to file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(html_parts))

    return output_path
