"""
C/C++ linters integration module.

This module provides integration with popular C/C++ linting tools such as
cppcheck, clang-tidy, and cpplint to analyze C/C++ code quality and detect potential issues.
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


class CPPLinter:
    """
    C/C++ code linter that integrates with various C/C++ linting tools.
    """

    def __init__(
        self,
        use_cppcheck: bool = True,
        use_clang_tidy: bool = False,
        use_cpplint: bool = False,
        config_dir: Optional[str] = None,
    ):
        """
        Initialize the C/C++ linter.

        Args:
            use_cppcheck: Whether to use cppcheck for linting
            use_clang_tidy: Whether to use clang-tidy for linting
            use_cpplint: Whether to use cpplint for linting
            config_dir: Directory containing configuration files for linters
        """
        self.use_cppcheck = use_cppcheck
        self.use_clang_tidy = use_clang_tidy
        self.use_cpplint = use_cpplint
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

    def run_cppcheck(
        self,
        target_path: str,
        config_file: Optional[str] = None,
        output_format: str = "json",
    ) -> Dict[str, Any]:
        """
        Run cppcheck on the target path.

        Args:
            target_path: Path to the C/C++ file or directory to analyze
            config_file: Path to the cppcheck configuration file
            output_format: Format of the output (json, xml, text)

        Returns:
            Dictionary with cppcheck analysis results
        """
        if not self._check_tool_available("cppcheck"):
            return {"error": "cppcheck not available"}

        cmd = ["cppcheck", "--enable=all", "--inconclusive", "--force", target_path]

        if config_file:
            cmd.extend(["--suppressions-list", config_file])
        elif self.config_dir:
            config_path = os.path.join(self.config_dir, "cppcheck.suppress")
            if os.path.exists(config_path):
                cmd.extend(["--suppressions-list", config_path])

        if output_format == "json":
            # cppcheck doesn't have direct JSON output, use XML and convert
            with tempfile.NamedTemporaryFile(suffix=".xml") as temp_file:
                xml_cmd = cmd + ["--xml", "--output-file=" + temp_file.name]

                try:
                    subprocess.run(
                        xml_cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        check=False,
                    )

                    # Convert XML to JSON (simplified)
                    import xml.etree.ElementTree as ET

                    tree = ET.parse(temp_file.name)
                    root = tree.getroot()

                    errors = []
                    for error in root.findall(".//error"):
                        error_data = {
                            "id": error.get("id"),
                            "severity": error.get("severity"),
                            "msg": error.get("msg"),
                            "verbose": error.get("verbose"),
                        }

                        # Get location information
                        location = error.find("location")
                        if location is not None:
                            error_data["file"] = location.get("file")
                            error_data["line"] = location.get("line")

                        errors.append(error_data)

                    return {"result": errors, "errors": ""}
                except Exception as e:
                    return {"error": str(e)}

        elif output_format == "xml":
            with tempfile.NamedTemporaryFile(suffix=".xml") as temp_file:
                xml_cmd = cmd + ["--xml", "--output-file=" + temp_file.name]

                try:
                    subprocess.run(
                        xml_cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        check=False,
                    )

                    with open(temp_file.name, "r") as f:
                        xml_content = f.read()

                    return {"result": xml_content, "errors": ""}
                except Exception as e:
                    return {"error": str(e)}

        else:  # text format
            try:
                result = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False,
                )

                # cppcheck outputs to stderr
                return {"result": result.stderr, "errors": ""}
            except Exception as e:
                return {"error": str(e)}

    def run_clang_tidy(
        self,
        target_path: str,
        config_file: Optional[str] = None,
        output_format: str = "json",
    ) -> Dict[str, Any]:
        """
        Run clang-tidy on the target path.

        Args:
            target_path: Path to the C/C++ file to analyze
            config_file: Path to the clang-tidy configuration file
            output_format: Format of the output (json, yaml, text)

        Returns:
            Dictionary with clang-tidy analysis results
        """
        if not self._check_tool_available("clang-tidy"):
            return {"error": "clang-tidy not available"}

        cmd = ["clang-tidy", target_path]

        if config_file:
            cmd.extend(["-config-file", config_file])
        elif self.config_dir:
            config_path = os.path.join(self.config_dir, ".clang-tidy")
            if os.path.exists(config_path):
                cmd.extend(["-config-file", config_path])

        # clang-tidy doesn't have direct JSON output, use YAML and convert if needed
        if output_format == "json" or output_format == "yaml":
            cmd.extend(["-export-fixes", "-"])

            try:
                result = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False,
                )

                if output_format == "json":
                    # Convert YAML to JSON
                    import yaml

                    try:
                        yaml_data = yaml.safe_load(result.stdout)
                        return {"result": yaml_data, "errors": result.stderr}
                    except yaml.YAMLError:
                        return {"result": result.stdout, "errors": result.stderr}
                else:
                    return {"result": result.stdout, "errors": result.stderr}
            except Exception as e:
                return {"error": str(e)}

        else:  # text format
            try:
                result = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False,
                )

                return {"result": result.stdout, "errors": result.stderr}
            except Exception as e:
                return {"error": str(e)}

    def run_cpplint(
        self,
        target_path: str,
        config_file: Optional[str] = None,
        output_format: str = "json",
    ) -> Dict[str, Any]:
        """
        Run cpplint on the target path.

        Args:
            target_path: Path to the C/C++ file or directory to analyze
            config_file: Path to the cpplint configuration file
            output_format: Format of the output (json, text)

        Returns:
            Dictionary with cpplint analysis results
        """
        if not self._check_tool_available("cpplint"):
            return {"error": "cpplint not available"}

        cmd = ["cpplint", target_path]

        if config_file:
            cmd.extend(["--config", config_file])

        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )

            # cpplint outputs to stderr
            output = result.stderr

            if output_format == "json":
                # Parse cpplint output to JSON format
                issues = []
                for line in output.splitlines():
                    if ":" in line:
                        parts = line.split(":", 4)
                        if len(parts) >= 4:
                            file_path = parts[0]
                            line_num = parts[1]
                            column = parts[2] if len(parts) > 3 else ""
                            message = parts[3] if len(parts) > 3 else ""

                            issues.append(
                                {
                                    "file": file_path,
                                    "line": line_num,
                                    "column": column,
                                    "message": message.strip(),
                                }
                            )

                return {"result": issues, "errors": ""}
            else:
                return {"result": output, "errors": ""}
        except Exception as e:
            return {"error": str(e)}

    def analyze(self, target_path: str, output_format: str = "json") -> Dict[str, Any]:
        """
        Run all enabled linters on the target path.

        Args:
            target_path: Path to the C/C++ file or directory to analyze
            output_format: Format of the output (json, text)

        Returns:
            Dictionary with analysis results from all enabled linters
        """
        results = {}

        if self.use_cppcheck:
            results["cppcheck"] = self.run_cppcheck(
                target_path, output_format=output_format
            )

        if self.use_clang_tidy:
            # clang-tidy works on individual files, not directories
            if os.path.isdir(target_path):
                clang_tidy_results = []
                for root, _, files in os.walk(target_path):
                    for file in files:
                        if file.endswith(
                            (".c", ".cpp", ".cc", ".cxx", ".h", ".hpp", ".hxx")
                        ):
                            file_path = os.path.join(root, file)
                            result = self.run_clang_tidy(
                                file_path, output_format=output_format
                            )
                            clang_tidy_results.append(
                                {"file": file_path, "result": result}
                            )
                results["clang_tidy"] = {"result": clang_tidy_results, "errors": ""}
            else:
                results["clang_tidy"] = self.run_clang_tidy(
                    target_path, output_format=output_format
                )

        if self.use_cpplint:
            results["cpplint"] = self.run_cpplint(
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
            md_lines = ["# C/C++ Code Analysis Report\n"]

            for tool, tool_results in results.items():
                md_lines.append(f"## {tool.upper()} Results\n")

                if "error" in tool_results:
                    md_lines.append(f"Error: {tool_results['error']}\n")
                    continue

                if tool == "cppcheck":
                    # Format cppcheck results
                    if isinstance(tool_results.get("result"), list):
                        md_lines.append("| File | Line | Severity | Message |\n")
                        md_lines.append("|------|------|----------|--------|\n")

                        for issue in tool_results["result"]:
                            md_lines.append(
                                f"| {issue.get('file', '')} | "
                                f"{issue.get('line', '')} | "
                                f"{issue.get('severity', '')} | "
                                f"{issue.get('msg', '')} |\n"
                            )
                    else:
                        md_lines.append(f"```\n{tool_results.get('result', '')}\n```\n")

                elif tool == "clang_tidy":
                    # Format clang-tidy results
                    if isinstance(tool_results.get("result"), list):
                        for file_result in tool_results["result"]:
                            md_lines.append(f"### {file_result.get('file', '')}\n")

                            file_issues = file_result.get("result", {}).get(
                                "result", {}
                            )
                            if (
                                isinstance(file_issues, dict)
                                and "Diagnostics" in file_issues
                            ):
                                md_lines.append(
                                    "| Line | Column | Severity | Message |\n"
                                )
                                md_lines.append(
                                    "|------|--------|----------|--------|\n"
                                )

                                for issue in file_issues["Diagnostics"]:
                                    md_lines.append(
                                        f"| {issue.get('Location', {}).get('Line', '')} | "
                                        f"{issue.get('Location', {}).get('Column', '')} | "
                                        f"{issue.get('Level', '')} | "
                                        f"{issue.get('Message', '')} |\n"
                                    )
                            else:
                                md_lines.append(f"```\n{file_issues}\n```\n")
                    else:
                        md_lines.append(f"```\n{tool_results.get('result', '')}\n```\n")

                elif tool == "cpplint":
                    # Format cpplint results
                    if isinstance(tool_results.get("result"), list):
                        md_lines.append("| File | Line | Column | Message |\n")
                        md_lines.append("|------|------|--------|--------|\n")

                        for issue in tool_results["result"]:
                            md_lines.append(
                                f"| {issue.get('file', '')} | "
                                f"{issue.get('line', '')} | "
                                f"{issue.get('column', '')} | "
                                f"{issue.get('message', '')} |\n"
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
                "    <title>C/C++ Code Analysis Report</title>",
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
                "    </style>",
                "</head>",
                "<body>",
                "    <h1>C/C++ Code Analysis Report</h1>",
            ]

            for tool, tool_results in results.items():
                html_lines.append(f"    <h2>{tool.upper()} Results</h2>")

                if "error" in tool_results:
                    html_lines.append(
                        f"    <p class='error'>Error: {tool_results['error']}</p>"
                    )
                    continue

                if tool == "cppcheck" and isinstance(tool_results.get("result"), list):
                    html_lines.append("    <table>")
                    html_lines.append(
                        "        <tr><th>File</th><th>Line</th><th>Severity</th><th>Message</th></tr>"
                    )

                    for issue in tool_results["result"]:
                        html_lines.append(
                            f"        <tr>"
                            f"<td>{issue.get('file', '')}</td>"
                            f"<td>{issue.get('line', '')}</td>"
                            f"<td>{issue.get('severity', '')}</td>"
                            f"<td>{issue.get('msg', '')}</td>"
                            f"</tr>"
                        )

                    html_lines.append("    </table>")
                elif tool == "clang_tidy" and isinstance(
                    tool_results.get("result"), list
                ):
                    for file_result in tool_results["result"]:
                        html_lines.append(f"    <h3>{file_result.get('file', '')}</h3>")

                        file_issues = file_result.get("result", {}).get("result", {})
                        if (
                            isinstance(file_issues, dict)
                            and "Diagnostics" in file_issues
                        ):
                            html_lines.append("    <table>")
                            html_lines.append(
                                "        <tr><th>Line</th><th>Column</th><th>Severity</th><th>Message</th></tr>"
                            )

                            for issue in file_issues["Diagnostics"]:
                                html_lines.append(
                                    f"        <tr>"
                                    f"<td>{issue.get('Location', {}).get('Line', '')}</td>"
                                    f"<td>{issue.get('Location', {}).get('Column', '')}</td>"
                                    f"<td>{issue.get('Level', '')}</td>"
                                    f"<td>{issue.get('Message', '')}</td>"
                                    f"</tr>"
                                )

                            html_lines.append("    </table>")
                        else:
                            html_lines.append(f"    <pre>{file_issues}</pre>")
                elif tool == "cpplint" and isinstance(tool_results.get("result"), list):
                    html_lines.append("    <table>")
                    html_lines.append(
                        "        <tr><th>File</th><th>Line</th><th>Column</th><th>Message</th></tr>"
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
                else:
                    html_lines.append(
                        f"    <pre>{tool_results.get('result', '')}</pre>"
                    )

            html_lines.extend(["</body>", "</html>"])

            return "\n".join(html_lines)

        else:  # text format
            text_lines = ["C/C++ Code Analysis Report", "=========================\n"]

            for tool, tool_results in results.items():
                text_lines.append(f"{tool.upper()} Results:")
                text_lines.append("-" * (len(tool) + 9) + "\n")

                if "error" in tool_results:
                    text_lines.append(f"Error: {tool_results['error']}\n")
                    continue

                text_lines.append(str(tool_results.get("result", "")))
                text_lines.append("\n")

            return "\n".join(text_lines)


def analyze_cpp_code(
    target_path: str,
    output_path: Optional[str] = None,
    output_format: str = "markdown",
    use_cppcheck: bool = True,
    use_clang_tidy: bool = False,
    use_cpplint: bool = False,
    config_dir: Optional[str] = None,
) -> str:
    """
    Analyze C/C++ code using various linting tools.

    Args:
        target_path: Path to the C/C++ file or directory to analyze
        output_path: Path to save the analysis report, if None returns as string
        output_format: Format of the report (text, json, html, markdown)
        use_cppcheck: Whether to use cppcheck for linting
        use_clang_tidy: Whether to use clang-tidy for linting
        use_cpplint: Whether to use cpplint for linting
        config_dir: Directory containing configuration files for linters

    Returns:
        Path to the output report file or the report as a string if output_path is None
    """
    console.print(f"Analyzing C/C++ code in [cyan]{target_path}[/cyan]...")

    linter = CPPLinter(
        use_cppcheck=use_cppcheck,
        use_clang_tidy=use_clang_tidy,
        use_cpplint=use_cpplint,
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
