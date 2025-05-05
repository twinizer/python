"""
Tests for the Project class in the core.project module.
"""

import os
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from twinizer.core.project import Project


class TestProject(unittest.TestCase):
    """Test cases for the Project class."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_dir = self.temp_dir.name
        self.create_sample_files()
        self.project = Project(self.project_dir)

    def tearDown(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()

    def create_sample_files(self):
        """Create sample files for testing file categorization."""
        os.makedirs(os.path.join(self.project_dir, "hardware"), exist_ok=True)
        os.makedirs(os.path.join(self.project_dir, "firmware"), exist_ok=True)
        os.makedirs(os.path.join(self.project_dir, "docs"), exist_ok=True)
        os.makedirs(os.path.join(self.project_dir, "bin"), exist_ok=True)
        os.makedirs(os.path.join(self.project_dir, "scripts"), exist_ok=True)

        with open(os.path.join(self.project_dir, "hardware", "design.sch"), "w") as f:
            f.write("Sample schematic file")
        with open(
            os.path.join(self.project_dir, "hardware", "board.kicad_pcb"), "w"
        ) as f:
            f.write("Sample PCB file")

        with open(os.path.join(self.project_dir, "firmware", "main.c"), "w") as f:
            f.write("Sample C file")
        with open(os.path.join(self.project_dir, "firmware", "header.h"), "w") as f:
            f.write("Sample header file")

        with open(os.path.join(self.project_dir, "docs", "readme.md"), "w") as f:
            f.write("Sample markdown file")
        with open(os.path.join(self.project_dir, "docs", "manual.pdf"), "w") as f:
            f.write("Sample PDF file")

        with open(os.path.join(self.project_dir, "bin", "firmware.hex"), "w") as f:
            f.write("Sample hex file")
        with open(os.path.join(self.project_dir, "bin", "program.elf"), "w") as f:
            f.write("Sample ELF file")

        with open(os.path.join(self.project_dir, "scripts", "build.sh"), "w") as f:
            f.write("Sample shell script")
        with open(os.path.join(self.project_dir, "scripts", "deploy.py"), "w") as f:
            f.write("Sample Python script")

        with open(os.path.join(self.project_dir, "unknown.xyz"), "w") as f:
            f.write("Sample unknown file")

    def test_init(self):
        """Test Project initialization."""
        project = Project(self.project_dir)
        self.assertEqual(project.source_dir, os.path.abspath(self.project_dir))
        self.assertEqual(project.name, os.path.basename(self.project_dir))
        self.assertEqual(project.hardware_files, [])
        self.assertEqual(project.firmware_files, [])
        self.assertEqual(project.binary_files, [])
        self.assertEqual(project.doc_files, [])
        self.assertEqual(project.script_files, [])
        self.assertEqual(project.other_files, [])

    def test_scan(self):
        """Test scanning project directory."""
        self.project.scan()

        self.assertEqual(len(self.project.hardware_files), 2)
        self.assertTrue(any("design.sch" in f for f in self.project.hardware_files))
        self.assertTrue(
            any("board.kicad_pcb" in f for f in self.project.hardware_files)
        )

        self.assertEqual(len(self.project.firmware_files), 2)
        self.assertTrue(any("main.c" in f for f in self.project.firmware_files))
        self.assertTrue(any("header.h" in f for f in self.project.firmware_files))

        self.assertEqual(len(self.project.doc_files), 2)
        self.assertTrue(any("readme.md" in f for f in self.project.doc_files))
        self.assertTrue(any("manual.pdf" in f for f in self.project.doc_files))

        self.assertEqual(len(self.project.binary_files), 2)
        self.assertTrue(any("firmware.hex" in f for f in self.project.binary_files))
        self.assertTrue(any("program.elf" in f for f in self.project.binary_files))

        self.assertEqual(len(self.project.script_files), 2)
        self.assertTrue(any("build.sh" in f for f in self.project.script_files))
        self.assertTrue(any("deploy.py" in f for f in self.project.script_files))

        self.assertEqual(len(self.project.other_files), 1)
        self.assertTrue(any("unknown.xyz" in f for f in self.project.other_files))

    @patch("rich.console.Console.print")
    def test_show_info(self, mock_print):
        """Test displaying project information."""
        self.project.scan()
        self.project.show_info()
        mock_print.assert_called()

    @patch("rich.console.Console.print")
    def test_analyze_structure(self, mock_print):
        """Test analyzing project structure."""
        self.project.scan()
        self.project.analyze_structure()
        mock_print.assert_called()

    @patch("rich.console.Console.print")
    def test_analyze_hardware(self, mock_print):
        """Test analyzing hardware files."""
        self.project.scan()
        self.project.analyze_hardware()
        mock_print.assert_called()

    @patch("rich.console.Console.print")
    def test_analyze_firmware(self, mock_print):
        """Test analyzing firmware files."""
        self.project.scan()
        self.project.analyze_firmware()
        mock_print.assert_called()

    @patch("rich.console.Console.print")
    def test_analyze_binary(self, mock_print):
        """Test analyzing binary files."""
        self.project.scan()

        with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as temp_file:
            temp_file.write(b"\x7FELF\x01\x01\x01\x00")  # Mock ELF header
            binary_file = temp_file.name

        try:
            with patch(
                "twinizer.software.analyze.binary.BinaryAnalyzer.analyze",
                return_value={"format": "ELF", "size": 8},
            ):
                result = self.project.analyze_binary(binary_file)
                self.assertIsInstance(result, dict)
                self.assertIn("format", result)
                mock_print.assert_called()
        finally:
            if os.path.exists(binary_file):
                os.unlink(binary_file)

    @patch("rich.console.Console.print")
    def test_analyze_documentation(self, mock_print):
        """Test analyzing documentation files."""
        self.project.scan()
        self.project.analyze_documentation()
        mock_print.assert_called()

    @patch("rich.console.Console.print")
    def test_analyze_scripts(self, mock_print):
        """Test analyzing script files."""
        self.project.scan()
        self.project.analyze_scripts()
        mock_print.assert_called()

    def test_export_project(self):
        """Test exporting project to a ZIP file."""
        self.project.scan()

        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_file:
            zip_path = temp_file.name

        try:
            self.project.export_project(zip_path)
            self.assertTrue(os.path.exists(zip_path))

            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                file_list = zip_ref.namelist()
                self.assertIn("hardware/design.sch", file_list)
                self.assertIn("firmware/main.c", file_list)
                self.assertIn("docs/readme.md", file_list)
        finally:
            if os.path.exists(zip_path):
                os.unlink(zip_path)

    def test_import_project(self):
        """Test importing project from a ZIP file."""
        self.project.scan()

        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_file:
            zip_path = temp_file.name

        try:
            self.project.export_project(zip_path)

            with tempfile.TemporaryDirectory() as import_dir:
                imported_project = Project.import_project(zip_path, import_dir)
                imported_project.scan()
                self.assertEqual(len(imported_project.hardware_files), 2)
                self.assertEqual(len(imported_project.firmware_files), 2)
                self.assertEqual(len(imported_project.doc_files), 2)
        finally:
            if os.path.exists(zip_path):
                os.unlink(zip_path)


if __name__ == "__main__":
    unittest.main()
