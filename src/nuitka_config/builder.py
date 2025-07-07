import importlib.util

from pathlib import Path
from enum import Enum

from dataclasses import fields, is_dataclass, replace

from nuitka_config.models import *
from nuitka_config.serializers import bool_flag_serializer, enum_serializer, iterable_serializer

def serialize_value(cli_name: str, value) -> list[str]:
    if isinstance(value, bool):
        return bool_flag_serializer(cli_name=cli_name)(value)
    elif isinstance(value, Enum):
        return enum_serializer(cli_name=cli_name)(value)
    elif isinstance(value, list):
        return iterable_serializer(cli_name=cli_name)(value)
    elif isinstance(value, Path):
        return [f"--{cli_name}={str(value.as_posix())}"]
    elif value is not None:
        return [f"--{cli_name}={str(value)}"]
    return []

def _config_to_args(config) -> list[str]:
    args = []

    for field_ in fields(config):
        value = getattr(config, field_.name)
        if value is None:
            continue

        meta = field_.metadata
        serializer = meta.get("serializer")
        cli_name = meta.get("cli")

        if serializer:
            args += serializer(value)
        elif is_dataclass(value):
            args += _config_to_args(value)  # Recursive flattening of nested config
        elif cli_name:
            args += serialize_value(cli_name, value)

    return args

from dataclasses import replace, fields, is_dataclass

def serialize_config(config: NuitkaConfig) -> list[str]:
    args = []

    # Build mode flag (manual)
    if isinstance(config.build_mode, str):
        args.append(f"--{config.build_mode}")
    elif config.build_mode and config.build_mode != BuildMode.default:
        args.append(f"--{config.build_mode.value}")

    # Special case: handle --run manually
    if config.post_compile and config.post_compile.run:
        args.append("--run")

    # Remove run=True from post_compile before serialization
    cleaned_post_compile = replace(config.post_compile, run=None)

    # Replace post_compile and build_mode before general serialization
    temp_config = replace(config,
        build_mode=None,
        post_compile=cleaned_post_compile
    )

    args += _config_to_args(temp_config)
    
    if config.extras:
        if isinstance(config.extras, str):
            args += config.extras.split()
        else:
            args += list(config.extras)
    
    if config.entry_file:
        entry = config.entry_file
        args.append(str(Path(entry).as_posix()))

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