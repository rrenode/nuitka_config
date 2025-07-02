import importlib.util

from pathlib import Path
from typing import List

from .models import *

def convert_to_nuitka_args(config: NuitkaConfig) -> List[str]:
    args = []

    # --- Core ---
    args.append(str(config.core.entry))
    if config.core.mode == BuildMode.module:
        args.append("--module")
    if config.core.result == BuildResult.standalone:
        args.append("--standalone")
    elif config.core.result == BuildResult.onefile:
        args.append("--onefile")

    # --- Output ---
    if config.output.remove_output:
        args.append("--remove-output")
    if config.output.show_progress:
        args.append("--show-progress")
    if config.output.output_dir:
        args.append(f"--output-dir={config.output.output_dir}")
    if config.output.output_filename:
        args.append(f"--output-filename={config.output.output_filename}")

    # --- Optimization ---
    if config.optimization.lto:
        args.append("--lto=yes")
    else:
        args.append("--lto=no")
    if config.optimization.enable_assets:
        args.append("--enable-asserts")
    if config.optimization.nooptimize:
        args.append("--nooptimize")
    if config.optimization.prefer_source_code:
        args.append("--prefer-source-code")
    if config.optimization.static_libpython:
        args.append("--static-libpython=yes")

    # --- Parallel ---
    if config.parallel.jobs:
        args.append(f"--jobs={config.parallel.jobs}")

    # --- Python ---
    if config.python.flags:
        for flag in config.python.flags:
            args.append(f"--python-flag={flag}")

    # --- Compiler ---
    if config.compiler.backend:
        args.append(f"--{config.compiler.backend}")
    if config.compiler.follow_symlinks:
        args.append("--follow-imports")

    # --- Plugins ---
    for plugin in config.plugins.enabled:
        args.append(f"--enable-plugin={plugin}")
    for user_plugin in config.plugins.user_plugins:
        args.append(f"--user-plugin={user_plugin}")
    if config.plugins.disable_auto_detection:
        args.append("--plugin-no-detection")
    if config.plugins.trace_plugins:
        args.append("--trace-plugins")

    # --- Packages ---
    for inc in config.packages.include:
        args.append(f"--include-package={inc}")
    for exc in config.packages.exclude:
        args.append(f"--exclude-module={exc}")
    if config.packages.nofollow_imports:
        args.append("--nofollow-imports")
    for nf in config.packages.nofollow_to:
        args.append(f"--nofollow-import-to={nf}")

    # --- Data ---
    for f in config.data.include_files:
        args.append(f"--include-data-files={f}")
    for d in config.data.include_dirs:
        args.append(f"--include-data-dir={d}")

    # --- Debug ---
    if config.debug.debug_symbols:
        args.append("--debug")
    if config.debug.unstripped:
        args.append("--unstripped")
    if config.debug.trace_execution:
        args.append("--trace-execution")
    if config.debug.show_memory:
        args.append("--show-memory")
    if config.debug.show_modules:
        args.append("--show-modules")

    # --- Logging ---
    if config.logging.verbose:
        args.append("--verbose")
    if config.logging.quiet:
        args.append("--quiet")

    return args

def load_spec_file(spec_path: Path):
    """Load a Python .spec.py file and extract the `config` object."""
    from sys import modules as sys_modules
    spec = importlib.util.spec_from_file_location("nuitka_spec", str(spec_path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load spec file: {spec_path}")
    module = importlib.util.module_from_spec(spec)
    sys_modules["nuitka_spec"] = module
    spec.loader.exec_module(module)
    if not hasattr(module, "config"):
        raise AttributeError("Spec file must define a variable named 'config'")
    return module.config