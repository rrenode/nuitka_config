# src/nuitka_config/__init__.py

from .main import run, normalize_nuitka_cmd 
from .builder import serialize_config, load_spec_file

# Use importlib.metadata to resolve version
import sys

if sys.version_info[:2] >= (3, 8):
    from importlib.metadata import version, PackageNotFoundError  # pragma: no cover
else:
    from importlib_metadata import version, PackageNotFoundError  # pragma: no cover

try:
    __version__ = version("nuitka-config")
except PackageNotFoundError:  # pragma: no cover
    __version__ = unknown
finally:
    del version, PackageNotFoundError
