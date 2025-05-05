"""
Tests for the Project class in the core.project module.
"""

import os
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from twinizer.core.project import Project


class TestProject(unittest.TestCase):
    """Test cases for the Project class."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_dir = self.temp_dir.name
        
        # Create sample files for testing
        self.create_sample_files()
        
        # Initialize project with the test directory
        self.project = Project(self.project_dir)

    def tearDown(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()

    def create_sample_files(self):
        """Create sample files for testing file categorization."""
        # Create directory structure
        os.makedirs(os.path.join(self.project_dir, "hardware"), exist_ok=True)
        os.makedirs(os.path.join(self.project_dir, "firmware"), exist_ok=True)
        os.makedirs(os.path.join(self.project_dir, "docs"), exist_ok=True)
        os.makedirs(os.path.join(self.project_dir, "bin"), exist_ok=True)
        os.makedirs(os.path.join(self.project_dir, "scripts"), exist_ok=True)
        
        # Create sample hardware files
        with open(os.path.join(self.project_dir, "hardware", "design.sch"), "w") as f:
            f.write("Sample schematic file")
        with open(os.path.join(self.project_dir, "hardware", "board.kicad_pcb"), "w") as f:
            f.write("Sample PCB file")
            
        # Create sample firmware files
        with open(os.path.join(self.project_dir, "firmware", "main.c"), "w") as f:
            f.write("Sample C file")
        with open(os.path.join(self.project_dir, "firmware", "header.h"), "w") as f:
            f.write("Sample header file")
            
        # Create sample documentation files
        with open(os.path.join(self.project_dir, "docs", "readme.md"), "w") as f:
            f.write("Sample markdown file")
        with open(os.path.join(self.project_dir, "docs", "manual.pdf"), "w") as f:
            f.write("Sample PDF file")
            
        # Create sample binary files
        with open(os.path.join(self.project_dir, "bin", "firmware.hex"), "w") as f:
            f.write("Sample hex file")
        with open(os.path.join(self.project_dir, "bin", "program.elf"), "w") as f:
            f.write("Sample ELF file")
            
        # Create sample script files
        with open(os.path.join(self.project_dir, "scripts", "build.sh"), "w") as f:
            f.write("Sample shell script")
        with open(os.path.join(self.project_dir, "scripts", "deploy.py"), "w") as f:
            f.write("Sample Python script")
            
        # Create sample other file
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
        
        # Verify hardware files were detected
        self.assertEqual(len(self.project.hardware_files), 2)
        self.assertTrue(any("design.sch" in f for f in self.project.hardware_files))
        self.assertTrue(any("board.kicad_pcb" in f for f in self.project.hardware_files))
        
        # Verify firmware files were detected
        self.assertEqual(len(self.project.firmware_files), 2)
        self.assertTrue(any("main.c" in f for f in self.project.firmware_files))
        self.assertTrue(any("header.h" in f for f in self.project.firmware_files))
        
        # Verify documentation files were detected
        self.assertEqual(len(self.project.doc_files), 2)
        self.assertTrue(any("readme.md" in f for f in self.project.doc_files))
        self.assertTrue(any("manual.pdf" in f for f in self.project.doc_files))
        
        # Verify binary files were detected
        self.assertEqual(len(self.project.binary_files), 2)
        self.assertTrue(any("firmware.hex" in f for f in self.project.binary_files))
        self.assertTrue(any("program.elf" in f for f in self.project.binary_files))
        
        # Verify script files were detected
        self.assertEqual(len(self.project.script_files), 2)
        self.assertTrue(any("build.sh" in f for f in self.project.script_files))
        self.assertTrue(any("deploy.py" in f for f in self.project.script_files))
        
        # Verify other files were detected
        self.assertEqual(len(self.project.other_files), 1)
        self.assertTrue(any("unknown.xyz" in f for f in self.project.other_files))

    @patch('rich.console.Console.print')
    def test_show_info(self, mock_print):
        """Test displaying project information."""
        # First scan the project
        self.project.scan()
        
        # Then show info
        self.project.show_info()
        
        # Verify console.print was called
        mock_print.assert_called()

    @patch('rich.console.Console.print')
    def test_analyze_structure(self, mock_print):
        """Test analyzing project structure."""
        # First scan the project
        self.project.scan()
        
        # Then analyze structure
        self.project.analyze_structure()
        
        # Verify console.print was called
        mock_print.assert_called()

    @patch('rich.console.Console.print')
    def test_analyze_hardware(self, mock_print):
        """Test analyzing hardware files."""
        # First scan the project
        self.project.scan()
        
        # Then analyze hardware
        self.project.analyze_hardware()
        
        # Verify console.print was called
        mock_print.assert_called()

    @patch('rich.console.Console.print')
    def test_analyze_firmware(self, mock_print):
        """Test analyzing firmware files."""
        # First scan the project
        self.project.scan()
        
        # Then analyze firmware
        self.project.analyze_firmware()
        
        # Verify console.print was called
        mock_print.assert_called()

    @patch('rich.console.Console.print')
    def test_analyze_binary(self, mock_print):
        """Test analyzing binary files."""
        # First scan the project
        self.project.scan()
        
        # Create a mock binary file for testing
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.bin', delete=False) as temp_file:
            temp_file.write(b'\x7FELF\x01\x01\x01\x00')  # Mock ELF header
            binary_file = temp_file.name
        
        try:
            # Then analyze binary with the file path
            with patch('twinizer.software.analyze.binary.BinaryAnalyzer.analyze', return_value={"format": "ELF", "size": 8}):
                result = self.project.analyze_binary(binary_file)
                
                # Verify result contains expected data
                self.assertIsInstance(result, dict)
                self.assertIn("format", result)
                
                # Verify console.print was called
                mock_print.assert_called()
        finally:
            # Clean up the temporary file
            import os
            if os.path.exists(binary_file):
                os.unlink(binary_file)

    def test_backup(self):
        """Test project backup functionality."""
        # Create a temporary directory for the backup
        backup_dir = tempfile.TemporaryDirectory()
        backup_path = os.path.join(backup_dir.name, "backup.zip")
        
        # First scan the project
        self.project.scan()
        
        # Create a backup with a specific path
        with patch('twinizer.core.project.datetime') as mock_datetime:
            mock_datetime.datetime.now.return_value.strftime.return_value = "20250504"
            result = self.project.backup(backup_path)
        
        # Verify backup was created
        self.assertTrue(os.path.exists(backup_path))
        self.assertEqual(result, backup_path)
        
        # Verify backup contains all files
        with zipfile.ZipFile(backup_path, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            self.assertTrue(any("design.sch" in f for f in file_list))
            self.assertTrue(any("main.c" in f for f in file_list))
            self.assertTrue(any("readme.md" in f for f in file_list))
        
        # Clean up
        backup_dir.cleanup()


if __name__ == '__main__':
    unittest.main()
