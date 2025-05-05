"""
JavaScript linters integration module.

This module provides integration with popular JavaScript linting tools such as
ESLint, JSHint, and StandardJS to analyze JavaScript code quality and detect potential issues.
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from rich.console import Console
from rich.table import Table

console = Console()


class JavaScriptLinter:
    """
    JavaScript code linter that integrates with various JavaScript linting tools.
    """

    def __init__(
        self,
        use_eslint: bool = True,
        use_jshint: bool = False,
        use_standard: bool = False,
        config_dir: Optional[str] = None,
    ):
        """
        Initialize the JavaScript linter.

        Args:
            use_eslint: Whether to use ESLint for linting
            use_jshint: Whether to use JSHint for linting
            use_standard: Whether to use StandardJS for linting
            config_dir: Directory containing configuration files for linters
        """
        self.use_eslint = use_eslint
        self.use_jshint = use_jshint
        self.use_standard = use_standard
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

    def run_eslint(
        self,
        target_path: str,
        config_file: Optional[str] = None,
        output_format: str = "json",
    ) -> Dict[str, Any]:
        """
        Run ESLint on the target path.

        Args:
            target_path: Path to the JavaScript file or directory to analyze
            config_file: Path to the ESLint configuration file
            output_format: Format of the output (json, stylish, html)

        Returns:
            Dictionary with ESLint analysis results
        """
        if not self._check_tool_available("eslint"):
            return {"error": "eslint not available"}

        cmd = ["eslint", target_path]

        if config_file:
            cmd.extend(["--config", config_file])
        elif self.config_dir:
            config_path = os.path.join(self.config_dir, ".eslintrc.js")
            if os.path.exists(config_path):
                cmd.extend(["--config", config_path])

        if output_format == "json":
            cmd.extend(["--format", "json"])
        elif output_format == "html":
            cmd.extend(["--format", "html"])
        else:
            cmd.extend(["--format", "stylish"])

        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )

            if output_format == "json":
                try:
                    return {
                        "result": json.loads(result.stdout),
                        "errors": result.stderr,
                    }
                except json.JSONDecodeError:
                    return {"result": result.stdout, "errors": result.stderr}
            else:
                return {"result": result.stdout, "errors": result.stderr}
        except Exception as e:
            return {"error": str(e)}

    def run_jshint(
        self,
        target_path: str,
        config_file: Optional[str] = None,
        output_format: str = "json",
    ) -> Dict[str, Any]:
        """
        Run JSHint on the target path.

        Args:
            target_path: Path to the JavaScript file or directory to analyze
            config_file: Path to the JSHint configuration file
            output_format: Format of the output (json, text)

        Returns:
            Dictionary with JSHint analysis results
        """
        if not self._check_tool_available("jshint"):
            return {"error": "jshint not available"}

        cmd = ["jshint", target_path]

        if config_file:
            cmd.extend(["--config", config_file])
        elif self.config_dir:
            config_path = os.path.join(self.config_dir, ".jshintrc")
            if os.path.exists(config_path):
                cmd.extend(["--config", config_path])

        if output_format == "json":
            cmd.append("--reporter=json")

        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )

            if output_format == "json":
                try:
                    return {
                        "result": json.loads(result.stdout),
                        "errors": result.stderr,
                    }
                except json.JSONDecodeError:
                    return {"result": result.stdout, "errors": result.stderr}
            else:
                return {"result": result.stdout, "errors": result.stderr}
        except Exception as e:
            return {"error": str(e)}

    def run_standard(
        self, target_path: str, output_format: str = "json"
    ) -> Dict[str, Any]:
        """
        Run StandardJS on the target path.

        Args:
            target_path: Path to the JavaScript file or directory to analyze
            output_format: Format of the output (json, text)

        Returns:
            Dictionary with StandardJS analysis results
        """
        if not self._check_tool_available("standard"):
            return {"error": "standard not available"}

        cmd = ["standard", target_path]

        if output_format == "json":
            cmd.append("--reporter=json")

        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )

            if output_format == "json":
                try:
                    return {
                        "result": json.loads(result.stdout),
                        "errors": result.stderr,
                    }
                except json.JSONDecodeError:
                    return {"result": result.stdout, "errors": result.stderr}
            else:
                return {"result": result.stdout, "errors": result.stderr}
        except Exception as e:
            return {"error": str(e)}

    def analyze(self, target_path: str, output_format: str = "json") -> Dict[str, Any]:
        """
        Run all enabled linters on the target path.

        Args:
            target_path: Path to the JavaScript file or directory to analyze
            output_format: Format of the output (json, text, html)

        Returns:
            Dictionary with analysis results from all enabled linters
        """
        results = {}

        if self.use_eslint:
            results["eslint"] = self.run_eslint(
                target_path, output_format=output_format
            )

        if self.use_jshint:
            results["jshint"] = self.run_jshint(
                target_path, output_format=output_format
            )

        if self.use_standard:
            results["standard"] = self.run_standard(
                target_path, output_format=output_format
            )

        return results

    def generate_report(
        self, results: Dict[str, Any], output_format: str = "text"
    ) -> str:
        """
        Generate a report from the analysis results.

        Args:
            results: Analysis results from the analyze method
            output_format: Format of the report (text, json, html, markdown)

        Returns:
            Report in the specified format
        """
        if output_format == "json":
            return json.dumps(results, indent=2)

        elif output_format == "markdown":
            md_lines = ["# JavaScript Code Analysis Report\n"]

            for tool, tool_results in results.items():
                md_lines.append(f"## {tool.upper()} Results\n")

                if "error" in tool_results:
                    md_lines.append(f"Error: {tool_results['error']}\n")
                    continue

                if tool == "eslint":
                    # Format ESLint results
                    if isinstance(tool_results.get("result"), list):
                        for file_result in tool_results["result"]:
                            md_lines.append(f"### {file_result.get('filePath', '')}\n")

                            if "messages" in file_result and file_result["messages"]:
                                md_lines.append(
                                    "| Line | Column | Severity | Message | Rule |\n"
                                )
                                md_lines.append(
                                    "|------|--------|----------|---------|------|\n"
                                )

                                for message in file_result["messages"]:
                                    severity = (
                                        "Error"
                                        if message.get("severity") == 2
                                        else "Warning"
                                    )
                                    md_lines.append(
                                        f"| {message.get('line', '')} | "
                                        f"{message.get('column', '')} | "
                                        f"{severity} | "
                                        f"{message.get('message', '')} | "
                                        f"{message.get('ruleId', '')} |\n"
                                    )
                            else:
                                md_lines.append("No issues found.\n")
                    else:
                        md_lines.append(f"```\n{tool_results.get('result', '')}\n```\n")

                elif tool == "jshint":
                    # Format JSHint results
                    if isinstance(tool_results.get("result"), list):
                        for file_result in tool_results["result"]:
                            md_lines.append(f"### {file_result.get('file', '')}\n")

                            if "error" in file_result and file_result["error"].get(
                                "reason"
                            ):
                                md_lines.append("| Line | Column | Message | Code |\n")
                                md_lines.append("|------|--------|---------|------|\n")

                                error = file_result["error"]
                                md_lines.append(
                                    f"| {error.get('line', '')} | "
                                    f"{error.get('character', '')} | "
                                    f"{error.get('reason', '')} | "
                                    f"{error.get('code', '')} |\n"
                                )
                            else:
                                md_lines.append("No issues found.\n")
                    else:
                        md_lines.append(f"```\n{tool_results.get('result', '')}\n```\n")

                elif tool == "standard":
                    # Format StandardJS results
                    if isinstance(tool_results.get("result"), list):
                        for file_result in tool_results["result"]:
                            md_lines.append(f"### {file_result.get('file', '')}\n")

                            if "messages" in file_result and file_result["messages"]:
                                md_lines.append("| Line | Column | Message |\n")
                                md_lines.append("|------|--------|--------|\n")

                                for message in file_result["messages"]:
                                    md_lines.append(
                                        f"| {message.get('line', '')} | "
                                        f"{message.get('column', '')} | "
                                        f"{message.get('message', '')} |\n"
                                    )
                            else:
                                md_lines.append("No issues found.\n")
                    else:
                        md_lines.append(f"```\n{tool_results.get('result', '')}\n```\n")

                else:
                    # Generic format for other tools
                    md_lines.append(f"```\n{tool_results.get('result', '')}\n```\n")

            return "\n".join(md_lines)

        elif output_format == "html":
            # Simple HTML report
            html_lines = [
                "<!DOCTYPE html>",
                "<html>",
                "<head>",
                "    <title>JavaScript Code Analysis Report</title>",
                "    <style>",
                "        body { font-family: Arial, sans-serif; margin: 20px; }",
                "        h1 { color: #333; }",
                "        h2 { color: #666; margin-top: 30px; }",
                "        h3 { color: #999; margin-top: 20px; }",
                "        table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }",
                "        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }",
                "        th { background-color: #f2f2f2; }",
                "        tr:nth-child(even) { background-color: #f9f9f9; }",
                "        pre { background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; }",
                "        .error { color: red; }",
                "        .warning { color: orange; }",
                "    </style>",
                "</head>",
                "<body>",
                "    <h1>JavaScript Code Analysis Report</h1>",
            ]

            for tool, tool_results in results.items():
                html_lines.append(f"    <h2>{tool.upper()} Results</h2>")

                if "error" in tool_results:
                    html_lines.append(
                        f"    <p class='error'>Error: {tool_results['error']}</p>"
                    )
                    continue

                if tool == "eslint" and isinstance(tool_results.get("result"), list):
                    for file_result in tool_results["result"]:
                        html_lines.append(
                            f"    <h3>{file_result.get('filePath', '')}</h3>"
                        )

                        if "messages" in file_result and file_result["messages"]:
                            html_lines.append("    <table>")
                            html_lines.append(
                                "        <tr><th>Line</th><th>Column</th><th>Severity</th><th>Message</th><th>Rule</th></tr>"
                            )

                            for message in file_result["messages"]:
                                severity = (
                                    "Error"
                                    if message.get("severity") == 2
                                    else "Warning"
                                )
                                severity_class = (
                                    "error" if severity == "Error" else "warning"
                                )

                                html_lines.append(
                                    f"        <tr>"
                                    f"<td>{message.get('line', '')}</td>"
                                    f"<td>{message.get('column', '')}</td>"
                                    f"<td class='{severity_class}'>{severity}</td>"
                                    f"<td>{message.get('message', '')}</td>"
                                    f"<td>{message.get('ruleId', '')}</td>"
                                    f"</tr>"
                                )

                            html_lines.append("    </table>")
                        else:
                            html_lines.append("    <p>No issues found.</p>")
                elif tool == "jshint" and isinstance(tool_results.get("result"), list):
                    for file_result in tool_results["result"]:
                        html_lines.append(f"    <h3>{file_result.get('file', '')}</h3>")

                        if "error" in file_result and file_result["error"].get(
                            "reason"
                        ):
                            html_lines.append("    <table>")
                            html_lines.append(
                                "        <tr><th>Line</th><th>Column</th><th>Message</th><th>Code</th></tr>"
                            )

                            error = file_result["error"]
                            html_lines.append(
                                f"        <tr>"
                                f"<td>{error.get('line', '')}</td>"
                                f"<td>{error.get('character', '')}</td>"
                                f"<td>{error.get('reason', '')}</td>"
                                f"<td>{error.get('code', '')}</td>"
                                f"</tr>"
                            )

                            html_lines.append("    </table>")
                        else:
                            html_lines.append("    <p>No issues found.</p>")
                elif tool == "standard" and isinstance(
                    tool_results.get("result"), list
                ):
                    for file_result in tool_results["result"]:
                        html_lines.append(f"    <h3>{file_result.get('file', '')}</h3>")

                        if "messages" in file_result and file_result["messages"]:
                            html_lines.append("    <table>")
                            html_lines.append(
                                "        <tr><th>Line</th><th>Column</th><th>Message</th></tr>"
                            )

                            for message in file_result["messages"]:
                                html_lines.append(
                                    f"        <tr>"
                                    f"<td>{message.get('line', '')}</td>"
                                    f"<td>{message.get('column', '')}</td>"
                                    f"<td>{message.get('message', '')}</td>"
                                    f"</tr>"
                                )

                            html_lines.append("    </table>")
                        else:
                            html_lines.append("    <p>No issues found.</p>")
                else:
                    html_lines.append(
                        f"    <pre>{tool_results.get('result', '')}</pre>"
                    )

            html_lines.extend(["</body>", "</html>"])

            return "\n".join(html_lines)

        else:  # text format
            text_lines = [
                "JavaScript Code Analysis Report",
                "===============================\n",
            ]

            for tool, tool_results in results.items():
                text_lines.append(f"{tool.upper()} Results:")
                text_lines.append("-" * (len(tool) + 9) + "\n")

                if "error" in tool_results:
                    text_lines.append(f"Error: {tool_results['error']}\n")
                    continue

                text_lines.append(str(tool_results.get("result", "")))
                text_lines.append("\n")

            return "\n".join(text_lines)


def analyze_javascript_code(
    target_path: str,
    output_path: Optional[str] = None,
    output_format: str = "markdown",
    use_eslint: bool = True,
    use_jshint: bool = False,
    use_standard: bool = False,
    config_dir: Optional[str] = None,
) -> str:
    """
    Analyze JavaScript code using various linting tools.

    Args:
        target_path: Path to the JavaScript file or directory to analyze
        output_path: Path to save the analysis report, if None returns as string
        output_format: Format of the report (text, json, html, markdown)
        use_eslint: Whether to use ESLint for linting
        use_jshint: Whether to use JSHint for linting
        use_standard: Whether to use StandardJS for linting
        config_dir: Directory containing configuration files for linters

    Returns:
        Path to the output report file or the report as a string if output_path is None
    """
    console.print(f"Analyzing JavaScript code in [cyan]{target_path}[/cyan]...")

    linter = JavaScriptLinter(
        use_eslint=use_eslint,
        use_jshint=use_jshint,
        use_standard=use_standard,
        config_dir=config_dir,
    )

    results = linter.analyze(target_path, output_format="json")
    report = linter.generate_report(results, output_format=output_format)

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)
        console.print(f"Analysis report saved to [green]{output_path}[/green]")
        return output_path

    return report
