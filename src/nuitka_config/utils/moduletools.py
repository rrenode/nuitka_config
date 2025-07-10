import pathlib
from typing import Union

def collect_submodules(
    root_package: str,
    *,
    source_root: Union[str, pathlib.Path] = "src",
    file_ext: str = ".py"
) -> list[str]:
    """
    Recursively collect all Python submodules (and subpackages) under a given root package directory.

    Args:
        root_package (str): The root Python package name (e.g., "myapp.utils").
        source_root (Union[str, Path], optional): Path to the project source root. Defaults to "src".
        file_ext (str, optional): Extension of Python files to look for. Defaults to ".py".

    Returns:
        list[str]: A list of fully-qualified dotted module names (e.g., "myapp.utils.helper").

    Raises:
        ValueError: If the computed base path does not exist or is not a directory.

    Example:
        Given this structure:
            src/
            └── myapp/
                ├── __init__.py
                ├── utils/
                │   ├── __init__.py
                │   └── helper.py
                └── main.py

        Calling `collect_submodules("myapp", source_root="src")` would return:
            ["myapp", "myapp.utils", "myapp.utils.helper", "myapp.main"]
    """
    source_root = pathlib.Path(source_root).resolve()
    base_path = (source_root / str(root_package).replace(".", "/")).resolve()

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