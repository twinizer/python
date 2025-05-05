"""
Tests for the CLI components in the cli module.
"""

import os
import sys
import unittest
from io import StringIO
from unittest.mock import MagicMock, patch

import click
from click.testing import CliRunner

from twinizer.cli.main import cli, main
from twinizer.cli.shell import TwinizerShell


class TestCLI(unittest.TestCase):
    """Test cases for the CLI functionality."""

    def setUp(self):
        """Set up test environment."""
        self.runner = CliRunner()

    def test_cli_version(self):
        """Test the version option."""
        result = self.runner.invoke(cli, ["--version"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Twinizer version", result.output)

    def test_cli_help(self):
        """Test the help option."""
        result = self.runner.invoke(cli, ["--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Twinizer - A comprehensive environment", result.output)
        # Check that commands are listed
        self.assertIn("run", result.output)

    @patch("twinizer.utils.env.bootstrap_environment")
    @patch("twinizer.cli.shell.TwinizerShell")
    def test_run_command(self, mock_shell_class, mock_bootstrap):
        """Test the run command."""
        # Mock shell instance
        mock_shell = MagicMock()
        mock_shell_class.return_value = mock_shell

        # Call run command
        result = self.runner.invoke(cli, ["run"])

        # Verify exit code
        self.assertEqual(result.exit_code, 0)

        # Verify bootstrap was called
        mock_bootstrap.assert_called_once()

        # Verify shell was created and run
        mock_shell_class.assert_called_once()
        mock_shell.run.assert_called_once()

    @patch("sys.exit")
    def test_main_function(self, mock_exit):
        """Test the main function."""
        # Mock cli function
        with patch("twinizer.cli.main.cli") as mock_cli:
            mock_cli.return_value = 0

            # Call main function
            main()

            # Verify cli was called with empty object
            mock_cli.assert_called_once()
            self.assertEqual(mock_cli.call_args[1], {"obj": {}})

            # Verify exit was not called (since we mocked cli to return 0)
            mock_exit.assert_not_called()


class TestTwinizerShell(unittest.TestCase):
    """Test cases for the TwinizerShell class."""

    def setUp(self):
        """Set up test environment."""
        self.context = {"source_dir": "/tmp/test_project"}

        # Patch Project class
        self.project_patcher = patch("twinizer.cli.shell.Project")
        self.mock_project_class = self.project_patcher.start()
        self.mock_project = MagicMock()
        self.mock_project_class.return_value = self.mock_project

        # Patch PromptSession
        self.session_patcher = patch("twinizer.cli.shell.PromptSession")
        self.mock_session_class = self.session_patcher.start()
        self.mock_session = MagicMock()
        self.mock_session_class.return_value = self.mock_session

        # Create shell instance
        self.shell = TwinizerShell(self.context)

    def tearDown(self):
        """Clean up after tests."""
        self.project_patcher.stop()
        self.session_patcher.stop()

    def test_init(self):
        """Test shell initialization."""
        # Verify project was created
        self.mock_project_class.assert_called_with("/tmp/test_project")

        # Verify session was created
        self.mock_session_class.assert_called_once()

        # Verify attributes
        self.assertEqual(self.shell.context, self.context)
        self.assertEqual(self.shell.source_dir, "/tmp/test_project")
        self.assertEqual(self.shell.project, self.mock_project)

    def test_run(self):
        """Test shell run method."""
        # Mock session prompt
        self.mock_session.prompt.side_effect = EOFError()  # To exit the loop

        # Call run method
        self.shell.run()

        # Verify project scan was called
        self.mock_project.scan.assert_called_once()

        # Verify prompt was called
        self.mock_session.prompt.assert_called_once()

    def test_process_command_exit(self):
        """Test processing exit command."""
        with patch("sys.exit") as mock_exit:
            self.shell.process_command("exit")
            mock_exit.assert_called_with(0)

            # Test quit alias
            mock_exit.reset_mock()
            self.shell.process_command("quit")
            mock_exit.assert_called_with(0)

    @patch("twinizer.cli.shell.console.print")
    def test_process_command_help(self, mock_print):
        """Test processing help command."""
        # Test general help
        self.shell.process_command("help")
        mock_print.assert_called()

        # Test specific command help
        mock_print.reset_mock()
        self.shell.process_command("help analyze")
        mock_print.assert_called()

    @patch("twinizer.cli.shell.console.print")
    def test_process_command_unknown(self, mock_print):
        """Test processing unknown command."""
        self.shell.process_command("unknown_command")
        mock_print.assert_called()
        self.assertIn("Unknown command", mock_print.call_args[0][0])

    def test_execute_command_analyze(self):
        """Test executing analyze command."""
        # Test analyze structure
        self.shell.execute_command("analyze", ["structure"])
        self.mock_project.analyze_structure.assert_called_once()

        # Test analyze hardware
        self.mock_project.reset_mock()
        self.shell.execute_command("analyze", ["hardware"])
        self.mock_project.analyze_hardware.assert_called_once()

        # Test analyze firmware
        self.mock_project.reset_mock()
        self.shell.execute_command("analyze", ["firmware"])
        self.mock_project.analyze_firmware.assert_called_once()

        # Test analyze binary
        self.mock_project.reset_mock()
        self.shell.execute_command("analyze", ["binary"])
        self.mock_project.analyze_binary.assert_called_once()

        # Test analyze without subcommand
        with patch("twinizer.cli.shell.console.print") as mock_print:
            self.mock_project.reset_mock()
            self.shell.execute_command("analyze", [])
            mock_print.assert_called()
            self.mock_project.analyze_structure.assert_not_called()

    def test_execute_command_project(self):
        """Test executing project command."""
        # Test project info
        self.shell.execute_command("project", ["info"])
        self.mock_project.show_info.assert_called_once()

        # Test project scan
        self.mock_project.reset_mock()
        self.shell.execute_command("project", ["scan"])
        self.mock_project.scan.assert_called_once()

        # Test project backup
        self.mock_project.reset_mock()
        with patch("twinizer.cli.shell.console.print"):
            self.shell.execute_command("project", ["backup"])
            self.mock_project.backup.assert_called_once()

        # Test project stats
        self.mock_project.reset_mock()
        self.shell.execute_command("project", ["stats"])
        self.mock_project.show_stats.assert_called_once()


if __name__ == "__main__":
    unittest.main()
