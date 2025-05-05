"""
Documentation generator module.

This module provides functionality to generate comprehensive documentation
from source code using various documentation tools and formats.
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from rich.console import Console
from rich.table import Table

console = Console()


class DocumentationGenerator:
    """
    Documentation generator that integrates with various documentation tools.
    """

    def __init__(
        self,
        output_dir: Optional[str] = None,
        template_dir: Optional[str] = None,
        config_dir: Optional[str] = None,
    ):
        """
        Initialize the documentation generator.

        Args:
            output_dir: Directory to save generated documentation
            template_dir: Directory containing documentation templates
            config_dir: Directory containing configuration files for documentation tools
        """
        self.output_dir = output_dir
        self.template_dir = template_dir
        self.config_dir = config_dir

    def _check_tool_available(self, tool_name: str) -> bool:
        """
        Check if a tool is available in the system.

        Args:
            tool_name: Name of the tool to check

        Returns:
            True if the tool is available, False otherwise
        """
        try:
            subprocess.run(
                [tool_name, "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            return True
        except FileNotFoundError:
            console.print(f"[yellow]Warning: {tool_name} not found in PATH[/yellow]")
            return False

    def generate_sphinx_docs(
        self,
        target_path: str,
        output_dir: Optional[str] = None,
        config_file: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate documentation using Sphinx.

        Args:
            target_path: Path to the Python project to document
            output_dir: Directory to save generated documentation
            config_file: Path to the Sphinx configuration file

        Returns:
            Dictionary with documentation generation results
        """
        if not self._check_tool_available("sphinx-build"):
            return {"error": "sphinx-build not available"}

        output_dir = output_dir or self.output_dir
        if not output_dir:
            output_dir = os.path.join(target_path, "docs", "build", "html")

        os.makedirs(output_dir, exist_ok=True)

        # Create Sphinx configuration if not provided
        if not config_file and self.config_dir:
            config_file = os.path.join(self.config_dir, "conf.py")

        if not config_file or not os.path.exists(config_file):
            # Create a temporary conf.py
            config_file = self._create_sphinx_config(target_path)

        # Create Sphinx source directory
        source_dir = os.path.join(output_dir, "_source")
        os.makedirs(source_dir, exist_ok=True)

        # Generate API documentation using sphinx-apidoc
        apidoc_cmd = [
            "sphinx-apidoc",
            "-o",
            source_dir,
            target_path,
            "--force",
            "--separate",
        ]

        try:
            subprocess.run(
                apidoc_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
        except Exception as e:
            return {"error": f"Error running sphinx-apidoc: {str(e)}"}

        # Copy config file to source directory
        import shutil

        shutil.copy(config_file, os.path.join(source_dir, "conf.py"))

        # Create index.rst if it doesn't exist
        index_path = os.path.join(source_dir, "index.rst")
        if not os.path.exists(index_path):
            self._create_sphinx_index(source_dir, target_path)

        # Build documentation
        build_cmd = ["sphinx-build", "-b", "html", source_dir, output_dir]

        try:
            result = subprocess.run(
                build_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )

            return {
                "result": "Documentation generated successfully",
                "output_dir": output_dir,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        except Exception as e:
            return {"error": f"Error building documentation: {str(e)}"}

    def _create_sphinx_config(self, target_path: str) -> str:
        """
        Create a basic Sphinx configuration file.

        Args:
            target_path: Path to the Python project

        Returns:
            Path to the created configuration file
        """
        # Get project name from directory
        project_name = os.path.basename(os.path.abspath(target_path))

        # Create a temporary directory for the configuration
        temp_dir = os.path.join(target_path, "docs", "temp")
        os.makedirs(temp_dir, exist_ok=True)

        config_path = os.path.join(temp_dir, "conf.py")

        with open(config_path, "w") as f:
            f.write(
                f"""
# Configuration file for Sphinx documentation builder.

# -- Project information -----------------------------------------------------
project = '{project_name}'
copyright = '2025, Twinizer'
author = 'Twinizer'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# -- Extension configuration -------------------------------------------------
autodoc_member_order = 'bysource'
autodoc_typehints = 'description'
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = True
napoleon_include_special_with_doc = True
"""
            )

        return config_path

    def _create_sphinx_index(self, source_dir: str, target_path: str) -> None:
        """
        Create a basic index.rst file for Sphinx documentation.

        Args:
            source_dir: Directory to save the index file
            target_path: Path to the Python project
        """
        # Get project name from directory
        project_name = os.path.basename(os.path.abspath(target_path))

        index_path = os.path.join(source_dir, "index.rst")

        with open(index_path, "w") as f:
            f.write(
                f"""
Welcome to {project_name}'s documentation!
{'=' * (len(project_name) + 23)}

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules

Indices and tables
=================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
"""
            )

    def generate_mkdocs(
        self,
        target_path: str,
        output_dir: Optional[str] = None,
        config_file: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate documentation using MkDocs.

        Args:
            target_path: Path to the project to document
            output_dir: Directory to save generated documentation
            config_file: Path to the MkDocs configuration file

        Returns:
            Dictionary with documentation generation results
        """
        if not self._check_tool_available("mkdocs"):
            return {"error": "mkdocs not available"}

        output_dir = output_dir or self.output_dir
        if not output_dir:
            output_dir = os.path.join(target_path, "site")

        # Create MkDocs configuration if not provided
        if not config_file and self.config_dir:
            config_file = os.path.join(self.config_dir, "mkdocs.yml")

        if not config_file or not os.path.exists(config_file):
            # Create a temporary mkdocs.yml
            config_file = self._create_mkdocs_config(target_path)

        # Create docs directory
        docs_dir = os.path.join(target_path, "docs")
        os.makedirs(docs_dir, exist_ok=True)

        # Create index.md if it doesn't exist
        index_path = os.path.join(docs_dir, "index.md")
        if not os.path.exists(index_path):
            self._create_mkdocs_index(docs_dir, target_path)

        # Build documentation
        build_cmd = ["mkdocs", "build", "-f", config_file, "-d", output_dir]

        try:
            result = subprocess.run(
                build_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )

            return {
                "result": "Documentation generated successfully",
                "output_dir": output_dir,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        except Exception as e:
            return {"error": f"Error building documentation: {str(e)}"}

    def _create_mkdocs_config(self, target_path: str) -> str:
        """
        Create a basic MkDocs configuration file.

        Args:
            target_path: Path to the project

        Returns:
            Path to the created configuration file
        """
        # Get project name from directory
        project_name = os.path.basename(os.path.abspath(target_path))

        config_path = os.path.join(target_path, "mkdocs.yml")

        with open(config_path, "w") as f:
            f.write(
                f"""
site_name: {project_name} Documentation
site_description: Documentation for {project_name}
site_author: Twinizer

theme:
  name: material
  palette:
    primary: indigo
    accent: indigo
  features:
    - navigation.instant
    - navigation.tracking
    - navigation.expand
    - navigation.indexes
    - toc.integrate

markdown_extensions:
  - admonition
  - codehilite
  - footnotes
  - pymdownx.highlight
  - pymdownx.superfences
  - pymdownx.inlinehilite
  - pymdownx.tabbed
  - pymdownx.critic
  - pymdownx.tasklist:
      custom_checkbox: true

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          selection:
            docstring_style: google
          rendering:
            show_source: true
            show_if_no_docstring: true

nav:
  - Home: index.md
  - API Reference: reference/
"""
            )

        return config_path

    def _create_mkdocs_index(self, docs_dir: str, target_path: str) -> None:
        """
        Create a basic index.md file for MkDocs documentation.

        Args:
            docs_dir: Directory to save the index file
            target_path: Path to the project
        """
        # Get project name from directory
        project_name = os.path.basename(os.path.abspath(target_path))

        index_path = os.path.join(docs_dir, "index.md")

        with open(index_path, "w") as f:
            f.write(
                f"""
# {project_name} Documentation

Welcome to the {project_name} documentation.

## Overview

This documentation provides comprehensive information about the {project_name} project,
including API reference, usage examples, and development guidelines.

## Installation

```bash
pip install {project_name.lower()}
```

## Quick Start

```python
import {project_name.lower()}

# Example code here
```

## API Reference

For detailed API documentation, see the [API Reference](reference/).
"""
            )

    def generate_pdoc(
        self, target_path: str, output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate documentation using pdoc.

        Args:
            target_path: Path to the Python module or package to document
            output_dir: Directory to save generated documentation

        Returns:
            Dictionary with documentation generation results
        """
        if not self._check_tool_available("pdoc"):
            return {"error": "pdoc not available"}

        output_dir = output_dir or self.output_dir
        if not output_dir:
            output_dir = os.path.join(os.path.dirname(target_path), "docs", "html")

        os.makedirs(output_dir, exist_ok=True)

        # Build documentation
        build_cmd = ["pdoc", "--html", "--output-dir", output_dir, target_path]

        try:
            result = subprocess.run(
                build_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )

            return {
                "result": "Documentation generated successfully",
                "output_dir": output_dir,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        except Exception as e:
            return {"error": f"Error building documentation: {str(e)}"}

    def generate_mermaid_diagrams(
        self,
        target_path: str,
        output_dir: Optional[str] = None,
        diagram_types: List[str] = ["class", "package"],
    ) -> Dict[str, Any]:
        """
        Generate Mermaid diagrams from Python code.

        Args:
            target_path: Path to the Python project
            output_dir: Directory to save generated diagrams
            diagram_types: Types of diagrams to generate (class, package, sequence)

        Returns:
            Dictionary with diagram generation results
        """
        try:
            import importlib.util

            pyreverse_spec = importlib.util.find_spec("pylint")
            if pyreverse_spec is None:
                return {"error": "pylint (with pyreverse) not available"}
        except ImportError:
            return {"error": "pylint (with pyreverse) not available"}

        output_dir = output_dir or self.output_dir
        if not output_dir:
            output_dir = os.path.join(target_path, "docs", "diagrams")

        os.makedirs(output_dir, exist_ok=True)

        results = {}

        # Generate diagrams using pyreverse
        for diagram_type in diagram_types:
            if diagram_type == "class":
                # Generate class diagram
                try:
                    # First generate dot files with pyreverse
                    pyreverse_cmd = [
                        "pyreverse",
                        "-o",
                        "dot",
                        "-p",
                        os.path.basename(target_path),
                        target_path,
                    ]

                    subprocess.run(
                        pyreverse_cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        check=False,
                    )

                    # Convert dot to Mermaid
                    dot_file = f"classes_{os.path.basename(target_path)}.dot"
                    if os.path.exists(dot_file):
                        mermaid_content = self._dot_to_mermaid(dot_file, "class")

                        # Save Mermaid diagram
                        mermaid_file = os.path.join(output_dir, f"class_diagram.md")
                        with open(mermaid_file, "w") as f:
                            f.write("# Class Diagram\n\n")
                            f.write("```mermaid\n")
                            f.write(mermaid_content)
                            f.write("\n```\n")

                        results["class_diagram"] = {
                            "result": "Class diagram generated successfully",
                            "output_file": mermaid_file,
                        }

                        # Clean up dot file
                        os.remove(dot_file)
                    else:
                        results["class_diagram"] = {
                            "error": "Failed to generate class diagram"
                        }
                except Exception as e:
                    results["class_diagram"] = {
                        "error": f"Error generating class diagram: {str(e)}"
                    }

            elif diagram_type == "package":
                # Generate package diagram
                try:
                    # First generate dot files with pyreverse
                    pyreverse_cmd = [
                        "pyreverse",
                        "-o",
                        "dot",
                        "-p",
                        os.path.basename(target_path),
                        "-k",
                        target_path,
                    ]

                    subprocess.run(
                        pyreverse_cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        check=False,
                    )

                    # Convert dot to Mermaid
                    dot_file = f"packages_{os.path.basename(target_path)}.dot"
                    if os.path.exists(dot_file):
                        mermaid_content = self._dot_to_mermaid(dot_file, "package")

                        # Save Mermaid diagram
                        mermaid_file = os.path.join(output_dir, f"package_diagram.md")
                        with open(mermaid_file, "w") as f:
                            f.write("# Package Diagram\n\n")
                            f.write("```mermaid\n")
                            f.write(mermaid_content)
                            f.write("\n```\n")

                        results["package_diagram"] = {
                            "result": "Package diagram generated successfully",
                            "output_file": mermaid_file,
                        }

                        # Clean up dot file
                        os.remove(dot_file)
                    else:
                        results["package_diagram"] = {
                            "error": "Failed to generate package diagram"
                        }
                except Exception as e:
                    results["package_diagram"] = {
                        "error": f"Error generating package diagram: {str(e)}"
                    }

        return results

    def _dot_to_mermaid(self, dot_file: str, diagram_type: str) -> str:
        """
        Convert a DOT file to Mermaid syntax.

        Args:
            dot_file: Path to the DOT file
            diagram_type: Type of diagram (class, package)

        Returns:
            Mermaid diagram content
        """
        # Simple conversion from DOT to Mermaid
        with open(dot_file, "r") as f:
            dot_content = f.read()

        if diagram_type == "class":
            # Convert to class diagram
            mermaid_lines = ["classDiagram"]

            # Parse DOT file
            import re

            # Extract nodes
            nodes = {}
            for node_match in re.finditer(
                r'"([^"]+)" \[label="{([^}]+)}"\]', dot_content
            ):
                node_id = node_match.group(1)
                node_label = node_match.group(2)

                # Process label
                parts = node_label.split("|")
                class_name = parts[0].strip()

                nodes[node_id] = class_name

                # Add class to diagram
                mermaid_lines.append(f"    class {class_name}")

                # Add attributes and methods if available
                if len(parts) > 1 and parts[1].strip():
                    attributes = parts[1].strip().split("\\l")
                    for attr in attributes:
                        if attr.strip():
                            mermaid_lines.append(f"    {class_name} : {attr.strip()}")

                if len(parts) > 2 and parts[2].strip():
                    methods = parts[2].strip().split("\\l")
                    for method in methods:
                        if method.strip():
                            mermaid_lines.append(f"    {class_name} : {method.strip()}")

            # Extract relationships
            for edge_match in re.finditer(
                r'"([^"]+)" -> "([^"]+)" \[arrowhead=([^,]+),.*\]', dot_content
            ):
                source = edge_match.group(1)
                target = edge_match.group(2)
                arrow_type = edge_match.group(3)

                if source in nodes and target in nodes:
                    source_class = nodes[source]
                    target_class = nodes[target]

                    # Map arrow type to relationship
                    if arrow_type == "empty":
                        # Inheritance
                        mermaid_lines.append(f"    {target_class} <|-- {source_class}")
                    elif arrow_type == "diamond":
                        # Composition
                        mermaid_lines.append(f"    {target_class} *-- {source_class}")
                    elif arrow_type == "odiamond":
                        # Aggregation
                        mermaid_lines.append(f"    {target_class} o-- {source_class}")
                    else:
                        # Association
                        mermaid_lines.append(f"    {source_class} --> {target_class}")

            return "\n".join(mermaid_lines)

        elif diagram_type == "package":
            # Convert to package diagram
            mermaid_lines = ["flowchart LR"]

            # Parse DOT file
            import re

            # Extract nodes
            nodes = {}
            for node_match in re.finditer(
                r'"([^"]+)" \[label="([^"]+)".*\]', dot_content
            ):
                node_id = node_match.group(1)
                node_label = node_match.group(2)

                nodes[node_id] = node_label

                # Add package to diagram
                mermaid_lines.append(f"    {node_id}[{node_label}]")

            # Extract relationships
            for edge_match in re.finditer(r'"([^"]+)" -> "([^"]+)"', dot_content):
                source = edge_match.group(1)
                target = edge_match.group(2)

                if source in nodes and target in nodes:
                    mermaid_lines.append(f"    {source} --> {target}")

            return "\n".join(mermaid_lines)

        return ""


def generate_documentation(
    target_path: str,
    output_dir: Optional[str] = None,
    doc_type: str = "sphinx",
    generate_diagrams: bool = True,
    template_dir: Optional[str] = None,
    config_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate documentation for a project.

    Args:
        target_path: Path to the project to document
        output_dir: Directory to save generated documentation
        doc_type: Type of documentation to generate (sphinx, mkdocs, pdoc)
        generate_diagrams: Whether to generate diagrams
        template_dir: Directory containing documentation templates
        config_dir: Directory containing configuration files for documentation tools

    Returns:
        Dictionary with documentation generation results
    """
    console.print(f"Generating documentation for [cyan]{target_path}[/cyan]...")

    generator = DocumentationGenerator(
        output_dir=output_dir, template_dir=template_dir, config_dir=config_dir
    )

    results = {}

    # Generate documentation based on doc_type
    if doc_type == "sphinx":
        results["sphinx"] = generator.generate_sphinx_docs(target_path, output_dir)
    elif doc_type == "mkdocs":
        results["mkdocs"] = generator.generate_mkdocs(target_path, output_dir)
    elif doc_type == "pdoc":
        results["pdoc"] = generator.generate_pdoc(target_path, output_dir)
    else:
        results["error"] = f"Unsupported documentation type: {doc_type}"

    # Generate diagrams if requested
    if generate_diagrams:
        diagram_output_dir = output_dir
        if output_dir:
            diagram_output_dir = os.path.join(output_dir, "diagrams")

        results["diagrams"] = generator.generate_mermaid_diagrams(
            target_path, output_dir=diagram_output_dir
        )

    return results
