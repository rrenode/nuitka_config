from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Optional

from nuitka_config.utils.export_class import export

@export
class BuildMode(StrEnum):
    #=================================================#
    # Compiles a Python script into a loadable Python extension module 
    #   (like .so, .pyd, or .dll depending on OS). No entrypoint is run — 
    #   instead, you import it from other Python code.
    #=================================================#
    module = "module" 
    
    #=================================================#
    # Compiles your Python script into a standalone executable (e.g., .exe, ELF binary). 
    #   The entrypoint is run like a program.
    #=================================================#
    executable = "executable" 
    
@export
class BuildResult(StrEnum):
    #=================================================#
    # IDK
    #=================================================#
    default = ""
    
    #=================================================#
    # Creates a directory (dist/your_app/) containing:
    #   - Your app executable
    #   - All dependencies (Python DLL, packages, plugins, etc.)
    #   - Portable — but still a folder of files.
    #
    # Use this when you want a fully self-contained app that doesn't rely 
    #   on a system Python install.
    #=================================================#
    standalone = "standalone"
    
    #=================================================#
    # Builds on standalone, but compresses everything into a single .exe or binary.
    # - At runtime, it unpacks the contents into a temporary 
    #       directory and runs it from there.
    # - Slightly slower startup, but more portable.
    #
    # Use when you want a single-file app for easier distribution.
    # Implicitly sets standalone = true.
    #=================================================#
    onefile = "onefile"
    
@export
@dataclass
class Core:
    """What you're compiling. Entrypoint and packaging mode.
    """
    entry: Path = "main.py"
    mode: BuildMode = BuildMode.executable
    result: BuildResult = BuildResult.standalone

@export
@dataclass
class Output:
    """Where output goes and naming behavior.
    """
    output_dir: str = "dist"
    output_filename: Path = "my_program"
    remove_output: bool = True
    show_progress: bool = True

@export
@dataclass
class Optimization:
    """Performance-related toggles.
    """
    lto: bool = True
    enable_asserts: bool = True
    nooptimize: bool = False
    prefer_source_code: bool = True
    static_libpython: bool = False

@export
@dataclass
class Parallel:
    """Compilation speed (e.g. --jobs).
    """
    jobs: int = 4

@export
@dataclass
class Python:
    """Python version and flags.
    """
    python_version = "3.11"
    flags: list[str] = field(default_factory=lambda: ["no_site"])  # --python-flag=

@export
class Compilers(StrEnum):
    mingw64 = "mingw64"
    clang = "clang"
    msvc = "msvc"
    gcc = "gcc"

@export
@dataclass
class Compiler:
    """Control C compiler backend and build mechanics.
    """
    backend: Optional[Compilers] = None  # Choose automatically or platform-specific
    follow_symlinks: bool = False

@export
@dataclass
class Plugins:
    """Plugin enablement and configuration.

    These help Nuitka handle special libraries that need custom treatment.
        (e.g., tk-inter, multiprocessing, numpy, etc.)
    
    You must manually enable some plugins, or your app may break 
    For instance, tkinter GUIs won't launch properly without tk-inter plugin).
    """
    #=================================================#
    # List of built-in Nuitka plugins.
    #=================================================#
    enabled: list[str] = field(default_factory=list)
    
    #=================================================#
    # Paths to custom plugin scripts (.py files) written by you.
    # 
    # These can:
    #   - Include additional files,
    #   - Hook into the compilation process,
    #   - Modify behavior of modules,
    #   - Patch compatibility issues.
    #=================================================#
    user_plugins: list[Path] = field(default_factory=list)
    
    #=================================================#
    # By default, Nuitka tries to detect needed plugins automatically 
    #   (based on your imports); this disables that.
    #
    # Use when you want full manual control and avoid accidental plugin inclusion.
    #=================================================#
    disable_auto_detection: bool = False
    
    #=================================================#
    # Logs detailed information about plugin activity during compilation.
    #
    # Use when debugging plugin behavior or figuring out what’s going wrong with packaging.
    #=================================================#
    trace_plugins: bool = False

@export
@dataclass
class Packages:
    """Manual module/package inclusion/exclusion.
    """
    #=================================================#
    # Force Nuitka to include specific packages or modules even if it didn't detect them via import scanning.
    # 
    # Needed for:
    #   - Dynamic imports (__import__, importlib),
    #   - Conditional imports,
    #   - Plugins that Nuitka doesn't fully scan.
    #=================================================#
    include: list[str] = field(default_factory=list)
    
    #=================================================#
    # Exclude specific modules/packages even if Nuitka thinks they’re needed.
    #
    # Use to shrink binary size or avoid bundling dev/test-only code.
    #=================================================#
    exclude: list[str] = field(default_factory=list)
    
    #=================================================#
    # Tells Nuitka to not follow any imports unless you manually include them.
    #
    # Use when you want complete manual control (advanced use only).
    # [!!!] Without include, your app probably won’t work if you enable this.
    #=================================================#
    nofollow_imports: bool = False
    
    #=================================================#
    # Tells Nuitka to ignore imports to specific modules 
    #   (like test frameworks or large unused submodules).
    # 
    # Use this to cut out bloat (e.g., excluding matplotlib.tests or scipy.whatever).
    #=================================================#
    nofollow_to: list[str] = field(default_factory=list)

@export
@dataclass
class Data:
    """Embedding data files and directories.
    """
    include_files: list[Path] = field(default_factory=list)
    include_dirs: list[Path] = field(default_factory=list)
    
@export
@dataclass
class Debug:
    """Debug symbols and runtime tracing.
    """
    debug_symbols: bool = True
    unstripped: bool = True
    trace_execution: bool = False
    show_memory: bool = False
    show_modules: bool = True

@export
@dataclass
class Logging:
    """Console verbosity and diagnostics.
    """
    verbose: bool = False
    quiet: bool = False

@export
@dataclass
class BinaryVersionInfo:
    company_name: str = "UNKNOWN"
    product_name: str = "MY_PROGRAM"
    file_version: str = "0.0.0-dev"

@export
@dataclass
class OSControls:
    #=================================================#
    #STUB - Ambiguous
    # Force standard output of the program to go to this location. 
    #  Useful for programs with disabled console and programs using 
    #   the Windows Services Plugin of Nuitka commercial. 
    # Defaults to not active, 
    #   use e.g. '{PROGRAM_BASE}.out.txt', i.e. file near your program.
    # Check User Manual for full list of available values.
    #=================================================#
    force_stdout: str | None = None
    
    #=================================================#
    #STUB - Ambiguous
    # Force standard error of the program to go to this location. 
    # Useful for programs with disabled console and programs using 
    #   the Windows Services Plugin of Nuitka commercial. 
    # Defaults to not active, 
    #   use e.g. '{PROGRAM_BASE}.err.txt', i.e. file near your program.
    # Check User Manual for full list of available values.
    #=================================================#
    force_stderr: str | None = None

@export
class WindowsConsoleMode(StrEnum):
    # creates a console window unless the program was started from one.
    force = "force"
    
    # With 'disable' it doesn't create or use a console at all.
    disable = "disable"
    
    # With 'attach' an existing console will be used for outputs.
    attach = "attach"
    
    # With 'hide' a newly spawned console will be hidden and an already
    #   existing console will behave like 'force'. 
    hide = "hide"

@export
@dataclass
class WindowsOS:
    # Select console mode to use. Default mode is 'force'.
    console_mode: bool = WindowsConsoleMode.force
    
    # Add executable icon. Can be given multiple times for different 
    #   resolutions or files with multiple icons inside.
    icon_from_ico: Path | None = None
    
    # Copy executable icons from this existing executable (Windows only).
    icon_from_exe: Path | None = None
    
    # When compiling for Windows and onefile, show this
    #   while loading the application. Defaults to off.
    slash_screen: str = ""
    
    # Request Windows User Control, to grant admin rights on
    #   execution. (Windows only). Defaults to off.
    uac_admin: bool = False
    
    # Request Windows User Control, to enforce running from 
    #   a few folders only, remote desktop access. 
    #   (Windows only). Defaults to off.
    uac_uiaccess: bool = False

@export
@dataclass
class NuitkaConfig:
    core: Core = field(default_factory=Core) 
    output: Output = field(default_factory=Output)
    optimization: Optimization = field(default_factory=Optimization)
    parallel: Parallel = field(default_factory=Parallel)
    python: Python = field(default_factory=Python)
    compiler: Compiler = field(default_factory=Compiler)
    plugins: Plugins = field(default_factory=Plugins)
    packages: Packages = field(default_factory=Packages)
    data: Data = field(default_factory=Data)
    debug: Debug = field(default_factory=Debug)
    logging: Logging = field(default_factory=Logging)