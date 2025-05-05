"""
Main code analyzer module.

This module provides a unified interface for analyzing code using various linting tools
and generating documentation for different programming languages.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from rich.console import Console
from rich.table import Table

# Import documentation generator
from twinizer.code_analyzer.documentation.generator import generate_documentation
from twinizer.code_analyzer.linters.cpp import analyze_cpp_code
from twinizer.code_analyzer.linters.javascript import analyze_javascript_code

# Import linters
from twinizer.code_analyzer.linters.python import analyze_python_code

console = Console()


class CodeAnalyzer:
    """
    Main code analyzer class that provides a unified interface for code analysis and documentation.
    """

    def __init__(
        self, output_dir: Optional[str] = None, config_dir: Optional[str] = None
    ):
        """
        Initialize the code analyzer.

        Args:
            output_dir: Directory to save analysis reports and documentation
            config_dir: Directory containing configuration files for linters and documentation tools
        """
        self.output_dir = output_dir
        self.config_dir = config_dir

        # Create output directory if it doesn't exist
        if self.output_dir:
            os.makedirs(self.output_dir, exist_ok=True)

    def detect_language(self, file_path: str) -> str:
        """
        Detect the programming language of a file based on its extension.

        Args:
            file_path: Path to the file

        Returns:
            Detected programming language
        """
        extension = os.path.splitext(file_path)[1].lower()

        if extension in [".py"]:
            return "python"
        elif extension in [".c", ".cpp", ".cc", ".cxx", ".h", ".hpp", ".hxx"]:
            return "cpp"
        elif extension in [".js", ".jsx", ".ts", ".tsx"]:
            return "javascript"
        else:
            return "unknown"

    def analyze_file(
        self,
        file_path: str,
        language: Optional[str] = None,
        output_format: str = "markdown",
    ) -> Dict[str, Any]:
        """
        Analyze a single file.

        Args:
            file_path: Path to the file to analyze
            language: Programming language of the file (if None, will be auto-detected)
            output_format: Format of the analysis report (text, json, html, markdown)

        Returns:
            Dictionary with analysis results
        """
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}

        if not language:
            language = self.detect_language(file_path)

        if language == "unknown":
            return {"error": f"Unsupported file type: {file_path}"}

        output_path = None
        if self.output_dir:
            file_name = os.path.basename(file_path)
            output_path = os.path.join(
                self.output_dir, f"{file_name}_analysis.{output_format}"
            )

        if language == "python":
            result = analyze_python_code(
                file_path,
                output_path=output_path,
                output_format=output_format,
                config_dir=self.config_dir,
            )
        elif language == "cpp":
            result = analyze_cpp_code(
                file_path,
                output_path=output_path,
                output_format=output_format,
                config_dir=self.config_dir,
            )
        elif language == "javascript":
            result = analyze_javascript_code(
                file_path,
                output_path=output_path,
                output_format=output_format,
                config_dir=self.config_dir,
            )
        else:
            return {"error": f"Unsupported language: {language}"}

        return {"result": result, "language": language, "output_path": output_path}

    def analyze_directory(
        self,
        directory_path: str,
        output_format: str = "markdown",
        recursive: bool = True,
        file_extensions: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze all files in a directory.

        Args:
            directory_path: Path to the directory to analyze
            output_format: Format of the analysis reports (text, json, html, markdown)
            recursive: Whether to analyze files in subdirectories
            file_extensions: List of file extensions to analyze (if None, analyze all supported files)

        Returns:
            Dictionary with analysis results for each file
        """
        if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
            return {"error": f"Directory not found: {directory_path}"}

        results = {}

        # Create a summary report file
        summary_path = None
        if self.output_dir:
            dir_name = os.path.basename(os.path.abspath(directory_path))
            summary_path = os.path.join(
                self.output_dir, f"{dir_name}_analysis_summary.{output_format}"
            )

        # Get all files in the directory
        if recursive:
            files = []
            for root, _, filenames in os.walk(directory_path):
                for filename in filenames:
                    files.append(os.path.join(root, filename))
        else:
            files = [
                os.path.join(directory_path, f)
                for f in os.listdir(directory_path)
                if os.path.isfile(os.path.join(directory_path, f))
            ]

        # Filter files by extension if specified
        if file_extensions:
            files = [
                f for f in files if os.path.splitext(f)[1].lower() in file_extensions
            ]
        else:
            # Only analyze supported file types
            supported_extensions = [
                ".py",
                ".c",
                ".cpp",
                ".cc",
                ".cxx",
                ".h",
                ".hpp",
                ".hxx",
                ".js",
                ".jsx",
                ".ts",
                ".tsx",
            ]
            files = [
                f
                for f in files
                if os.path.splitext(f)[1].lower() in supported_extensions
            ]

        # Analyze each file
        for file_path in files:
            console.print(f"Analyzing [cyan]{file_path}[/cyan]...")
            result = self.analyze_file(file_path, output_format=output_format)
            results[file_path] = result

        # Generate summary report
        if summary_path:
            self._generate_summary_report(results, summary_path, output_format)
            results["summary"] = {"path": summary_path}

        return results

    def _generate_summary_report(
        self, results: Dict[str, Any], output_path: str, output_format: str
    ) -> None:
        """
        Generate a summary report of all analysis results.

        Args:
            results: Dictionary with analysis results for each file
            output_path: Path to save the summary report
            output_format: Format of the summary report (text, json, html, markdown)
        """
        if output_format == "json":
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2)

        elif output_format == "markdown":
            md_lines = ["# Code Analysis Summary\n"]

            # Count files by language
            language_counts = {}
            for file_path, result in results.items():
                language = result.get("language", "unknown")
                language_counts[language] = language_counts.get(language, 0) + 1

            md_lines.append("## Overview\n")
            md_lines.append(f"Total files analyzed: {len(results)}\n")

            md_lines.append("### Files by Language\n")
            md_lines.append("| Language | Count |\n")
            md_lines.append("|----------|-------|\n")
            for language, count in language_counts.items():
                md_lines.append(f"| {language} | {count} |\n")

            md_lines.append("\n## Analysis Results\n")

            for file_path, result in results.items():
                md_lines.append(f"### {os.path.basename(file_path)}\n")
                md_lines.append(f"- Path: `{file_path}`\n")
                md_lines.append(f"- Language: {result.get('language', 'unknown')}\n")

                if "error" in result:
                    md_lines.append(f"- Error: {result['error']}\n")
                else:
                    output_path = result.get("output_path")
                    if output_path:
                        md_lines.append(
                            f"- Analysis report: [{os.path.basename(output_path)}]({output_path})\n"
                        )
                    else:
                        md_lines.append(
                            f"- Analysis result: {result.get('result', '')}\n"
                        )

            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n".join(md_lines))

        elif output_format == "html":
            html_lines = [
                "<!DOCTYPE html>",
                "<html>",
                "<head>",
                "    <title>Code Analysis Summary</title>",
                "    <style>",
                "        body { font-family: Arial, sans-serif; margin: 20px; }",
                "        h1 { color: #333; }",
                "        h2 { color: #666; margin-top: 30px; }",
                "        h3 { color: #999; margin-top: 20px; }",
                "        table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }",
                "        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }",
                "        th { background-color: #f2f2f2; }",
                "        tr:nth-child(even) { background-color: #f9f9f9; }",
                "        .error { color: red; }",
                "    </style>",
                "</head>",
                "<body>",
                "    <h1>Code Analysis Summary</h1>",
            ]

            # Count files by language
            language_counts = {}
            for file_path, result in results.items():
                language = result.get("language", "unknown")
                language_counts[language] = language_counts.get(language, 0) + 1

            html_lines.append("    <h2>Overview</h2>")
            html_lines.append(f"    <p>Total files analyzed: {len(results)}</p>")

            html_lines.append("    <h3>Files by Language</h3>")
            html_lines.append("    <table>")
            html_lines.append("        <tr><th>Language</th><th>Count</th></tr>")
            for language, count in language_counts.items():
                html_lines.append(
                    f"        <tr><td>{language}</td><td>{count}</td></tr>"
                )
            html_lines.append("    </table>")

            html_lines.append("    <h2>Analysis Results</h2>")

            for file_path, result in results.items():
                html_lines.append(f"    <h3>{os.path.basename(file_path)}</h3>")
                html_lines.append(f"    <p>Path: <code>{file_path}</code></p>")
                html_lines.append(
                    f"    <p>Language: {result.get('language', 'unknown')}</p>"
                )

                if "error" in result:
                    html_lines.append(
                        f"    <p class='error'>Error: {result['error']}</p>"
                    )
                else:
                    output_path = result.get("output_path")
                    if output_path:
                        html_lines.append(
                            f"    <p>Analysis report: <a href='{output_path}'>{os.path.basename(output_path)}</a></p>"
                        )
                    else:
                        html_lines.append(
                            f"    <p>Analysis result: {result.get('result', '')}</p>"
                        )

            html_lines.extend(["</body>", "</html>"])

            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n".join(html_lines))

        else:  # text format
            text_lines = ["Code Analysis Summary", "=====================\n"]

            # Count files by language
            language_counts = {}
            for file_path, result in results.items():
                language = result.get("language", "unknown")
                language_counts[language] = language_counts.get(language, 0) + 1

            text_lines.append("Overview:")
            text_lines.append(f"Total files analyzed: {len(results)}\n")

            text_lines.append("Files by Language:")
            for language, count in language_counts.items():
                text_lines.append(f"- {language}: {count}")

            text_lines.append("\nAnalysis Results:")

            for file_path, result in results.items():
                text_lines.append(f"\n{os.path.basename(file_path)}:")
                text_lines.append(f"- Path: {file_path}")
                text_lines.append(f"- Language: {result.get('language', 'unknown')}")

                if "error" in result:
                    text_lines.append(f"- Error: {result['error']}")
                else:
                    output_path = result.get("output_path")
                    if output_path:
                        text_lines.append(f"- Analysis report: {output_path}")
                    else:
                        text_lines.append(
                            f"- Analysis result: {result.get('result', '')}"
                        )

            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n".join(text_lines))

    def generate_docs(
        self, target_path: str, doc_type: str = "sphinx", generate_diagrams: bool = True
    ) -> Dict[str, Any]:
        """
        Generate documentation for a project.

        Args:
            target_path: Path to the project to document
            doc_type: Type of documentation to generate (sphinx, mkdocs, pdoc)
            generate_diagrams: Whether to generate diagrams

        Returns:
            Dictionary with documentation generation results
        """
        if not os.path.exists(target_path):
            return {"error": f"Path not found: {target_path}"}

        output_dir = None
        if self.output_dir:
            dir_name = os.path.basename(os.path.abspath(target_path))
            output_dir = os.path.join(self.output_dir, f"{dir_name}_docs")

        return generate_documentation(
            target_path,
            output_dir=output_dir,
            doc_type=doc_type,
            generate_diagrams=generate_diagrams,
            config_dir=self.config_dir,
        )


def analyze_code(
    target_path: str,
    output_dir: Optional[str] = None,
    output_format: str = "markdown",
    config_dir: Optional[str] = None,
    recursive: bool = True,
    generate_docs: bool = False,
    doc_type: str = "sphinx",
) -> Dict[str, Any]:
    """
    Analyze code in a file or directory.

    Args:
        target_path: Path to the file or directory to analyze
        output_dir: Directory to save analysis reports and documentation
        output_format: Format of the analysis reports (text, json, html, markdown)
        config_dir: Directory containing configuration files for linters and documentation tools
        recursive: Whether to analyze files in subdirectories (if target_path is a directory)
        generate_docs: Whether to generate documentation for the project
        doc_type: Type of documentation to generate (sphinx, mkdocs, pdoc)

    Returns:
        Dictionary with analysis results
    """
    analyzer = CodeAnalyzer(output_dir=output_dir, config_dir=config_dir)

    results = {}

    if os.path.isfile(target_path):
        results["analysis"] = analyzer.analyze_file(
            target_path, output_format=output_format
        )
    elif os.path.isdir(target_path):
        results["analysis"] = analyzer.analyze_directory(
            target_path, output_format=output_format, recursive=recursive
        )
    else:
        return {"error": f"Path not found: {target_path}"}

    if generate_docs:
        results["documentation"] = analyzer.generate_docs(
            target_path, doc_type=doc_type
        )

    return results
