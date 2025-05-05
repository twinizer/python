"""
Tests for the environment utilities in the utils.env module.
"""

import os
import platform
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, call, patch

from twinizer.utils.env import (
    bootstrap_environment,
    check_conda_env,
    check_python_version,
    create_venv,
    get_pip_path,
    get_python_path,
    get_venv_path,
    inject_system_paths,
    install_dependencies,
    is_in_virtualenv,
)


class TestEnvironmentUtils(unittest.TestCase):
    """Test cases for the environment utilities."""

    def test_is_in_virtualenv(self):
        """Test detection of virtual environment."""
        # Test when in a virtualenv (sys.base_prefix != sys.prefix)
        with patch("sys.base_prefix", "base_prefix"), patch(
            "sys.prefix", "different_prefix"
        ):
            self.assertTrue(is_in_virtualenv())

        # Test when in a virtualenv (has real_prefix)
        with patch("sys.real_prefix", "real_prefix", create=True), patch(
            "sys.prefix", "prefix"
        ):
            self.assertTrue(is_in_virtualenv())

        # Test when not in a virtualenv
        with patch("sys.base_prefix", "same_prefix"), patch(
            "sys.prefix", "same_prefix"
        ):
            if hasattr(sys, "real_prefix"):
                with patch.object(sys, "real_prefix", None, create=False):
                    self.assertFalse(is_in_virtualenv())
            else:
                self.assertFalse(is_in_virtualenv())

    def test_check_python_version(self):
        """Test Python version check."""
        # Test with Python 3.9 (should pass)
        with patch("sys.version_info", (3, 9, 0, "final", 0)):
            self.assertTrue(check_python_version())

        # Test with Python 3.10 (should pass)
        with patch("sys.version_info", (3, 10, 0, "final", 0)):
            self.assertTrue(check_python_version())

        # Test with Python 3.8 (should fail)
        with patch("sys.version_info", (3, 8, 0, "final", 0)), patch(
            "rich.console.Console.print"
        ):
            self.assertFalse(check_python_version())

        # Test with Python 2.7 (should fail)
        with patch("sys.version_info", (2, 7, 0, "final", 0)), patch(
            "rich.console.Console.print"
        ):
            self.assertFalse(check_python_version())

    def test_check_conda_env(self):
        """Test conda environment detection."""
        # Test when in a conda environment
        with patch.dict(os.environ, {"CONDA_PREFIX": "/path/to/conda/env"}):
            self.assertTrue(check_conda_env())

        # Test when not in a conda environment
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(check_conda_env())

    def test_get_venv_path(self):
        """Test getting the virtual environment path."""
        # Mock home directory
        with patch("pathlib.Path.home", return_value=Path("/home/user")):
            venv_path = get_venv_path()
            self.assertEqual(venv_path, Path("/home/user/.twinizer_env"))

    @patch("subprocess.run")
    @patch("rich.console.Console.print")
    def test_create_venv(self, mock_print, mock_run):
        """Test virtual environment creation."""
        venv_path = Path("/path/to/venv")
        create_venv(venv_path)

        # Verify subprocess.run was called correctly
        mock_run.assert_called_with(
            [sys.executable, "-m", "venv", venv_path], check=True
        )

    def test_get_pip_path(self):
        """Test getting the pip path in the virtual environment."""
        venv_path = Path("/path/to/venv")

        # Test on Windows
        with patch("platform.system", return_value="Windows"):
            pip_path = get_pip_path(venv_path)
            self.assertEqual(pip_path, Path("/path/to/venv/Scripts/pip.exe"))

        # Test on Linux
        with patch("platform.system", return_value="Linux"):
            pip_path = get_pip_path(venv_path)
            self.assertEqual(pip_path, Path("/path/to/venv/bin/pip"))

    def test_get_python_path(self):
        """Test getting the Python path in the virtual environment."""
        venv_path = Path("/path/to/venv")

        # Test on Windows
        with patch("platform.system", return_value="Windows"):
            python_path = get_python_path(venv_path)
            self.assertEqual(python_path, Path("/path/to/venv/Scripts/python.exe"))

        # Test on Linux
        with patch("platform.system", return_value="Linux"):
            python_path = get_python_path(venv_path)
            self.assertEqual(python_path, Path("/path/to/venv/bin/python"))

    @patch("subprocess.run")
    @patch("rich.progress.Progress")
    def test_install_dependencies(self, mock_progress, mock_run):
        """Test dependency installation."""
        # Mock progress bar
        mock_task = MagicMock()
        mock_progress_instance = MagicMock()
        mock_progress_instance.add_task.return_value = mock_task
        mock_progress.return_value.__enter__.return_value = mock_progress_instance

        # Call install_dependencies
        pip_path = Path("/path/to/venv/bin/pip")
        install_dependencies(pip_path)

        # Verify subprocess.run was called correctly
        mock_run.assert_called_with([str(pip_path), "install", "-e", "."], check=True)

        # Verify progress was updated
        mock_progress_instance.update.assert_called()

    def test_inject_system_paths(self):
        """Test system path injection."""
        # Save original PATH
        original_path = os.environ.get("PATH", "")

        try:
            # Set up a test PATH
            os.environ["PATH"] = "/usr/bin:/bin"

            # Mock platform and path existence
            with patch("platform.system", return_value="Linux"), patch(
                "os.path.exists", return_value=True
            ):
                inject_system_paths()

                # Verify paths were added
                self.assertIn("/usr/local/bin", os.environ["PATH"])
                self.assertIn("/opt/gcc/bin", os.environ["PATH"])
                self.assertIn("/opt/avr/bin", os.environ["PATH"])
        finally:
            # Restore original PATH
            os.environ["PATH"] = original_path

    @patch("twinizer.utils.env.check_python_version", return_value=True)
    @patch("twinizer.utils.env.is_in_virtualenv", return_value=False)
    @patch("twinizer.utils.env.check_conda_env", return_value=False)
    @patch("twinizer.utils.env.get_venv_path")
    @patch("pathlib.Path.exists")
    @patch("twinizer.utils.env.create_venv")
    @patch("twinizer.utils.env.get_pip_path")
    @patch("twinizer.utils.env.install_dependencies")
    @patch("twinizer.utils.env.get_python_path")
    @patch("os.execv")
    def test_bootstrap_environment_new_venv(
        self,
        mock_execv,
        mock_get_python_path,
        mock_install_dependencies,
        mock_get_pip_path,
        mock_create_venv,
        mock_exists,
        mock_get_venv_path,
        mock_check_conda_env,
        mock_is_in_virtualenv,
        mock_check_python_version,
    ):
        """Test bootstrapping a new virtual environment."""
        # Mock venv path
        venv_path = Path("/path/to/venv")
        mock_get_venv_path.return_value = venv_path
        mock_exists.return_value = False

        # Mock pip and python paths
        pip_path = Path("/path/to/venv/bin/pip")
        python_path = Path("/path/to/venv/bin/python")
        mock_get_pip_path.return_value = pip_path
        mock_get_python_path.return_value = python_path

        # Call bootstrap_environment
        bootstrap_environment()

        # Verify venv was created
        mock_create_venv.assert_called_once_with(venv_path)

        # Verify dependencies were installed
        mock_install_dependencies.assert_called_once_with(pip_path)

        # Verify python was re-executed
        mock_execv.assert_called_once_with(
            str(python_path), [str(python_path)] + sys.argv
        )

    @patch("twinizer.utils.env.check_python_version", return_value=True)
    @patch("twinizer.utils.env.is_in_virtualenv", return_value=False)
    @patch("twinizer.utils.env.check_conda_env", return_value=False)
    @patch("twinizer.utils.env.get_venv_path")
    @patch("pathlib.Path.exists")
    @patch("twinizer.utils.env.create_venv")
    @patch("twinizer.utils.env.get_pip_path")
    @patch("twinizer.utils.env.install_dependencies")
    @patch("twinizer.utils.env.get_python_path")
    @patch("os.execv")
    def test_bootstrap_environment_existing_venv(
        self,
        mock_execv,
        mock_get_python_path,
        mock_install_dependencies,
        mock_get_pip_path,
        mock_create_venv,
        mock_exists,
        mock_get_venv_path,
        mock_check_conda_env,
        mock_is_in_virtualenv,
        mock_check_python_version,
    ):
        """Test bootstrapping with an existing virtual environment."""
        # Mock venv path
        venv_path = Path("/path/to/venv")
        mock_get_venv_path.return_value = venv_path
        mock_exists.return_value = True

        # Mock pip and python paths
        pip_path = Path("/path/to/venv/bin/pip")
        python_path = Path("/path/to/venv/bin/python")
        mock_get_pip_path.return_value = pip_path
        mock_get_python_path.return_value = python_path

        # Call bootstrap_environment
        bootstrap_environment()

        # Verify venv was not created
        mock_create_venv.assert_not_called()

        # Verify dependencies were installed
        mock_install_dependencies.assert_called_once_with(pip_path)

        # Verify python was re-executed
        mock_execv.assert_called_once_with(
            str(python_path), [str(python_path)] + sys.argv
        )

    @patch("twinizer.utils.env.check_python_version", return_value=True)
    @patch("twinizer.utils.env.is_in_virtualenv", return_value=True)
    def test_bootstrap_environment_already_in_venv(
        self, mock_is_in_virtualenv, mock_check_python_version
    ):
        """Test bootstrapping when already in a virtual environment."""
        # Call bootstrap_environment
        result = bootstrap_environment()

        # Verify result is True (no action needed)
        self.assertTrue(result)

    @patch("twinizer.utils.env.check_python_version", return_value=True)
    @patch("twinizer.utils.env.is_in_virtualenv", return_value=False)
    @patch("twinizer.utils.env.check_conda_env", return_value=True)
    def test_bootstrap_environment_in_conda(
        self, mock_check_conda_env, mock_is_in_virtualenv, mock_check_python_version
    ):
        """Test bootstrapping when in a conda environment."""
        # Call bootstrap_environment
        result = bootstrap_environment()

        # Verify result is True (no action needed)
        self.assertTrue(result)

    @patch("twinizer.utils.env.check_python_version", return_value=False)
    def test_bootstrap_environment_wrong_python(self, mock_check_python_version):
        """Test bootstrapping with incompatible Python version."""
        # Call bootstrap_environment
        result = bootstrap_environment()

        # Verify result is False (cannot bootstrap)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
