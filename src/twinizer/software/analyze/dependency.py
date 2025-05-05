"""
Dependency analyzer module.

This module provides functionality to analyze dependencies in software projects
across various languages and build systems.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

from rich.console import Console
from rich.tree import Tree

console = Console()


class DependencyAnalyzer:
    """
    Analyzer for software project dependencies.
    """

    def __init__(self, project_path: str):
        """
        Initialize the dependency analyzer.

        Args:
            project_path: Path to the project to analyze
        """
        self.project_path = os.path.abspath(project_path)
        if not os.path.exists(self.project_path):
            raise FileNotFoundError(f"Project path not found: {self.project_path}")

        self.language = self._detect_language()
        self.build_system = self._detect_build_system()

    def _detect_language(self) -> str:
        """
        Detect the primary programming language of the project.

        Returns:
            Detected programming language
        """
        # Count files by extension
        extensions = {}
        for root, _, files in os.walk(self.project_path):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext:
                    extensions[ext] = extensions.get(ext, 0) + 1

        # Map extensions to languages
        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".c": "c",
            ".cpp": "cpp",
            ".h": "c/cpp",
            ".hpp": "cpp",
            ".cs": "csharp",
            ".go": "go",
            ".rb": "ruby",
            ".php": "php",
            ".rs": "rust",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
        }

        # Determine primary language
        primary_language = "unknown"
        max_count = 0

        for ext, count in extensions.items():
            if ext in language_map and count > max_count:
                primary_language = language_map[ext]
                max_count = count

        return primary_language

    def _detect_build_system(self) -> str:
        """
        Detect the build system used by the project.

        Returns:
            Detected build system
        """
        # Check for common build files
        build_files = {
            "setup.py": "setuptools",
            "pyproject.toml": "poetry/pep517",
            "requirements.txt": "pip",
            "Pipfile": "pipenv",
            "package.json": "npm",
            "build.gradle": "gradle",
            "pom.xml": "maven",
            "Makefile": "make",
            "CMakeLists.txt": "cmake",
            "Cargo.toml": "cargo",
            "go.mod": "go",
            "Gemfile": "bundler",
            "composer.json": "composer",
        }

        for file, system in build_files.items():
            if os.path.exists(os.path.join(self.project_path, file)):
                return system

        return "unknown"

    def analyze(self) -> Dict:
        """
        Analyze the project dependencies.

        Returns:
            Dictionary with dependency information
        """
        result = {
            "project_path": self.project_path,
            "language": self.language,
            "build_system": self.build_system,
            "dependencies": {},
            "dependency_graph": {},
        }

        # Call appropriate analyzer based on language/build system
        if self.language == "python":
            if self.build_system == "setuptools":
                result.update(self._analyze_python_setuptools())
            elif self.build_system == "poetry/pep517":
                result.update(self._analyze_python_poetry())
            elif self.build_system == "pip":
                result.update(self._analyze_python_requirements())
            elif self.build_system == "pipenv":
                result.update(self._analyze_python_pipenv())
        elif self.language in ["javascript", "typescript"]:
            if self.build_system == "npm":
                result.update(self._analyze_npm())
        elif self.language in ["java"]:
            if self.build_system == "maven":
                result.update(self._analyze_maven())
            elif self.build_system == "gradle":
                result.update(self._analyze_gradle())
        elif self.language in ["c", "cpp", "c/cpp"]:
            if self.build_system == "make":
                result.update(self._analyze_make())
            elif self.build_system == "cmake":
                result.update(self._analyze_cmake())

        return result

    def _analyze_python_setuptools(self) -> Dict:
        """Analyze Python project using setuptools."""
        result = {"dependencies": {}, "dependency_graph": {}}
        setup_py = os.path.join(self.project_path, "setup.py")

        try:
            # Extract install_requires using a temporary script
            temp_script = os.path.join(self.project_path, "_temp_extract_deps.py")
            with open(temp_script, "w") as f:
                f.write(
                    """
import ast
import json
import sys

def extract_setup_args(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    tree = ast.parse(content)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node, 'func', None) is not None:
            func_name = getattr(node.func, 'id', '')
            if func_name == 'setup':
                for kw in node.keywords:
                    if kw.arg == 'install_requires':
                        if isinstance(kw.value, ast.List):
                            deps = [elt.s for elt in kw.value.elts if isinstance(elt, ast.Str)]
                            return deps
    return []

if __name__ == '__main__':
    deps = extract_setup_args(sys.argv[1])
    print(json.dumps(deps))
                """
                )

            # Run the script to extract dependencies
            output = subprocess.check_output(
                [sys.executable, temp_script, setup_py], text=True
            )
            os.remove(temp_script)

            # Parse dependencies
            dependencies = json.loads(output.strip())
            for dep in dependencies:
                name = (
                    dep.split(">=")[0]
                    .split("==")[0]
                    .split(">")[0]
                    .split("<")[0]
                    .strip()
                )
                result["dependencies"][name] = dep
                result["dependency_graph"][name] = []

        except Exception as e:
            console.print(f"[yellow]Warning: Error analyzing setup.py: {e}[/yellow]")

        return result

    def _analyze_python_poetry(self) -> Dict:
        """Analyze Python project using Poetry."""
        result = {"dependencies": {}, "dependency_graph": {}}
        pyproject_toml = os.path.join(self.project_path, "pyproject.toml")

        try:
            # Try to use toml package if available
            try:
                import toml

                with open(pyproject_toml, "r") as f:
                    data = toml.load(f)

                # Extract dependencies
                deps = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
                for name, version in deps.items():
                    if name != "python":  # Skip Python version constraint
                        if isinstance(version, str):
                            result["dependencies"][name] = version
                        else:
                            result["dependencies"][name] = str(version)
                        result["dependency_graph"][name] = []

                # Extract dev dependencies
                dev_deps = (
                    data.get("tool", {}).get("poetry", {}).get("dev-dependencies", {})
                )
                for name, version in dev_deps.items():
                    if isinstance(version, str):
                        result["dependencies"][name] = f"{version} (dev)"
                    else:
                        result["dependencies"][name] = f"{str(version)} (dev)"
                    result["dependency_graph"][name] = []

            except ImportError:
                # Fallback to parsing the file manually
                with open(pyproject_toml, "r") as f:
                    content = f.read()

                # Very basic parsing - would be better with a proper TOML parser
                in_deps_section = False
                in_dev_deps_section = False

                for line in content.split("\n"):
                    line = line.strip()
                    if line == "[tool.poetry.dependencies]":
                        in_deps_section = True
                        in_dev_deps_section = False
                        continue
                    elif line == "[tool.poetry.dev-dependencies]":
                        in_deps_section = False
                        in_dev_deps_section = True
                        continue
                    elif line.startswith("[") and line.endswith("]"):
                        in_deps_section = False
                        in_dev_deps_section = False
                        continue

                    if (in_deps_section or in_dev_deps_section) and "=" in line:
                        parts = line.split("=", 1)
                        name = parts[0].strip()
                        if name != "python":  # Skip Python version constraint
                            version = parts[1].strip().strip("\"'")
                            if in_dev_deps_section:
                                version += " (dev)"
                            result["dependencies"][name] = version
                            result["dependency_graph"][name] = []

        except Exception as e:
            console.print(
                f"[yellow]Warning: Error analyzing pyproject.toml: {e}[/yellow]"
            )

        return result

    def _analyze_python_requirements(self) -> Dict:
        """Analyze Python project using requirements.txt."""
        result = {"dependencies": {}, "dependency_graph": {}}
        req_file = os.path.join(self.project_path, "requirements.txt")

        try:
            with open(req_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        # Handle line continuations and comments
                        if line.endswith("\\"):
                            line = line[:-1].strip()

                        # Skip options and editable installs for simplicity
                        if (
                            line.startswith("-e ")
                            or line.startswith("-r ")
                            or line.startswith("-")
                        ):
                            continue

                        # Extract package name
                        name = (
                            line.split(">=")[0]
                            .split("==")[0]
                            .split(">")[0]
                            .split("<")[0]
                            .strip()
                        )
                        result["dependencies"][name] = line
                        result["dependency_graph"][name] = []

        except Exception as e:
            console.print(
                f"[yellow]Warning: Error analyzing requirements.txt: {e}[/yellow]"
            )

        return result

    def _analyze_python_pipenv(self) -> Dict:
        """Analyze Python project using Pipenv."""
        result = {"dependencies": {}, "dependency_graph": {}}
        pipfile = os.path.join(self.project_path, "Pipfile")
        pipfile_lock = os.path.join(self.project_path, "Pipfile.lock")

        try:
            # Try to use the lock file first (more accurate)
            if os.path.exists(pipfile_lock):
                with open(pipfile_lock, "r") as f:
                    data = json.load(f)

                # Extract default dependencies
                for name, info in data.get("default", {}).items():
                    version = info.get("version", "")
                    result["dependencies"][name] = version
                    result["dependency_graph"][name] = []

                # Extract dev dependencies
                for name, info in data.get("develop", {}).items():
                    version = info.get("version", "")
                    result["dependencies"][name] = f"{version} (dev)"
                    result["dependency_graph"][name] = []

            # Fallback to Pipfile if lock doesn't exist
            elif os.path.exists(pipfile):
                # Very basic parsing - would be better with a proper TOML parser
                with open(pipfile, "r") as f:
                    content = f.read()

                in_packages_section = False
                in_dev_packages_section = False

                for line in content.split("\n"):
                    line = line.strip()
                    if line == "[packages]":
                        in_packages_section = True
                        in_dev_packages_section = False
                        continue
                    elif line == "[dev-packages]":
                        in_packages_section = False
                        in_dev_packages_section = True
                        continue
                    elif line.startswith("[") and line.endswith("]"):
                        in_packages_section = False
                        in_dev_packages_section = False
                        continue

                    if (in_packages_section or in_dev_packages_section) and "=" in line:
                        parts = line.split("=", 1)
                        name = parts[0].strip()
                        version = parts[1].strip().strip("\"'")
                        if in_dev_packages_section:
                            version += " (dev)"
                        result["dependencies"][name] = version
                        result["dependency_graph"][name] = []

        except Exception as e:
            console.print(
                f"[yellow]Warning: Error analyzing Pipfile/Pipfile.lock: {e}[/yellow]"
            )

        return result

    def _analyze_npm(self) -> Dict:
        """Analyze JavaScript/TypeScript project using npm."""
        result = {"dependencies": {}, "dependency_graph": {}}
        package_json = os.path.join(self.project_path, "package.json")

        try:
            with open(package_json, "r") as f:
                data = json.load(f)

            # Extract dependencies
            for name, version in data.get("dependencies", {}).items():
                result["dependencies"][name] = version
                result["dependency_graph"][name] = []

            # Extract dev dependencies
            for name, version in data.get("devDependencies", {}).items():
                result["dependencies"][name] = f"{version} (dev)"
                result["dependency_graph"][name] = []

            # Extract peer dependencies
            for name, version in data.get("peerDependencies", {}).items():
                result["dependencies"][name] = f"{version} (peer)"
                result["dependency_graph"][name] = []

            # Check for package-lock.json or yarn.lock for more detailed dependency info
            package_lock = os.path.join(self.project_path, "package-lock.json")
            yarn_lock = os.path.join(self.project_path, "yarn.lock")

            if os.path.exists(package_lock):
                result["lock_file"] = "package-lock.json"
            elif os.path.exists(yarn_lock):
                result["lock_file"] = "yarn.lock"
            else:
                result["lock_file"] = None

        except Exception as e:
            console.print(
                f"[yellow]Warning: Error analyzing package.json: {e}[/yellow]"
            )

        return result

    def _analyze_maven(self) -> Dict:
        """Analyze Java project using Maven."""
        result = {"dependencies": {}, "dependency_graph": {}}
        pom_xml = os.path.join(self.project_path, "pom.xml")

        try:
            # This is a very basic XML parsing approach
            # For a real implementation, use a proper XML parser like ElementTree
            with open(pom_xml, "r") as f:
                content = f.read()

            # Very basic parsing for dependencies
            import re

            deps = re.findall(
                r"<dependency>.*?<groupId>(.*?)</groupId>.*?<artifactId>(.*?)</artifactId>.*?<version>(.*?)</version>.*?</dependency>",
                content,
                re.DOTALL,
            )

            for group_id, artifact_id, version in deps:
                name = f"{group_id}:{artifact_id}"
                result["dependencies"][name] = version
                result["dependency_graph"][name] = []

        except Exception as e:
            console.print(f"[yellow]Warning: Error analyzing pom.xml: {e}[/yellow]")

        return result

    def _analyze_gradle(self) -> Dict:
        """Analyze Java project using Gradle."""
        result = {"dependencies": {}, "dependency_graph": {}}
        build_gradle = os.path.join(self.project_path, "build.gradle")

        try:
            # This is a very basic parsing approach
            # For a real implementation, use a proper Gradle parser
            with open(build_gradle, "r") as f:
                content = f.read()

            # Very basic parsing for dependencies
            import re

            deps = re.findall(
                r'(implementation|testImplementation|api|compileOnly|runtimeOnly)\s*[\'\"]([^\'"]+)[\'\"]',
                content,
            )

            for dep_type, dep in deps:
                parts = dep.split(":")
                if len(parts) >= 2:
                    group_id = parts[0]
                    artifact_id = parts[1]
                    version = parts[2] if len(parts) > 2 else "unknown"

                    name = f"{group_id}:{artifact_id}"
                    result["dependencies"][name] = f"{version} ({dep_type})"
                    result["dependency_graph"][name] = []

        except Exception as e:
            console.print(
                f"[yellow]Warning: Error analyzing build.gradle: {e}[/yellow]"
            )

        return result

    def _analyze_make(self) -> Dict:
        """Analyze C/C++ project using Make."""
        result = {"dependencies": {}, "dependency_graph": {}}
        makefile = os.path.join(self.project_path, "Makefile")

        try:
            # This is a very basic parsing approach
            # For a real implementation, use a proper Makefile parser
            with open(makefile, "r") as f:
                content = f.read()

            # Look for libraries in LDLIBS, LDFLAGS, etc.
            import re

            libs = re.findall(r"-l([a-zA-Z0-9_]+)", content)

            for lib in libs:
                result["dependencies"][lib] = "system library"
                result["dependency_graph"][lib] = []

            # Look for includes
            includes = re.findall(r'#include\s*[<"]([^>"]+)[>"]', content)
            for include in includes:
                result["dependencies"][include] = "header"
                result["dependency_graph"][include] = []

        except Exception as e:
            console.print(f"[yellow]Warning: Error analyzing Makefile: {e}[/yellow]")

        return result

    def _analyze_cmake(self) -> Dict:
        """Analyze C/C++ project using CMake."""
        result = {"dependencies": {}, "dependency_graph": {}}
        cmake_file = os.path.join(self.project_path, "CMakeLists.txt")

        try:
            # This is a very basic parsing approach
            # For a real implementation, use a proper CMake parser
            with open(cmake_file, "r") as f:
                content = f.read()

            # Look for find_package calls
            import re

            packages = re.findall(r"find_package\s*\(\s*([a-zA-Z0-9_]+)", content)

            for package in packages:
                result["dependencies"][package] = "CMake package"
                result["dependency_graph"][package] = []

            # Look for target_link_libraries calls
            links = re.findall(
                r"target_link_libraries\s*\(\s*[a-zA-Z0-9_]+\s+([^)]+)\)", content
            )
            for link_str in links:
                for lib in link_str.split():
                    lib = lib.strip()
                    if lib and not lib.startswith("$"):
                        result["dependencies"][lib] = "linked library"
                        result["dependency_graph"][lib] = []

        except Exception as e:
            console.print(
                f"[yellow]Warning: Error analyzing CMakeLists.txt: {e}[/yellow]"
            )

        return result

    def visualize(self) -> None:
        """
        Visualize the dependency analysis results.
        """
        analysis = self.analyze()

        console.print(f"[bold green]Project Analysis: {self.project_path}[/bold green]")
        console.print(f"[bold]Language:[/bold] {analysis['language']}")
        console.print(f"[bold]Build System:[/bold] {analysis['build_system']}")

        # Create a tree of dependencies
        tree = Tree("[bold]Dependencies[/bold]")

        # Sort dependencies by name
        sorted_deps = sorted(analysis["dependencies"].items())

        for name, version in sorted_deps:
            tree.add(f"[cyan]{name}[/cyan]: {version}")

        console.print(tree)


def analyze_dependencies(project_path: str) -> Dict:
    """
    Analyze dependencies in a software project.

    Args:
        project_path: Path to the project to analyze

    Returns:
        Dictionary with dependency information
    """
    analyzer = DependencyAnalyzer(project_path)
    return analyzer.analyze()


def visualize_dependencies(project_path: str) -> None:
    """
    Visualize dependencies in a software project.

    Args:
        project_path: Path to the project to analyze
    """
    analyzer = DependencyAnalyzer(project_path)
    analyzer.visualize()
