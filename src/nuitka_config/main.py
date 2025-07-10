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

__author__ = "rrenode"
__copyright__ = "rrenode"
__license__ = "MIT"

_logger = logging.getLogger(__name__)

def convert_config_to_args(config) -> list[str]:
    """Convert a NuitkaConfig dataclass into CLI arguments."""
    from nuitka_config import serialize_config
    return serialize_config(config)


def parse_args(args):
    """Parse CLI arguments."""
    from nuitka_config import __version__
    parser = argparse.ArgumentParser(description="Nuitka CLI build runner", allow_abbrev=False)
    parser.add_argument("--version", action="version", version=f"nuitka_config {__version__}")
    parser.add_argument("--spec", type=Path, help="Path to .spec.py file defining a NuitkaConfig object")
    parser.add_argument("--dry-run", action="store_true", help="Only print the command to be run")
    parser.add_argument(
        "--export-script",
        type=Path,
        help="Write the resolved Nuitka command to a script file (.bat, .sh, or .ps1)"
    )
    parser.add_argument("--nuitka", default="nuitka", help="Override the Nuitka binary (e.g., 'python -m nuitka')")
    parser.add_argument(
        "-v", "--verbose", dest="loglevel", help="Set loglevel to INFO", action="store_const", const=logging.INFO
    )
    parser.add_argument(
        "-vv", "--very-verbose", dest="loglevel", help="Set loglevel to DEBUG", action="store_const", const=logging.DEBUG
    )
    return parser.parse_known_args(args)


def setup_logging(loglevel: int):
    """Configure logging."""
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel or logging.WARNING,
        stream=sys.stdout,
        format=logformat,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

def detect_nuitka():
    import importlib.util
    import shutil
    cli_path = shutil.which("nuitka") 
    py_module = importlib.util.find_spec("nuitka") is not None

    return {
        "cli_available": bool(cli_path),
        "cli_path": cli_path,
        "module_available": py_module
    }

def normalize_nuitka_cmd(cmd: list):
    nuitka_paths = detect_nuitka()
    exc = nuitka_paths.get("cli_path")
    mod = nuitka_paths.get("module_available")
    if mod:
        cmd.insert(0, sys.executable)
        cmd.insert(1, "-m")
    elif exc:
        cmd.insert(0, exc)
    return cmd

def main(args):
    from nuitka_config.builder import load_spec_file
    parsed_args, passthrough_args = parse_args(args)
    setup_logging(parsed_args.loglevel)

    if parsed_args.spec:
        _logger.info(f"Loading config from {parsed_args.spec}")
        config = load_spec_file(parsed_args.spec)
        cli_args = convert_config_to_args(config)
    elif passthrough_args:
        cli_args = passthrough_args + [" <--- (Plus Nuitka's defaults)"]
    else:
        # No --spec and no args: use default config
        _logger.info("No spec or args provided — using default NuitkaConfig()")
        from nuitka_config.models import NuitkaConfig
        config = NuitkaConfig()
        cli_args = convert_config_to_args(config)

    cmd = parsed_args.nuitka.split() + cli_args
    full_command = normalize_nuitka_cmd(cmd)
    
    _logger.debug("Resolved command: %s", full_command)

    if parsed_args.export_script:
        from nuitka_config.utils.files import write_script
        write_script(parsed_args.export_script, cli_args, runner=parsed_args.nuitka)
        _logger.info(f"Wrote build script to {parsed_args.export_script}")
    elif parsed_args.dry_run:
        print("Dry run. Would run:")
        print(" ".join(full_command))
    else:
        _logger.info("Running Nuitka...")
        subprocess.run(full_command)


def run(args = None):
    """Run the CLI using arguments from sys.argv."""
    main(args if args else sys.argv[1:])


if __name__ == "__main__":
    run()
