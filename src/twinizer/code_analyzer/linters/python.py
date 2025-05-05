"""
Python linters integration module.

This module provides integration with popular Python linting tools such as
flake8, pylint, and mypy to analyze Python code quality and detect potential issues.
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from rich.console import Console
from rich.table import Table

console = Console()


class PythonLinter:
    """
    Python code linter that integrates with various Python linting tools.
    """

    def __init__(
        self,
        use_flake8: bool = True,
        use_pylint: bool = True,
        use_mypy: bool = False,
        use_bandit: bool = False,
        config_dir: Optional[str] = None,
    ):
        """
        Initialize the Python linter.

        Args:
            use_flake8: Whether to use flake8 for linting
            use_pylint: Whether to use pylint for linting
            use_mypy: Whether to use mypy for type checking
            use_bandit: Whether to use bandit for security analysis
            config_dir: Directory containing configuration files for linters
        """
        self.use_flake8 = use_flake8
        self.use_pylint = use_pylint
        self.use_mypy = use_mypy
        self.use_bandit = use_bandit
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

    def run_flake8(
        self,
        target_path: str,
        config_file: Optional[str] = None,
        output_format: str = "json",
    ) -> Dict[str, Any]:
        """
        Run flake8 on the target path.

        Args:
            target_path: Path to the Python file or directory to analyze
            config_file: Path to the flake8 configuration file
            output_format: Format of the output (json, text)

        Returns:
            Dictionary with flake8 analysis results
        """
        if not self._check_tool_available("flake8"):
            return {"error": "flake8 not available"}

        cmd = ["flake8", target_path]

        if config_file:
            cmd.extend(["--config", config_file])
        elif self.config_dir:
            config_path = os.path.join(self.config_dir, ".flake8")
            if os.path.exists(config_path):
                cmd.extend(["--config", config_path])

        if output_format == "json":
            cmd.extend(["--format", "json"])

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

    def run_pylint(
        self,
        target_path: str,
        config_file: Optional[str] = None,
        output_format: str = "json",
    ) -> Dict[str, Any]:
        """
        Run pylint on the target path.

        Args:
            target_path: Path to the Python file or directory to analyze
            config_file: Path to the pylint configuration file
            output_format: Format of the output (json, text)

        Returns:
            Dictionary with pylint analysis results
        """
        if not self._check_tool_available("pylint"):
            return {"error": "pylint not available"}

        cmd = ["pylint", target_path]

        if config_file:
            cmd.extend(["--rcfile", config_file])
        elif self.config_dir:
            config_path = os.path.join(self.config_dir, ".pylintrc")
            if os.path.exists(config_path):
                cmd.extend(["--rcfile", config_path])

        if output_format == "json":
            cmd.extend(["--output-format", "json"])

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

    def run_mypy(
        self,
        target_path: str,
        config_file: Optional[str] = None,
        output_format: str = "json",
    ) -> Dict[str, Any]:
        """
        Run mypy on the target path.

        Args:
            target_path: Path to the Python file or directory to analyze
            config_file: Path to the mypy configuration file
            output_format: Format of the output (json, text)

        Returns:
            Dictionary with mypy analysis results
        """
        if not self._check_tool_available("mypy"):
            return {"error": "mypy not available"}

        cmd = ["mypy", target_path]

        if config_file:
            cmd.extend(["--config-file", config_file])
        elif self.config_dir:
            config_path = os.path.join(self.config_dir, "mypy.ini")
            if os.path.exists(config_path):
                cmd.extend(["--config-file", config_path])

        if output_format == "json":
            cmd.append("--json")

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

    def run_bandit(
        self,
        target_path: str,
        config_file: Optional[str] = None,
        output_format: str = "json",
    ) -> Dict[str, Any]:
        """
        Run bandit on the target path.

        Args:
            target_path: Path to the Python file or directory to analyze
            config_file: Path to the bandit configuration file
            output_format: Format of the output (json, text)

        Returns:
            Dictionary with bandit analysis results
        """
        if not self._check_tool_available("bandit"):
            return {"error": "bandit not available"}

        cmd = ["bandit", "-r", target_path]

        if config_file:
            cmd.extend(["-c", config_file])
        elif self.config_dir:
            config_path = os.path.join(self.config_dir, ".bandit")
            if os.path.exists(config_path):
                cmd.extend(["-c", config_path])

        if output_format == "json":
            cmd.extend(["-f", "json"])

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
            target_path: Path to the Python file or directory to analyze
            output_format: Format of the output (json, text)

        Returns:
            Dictionary with analysis results from all enabled linters
        """
        results = {}

        if self.use_flake8:
            results["flake8"] = self.run_flake8(
                target_path, output_format=output_format
            )

        if self.use_pylint:
            results["pylint"] = self.run_pylint(
                target_path, output_format=output_format
            )

        if self.use_mypy:
            results["mypy"] = self.run_mypy(target_path, output_format=output_format)

        if self.use_bandit:
            results["bandit"] = self.run_bandit(
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
            md_lines = ["# Python Code Analysis Report\n"]

            for tool, tool_results in results.items():
                md_lines.append(f"## {tool.upper()} Results\n")

                if "error" in tool_results:
                    md_lines.append(f"Error: {tool_results['error']}\n")
                    continue

                if tool == "flake8":
                    # Format flake8 results
                    if isinstance(tool_results.get("result"), list):
                        md_lines.append(
                            "| File | Line | Column | Error Code | Message |\n"
                        )
                        md_lines.append(
                            "|------|------|--------|------------|--------|\n"
                        )

                        for issue in tool_results["result"]:
                            md_lines.append(
                                f"| {issue.get('filename', '')} | "
                                f"{issue.get('line_number', '')} | "
                                f"{issue.get('column_number', '')} | "
                                f"{issue.get('code', '')} | "
                                f"{issue.get('text', '')} |\n"
                            )
                    else:
                        md_lines.append(f"```\n{tool_results.get('result', '')}\n```\n")

                elif tool == "pylint":
                    # Format pylint results
                    if isinstance(tool_results.get("result"), list):
                        md_lines.append(
                            "| File | Line | Column | Type | Message | Symbol |\n"
                        )
                        md_lines.append(
                            "|------|------|--------|------|---------|--------|\n"
                        )

                        for issue in tool_results["result"]:
                            md_lines.append(
                                f"| {issue.get('path', '')} | "
                                f"{issue.get('line', '')} | "
                                f"{issue.get('column', '')} | "
                                f"{issue.get('type', '')} | "
                                f"{issue.get('message', '')} | "
                                f"{issue.get('symbol', '')} |\n"
                            )
                    else:
                        md_lines.append(f"```\n{tool_results.get('result', '')}\n```\n")

                elif tool == "mypy":
                    # Format mypy results
                    if isinstance(tool_results.get("result"), list):
                        md_lines.append("| File | Line | Column | Error Message |\n")
                        md_lines.append("|------|------|--------|---------------|\n")

                        for issue in tool_results["result"]:
                            md_lines.append(
                                f"| {issue.get('file', '')} | "
                                f"{issue.get('line', '')} | "
                                f"{issue.get('column', '')} | "
                                f"{issue.get('message', '')} |\n"
                            )
                    else:
                        md_lines.append(f"```\n{tool_results.get('result', '')}\n```\n")

                elif tool == "bandit":
                    # Format bandit results
                    if (
                        isinstance(tool_results.get("result"), dict)
                        and "results" in tool_results["result"]
                    ):
                        md_lines.append(
                            "| File | Line | Severity | Confidence | Issue Type | Description |\n"
                        )
                        md_lines.append(
                            "|------|------|----------|------------|------------|-------------|\n"
                        )

                        for issue in tool_results["result"]["results"]:
                            md_lines.append(
                                f"| {issue.get('filename', '')} | "
                                f"{issue.get('line_number', '')} | "
                                f"{issue.get('issue_severity', '')} | "
                                f"{issue.get('issue_confidence', '')} | "
                                f"{issue.get('issue_text', '')} | "
                                f"{issue.get('test_id', '')} |\n"
                            )
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
                "    <title>Python Code Analysis Report</title>",
                "    <style>",
                "        body { font-family: Arial, sans-serif; margin: 20px; }",
                "        h1 { color: #333; }",
                "        h2 { color: #666; margin-top: 30px; }",
                "        table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }",
                "        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }",
                "        th { background-color: #f2f2f2; }",
                "        tr:nth-child(even) { background-color: #f9f9f9; }",
                "        pre { background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; }",
                "        .error { color: red; }",
                "    </style>",
                "</head>",
                "<body>",
                "    <h1>Python Code Analysis Report</h1>",
            ]

            for tool, tool_results in results.items():
                html_lines.append(f"    <h2>{tool.upper()} Results</h2>")

                if "error" in tool_results:
                    html_lines.append(
                        f"    <p class='error'>Error: {tool_results['error']}</p>"
                    )
                    continue

                if tool == "flake8" and isinstance(tool_results.get("result"), list):
                    html_lines.append("    <table>")
                    html_lines.append(
                        "        <tr><th>File</th><th>Line</th><th>Column</th><th>Error Code</th><th>Message</th></tr>"
                    )

                    for issue in tool_results["result"]:
                        html_lines.append(
                            f"        <tr>"
                            f"<td>{issue.get('filename', '')}</td>"
                            f"<td>{issue.get('line_number', '')}</td>"
                            f"<td>{issue.get('column_number', '')}</td>"
                            f"<td>{issue.get('code', '')}</td>"
                            f"<td>{issue.get('text', '')}</td>"
                            f"</tr>"
                        )

                    html_lines.append("    </table>")
                elif tool == "pylint" and isinstance(tool_results.get("result"), list):
                    html_lines.append("    <table>")
                    html_lines.append(
                        "        <tr><th>File</th><th>Line</th><th>Column</th><th>Type</th><th>Message</th><th>Symbol</th></tr>"
                    )

                    for issue in tool_results["result"]:
                        html_lines.append(
                            f"        <tr>"
                            f"<td>{issue.get('path', '')}</td>"
                            f"<td>{issue.get('line', '')}</td>"
                            f"<td>{issue.get('column', '')}</td>"
                            f"<td>{issue.get('type', '')}</td>"
                            f"<td>{issue.get('message', '')}</td>"
                            f"<td>{issue.get('symbol', '')}</td>"
                            f"</tr>"
                        )

                    html_lines.append("    </table>")
                elif tool == "mypy" and isinstance(tool_results.get("result"), list):
                    html_lines.append("    <table>")
                    html_lines.append(
                        "        <tr><th>File</th><th>Line</th><th>Column</th><th>Error Message</th></tr>"
                    )

                    for issue in tool_results["result"]:
                        html_lines.append(
                            f"        <tr>"
                            f"<td>{issue.get('file', '')}</td>"
                            f"<td>{issue.get('line', '')}</td>"
                            f"<td>{issue.get('column', '')}</td>"
                            f"<td>{issue.get('message', '')}</td>"
                            f"</tr>"
                        )

                    html_lines.append("    </table>")
                elif (
                    tool == "bandit"
                    and isinstance(tool_results.get("result"), dict)
                    and "results" in tool_results["result"]
                ):
                    html_lines.append("    <table>")
                    html_lines.append(
                        "        <tr><th>File</th><th>Line</th><th>Severity</th><th>Confidence</th><th>Issue Type</th><th>Description</th></tr>"
                    )

                    for issue in tool_results["result"]["results"]:
                        html_lines.append(
                            f"        <tr>"
                            f"<td>{issue.get('filename', '')}</td>"
                            f"<td>{issue.get('line_number', '')}</td>"
                            f"<td>{issue.get('issue_severity', '')}</td>"
                            f"<td>{issue.get('issue_confidence', '')}</td>"
                            f"<td>{issue.get('test_id', '')}</td>"
                            f"<td>{issue.get('issue_text', '')}</td>"
                            f"</tr>"
                        )

                    html_lines.append("    </table>")
                else:
                    html_lines.append(
                        f"    <pre>{tool_results.get('result', '')}</pre>"
                    )

            html_lines.extend(["</body>", "</html>"])

            return "\n".join(html_lines)

        else:  # text format
            text_lines = ["Python Code Analysis Report", "=========================\n"]

            for tool, tool_results in results.items():
                text_lines.append(f"{tool.upper()} Results:")
                text_lines.append("-" * (len(tool) + 9) + "\n")

                if "error" in tool_results:
                    text_lines.append(f"Error: {tool_results['error']}\n")
                    continue

                text_lines.append(str(tool_results.get("result", "")))
                text_lines.append("\n")

            return "\n".join(text_lines)


def analyze_python_code(
    target_path: str,
    output_path: Optional[str] = None,
    output_format: str = "markdown",
    use_flake8: bool = True,
    use_pylint: bool = True,
    use_mypy: bool = False,
    use_bandit: bool = False,
    config_dir: Optional[str] = None,
) -> str:
    """
    Analyze Python code using various linting tools.

    Args:
        target_path: Path to the Python file or directory to analyze
        output_path: Path to save the analysis report, if None returns as string
        output_format: Format of the report (text, json, html, markdown)
        use_flake8: Whether to use flake8 for linting
        use_pylint: Whether to use pylint for linting
        use_mypy: Whether to use mypy for type checking
        use_bandit: Whether to use bandit for security analysis
        config_dir: Directory containing configuration files for linters

    Returns:
        Path to the output report file or the report as a string if output_path is None
    """
    console.print(f"Analyzing Python code in [cyan]{target_path}[/cyan]...")

    linter = PythonLinter(
        use_flake8=use_flake8,
        use_pylint=use_pylint,
        use_mypy=use_mypy,
        use_bandit=use_bandit,
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
