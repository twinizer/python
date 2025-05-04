#!/usr/bin/env python3
"""
Test runner for Twinizer.

This script runs all the tests in the Twinizer test suite.
"""

import os
import sys
import unittest
import argparse


def discover_and_run(pattern=None, verbose=False):
    """
    Discover and run tests matching the given pattern.
    
    Args:
        pattern: Test pattern to match (e.g., 'test_pdf2md')
        verbose: Whether to show verbose output
    
    Returns:
        True if all tests pass, False otherwise
    """
    # Get the directory containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create a test loader
    loader = unittest.TestLoader()
    
    # Discover tests
    if pattern:
        suite = loader.discover(script_dir, pattern=f"*{pattern}*.py")
    else:
        suite = loader.discover(script_dir)
    
    # Create a test runner
    verbosity = 2 if verbose else 1
    runner = unittest.TextTestRunner(verbosity=verbosity)
    
    # Run the tests
    result = runner.run(suite)
    
    # Return True if all tests pass
    return result.wasSuccessful()


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run Twinizer tests")
    parser.add_argument("-p", "--pattern", help="Test pattern to match (e.g., 'pdf2md')")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show verbose output")
    args = parser.parse_args()
    
    # Run tests and exit with appropriate status code
    success = discover_and_run(args.pattern, args.verbose)
    sys.exit(0 if success else 1)
