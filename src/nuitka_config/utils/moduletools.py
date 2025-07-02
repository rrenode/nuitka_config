import pathlib
from typing import Union

def collect_submodules(
    root_package: str,
    *,
    source_root: Union[str, pathlib.Path] = "src",
    file_ext: str = ".py"
) -> list[str]:
    source_root = pathlib.Path(source_root).resolve()
    base_path = (source_root / root_package.replace(".", "/")).resolve()

    if not base_path.is_dir():
        raise ValueError(f"Package path '{base_path}' does not exist or is not a directory.")

    submodules = []

    for py_file in base_path.rglob(f"*{file_ext}"):
        rel_path = py_file.relative_to(source_root).with_suffix("")
        parts = rel_path.parts
        if parts[-1] == "__init__":
            parts = parts[:-1]
        dotted_path = ".".join(parts)
        submodules.append(dotted_path)

    return submodules