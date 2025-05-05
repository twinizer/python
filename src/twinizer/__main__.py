"""
__main__.py
"""

"""
Entry point for Twinizer when run as a module.
"""

import sys

from twinizer.cli.main import main as cli_main


def main():
    """
    Main entry point for the Twinizer application.
    """
    return cli_main()


if __name__ == "__main__":
    sys.exit(main())
