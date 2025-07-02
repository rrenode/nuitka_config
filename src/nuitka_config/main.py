"""
This script provides a CLI interface to run Nuitka with either direct arguments
or using a Python-based .spec.py configuration file.

To install this as a console script, update your ``setup.cfg``::

    [options.entry_points]
    console_scripts =
         nuitka-build = nuitka_config.main:run

Then run ``pip install .`` or ``pip install -e .`` and you'll be able to use the
``nuitka-build`` command in your shell.

Author:
    rrenode

References:
    - https://setuptools.pypa.io/en/latest/userguide/entry_point.html
    - https://pip.pypa.io/en/stable/reference/pip_install
"""

import argparse
import logging
import subprocess
import sys
from pathlib import Path

from nuitka_config import __version__

__author__ = "rrenode"
__copyright__ = "rrenode"
__license__ = "MIT"

_logger = logging.getLogger(__name__)

def convert_config_to_args(config) -> list[str]:
    """Convert a NuitkaConfig dataclass into CLI arguments."""
    from nuitka_config import convert_to_nuitka_args
    return convert_to_nuitka_args(config)


def parse_args(args):
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Nuitka CLI build runner")
    parser.add_argument("--version", action="version", version=f"nuitka_config {__version__}")
    parser.add_argument("--spec", type=Path, help="Path to .spec.py file defining a NuitkaConfig object")
    parser.add_argument("--dry-run", action="store_true", help="Only print the command to be run")
    parser.add_argument("--nuitka", default="nuitka", help="Override the Nuitka binary (e.g., 'python -m nuitka')")
    parser.add_argument(
        "-v", "--verbose", dest="loglevel", help="Set loglevel to INFO", action="store_const", const=logging.INFO
    )
    parser.add_argument(
        "-vv", "--very-verbose", dest="loglevel", help="Set loglevel to DEBUG", action="store_const", const=logging.DEBUG
    )
    return parser.parse_args(args)


def setup_logging(loglevel: int):
    """Configure logging."""
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel or logging.WARNING,
        stream=sys.stdout,
        format=logformat,
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def main(args):
    """Main entry point for CLI logic."""
    from .builder import load_spec_file
    args = parse_args(args)
    setup_logging(args.loglevel)

    if args.spec:
        _logger.info(f"Loading config from {args.spec}")
        config = load_spec_file(args.spec)
        cli_args = convert_config_to_args(config)
    else:
        cli_args = sys.argv[1:]  # fallback to raw passthrough

    full_command = args.nuitka.split() + cli_args
    _logger.debug("Resolved command: %s", full_command)

    if args.dry_run:
        print("Dry run. Would run:")
        print(" ".join(full_command))
    else:
        _logger.info("Running Nuitka...")
        subprocess.run(full_command)


def run(args = None):
    """Run the CLI using arguments from sys.argv."""
    main(args if args else sys.argv[1:])


if __name__ == "__main__":
    run(sys.argv[1:])
