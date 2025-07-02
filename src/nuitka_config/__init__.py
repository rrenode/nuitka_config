# src/nuitka_config/__init__.py

from .main import run  # CLI entry point
from .builder import convert_to_nuitka_args, load_spec_file
from .models import (
    # Main Config Model
    NuitkaConfig, 
    
    # Its Sub-Models
    Core, Output, Optimization, 
    Parallel, Python, Compiler, Plugins, Packages,
    Data, Debug, Logging,
    
    # Choice Models
    BuildMode,
    BuildResult,
    Compilers,
)

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
