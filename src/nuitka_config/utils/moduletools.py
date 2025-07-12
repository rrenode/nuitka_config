import pathlib
from typing import Union, Tuple

from importlib.metadata import distribution, PackageNotFoundError

def get_import_name_from_pkg_name(pkg_name: str) -> str | None:
    predetermined_map = {
        "pywin32": "pywin32"
    }
    if pkg_name.lower() in predetermined_map.keys():
        return predetermined_map[pkg_name]
    try:
        dist = distribution(pkg_name)

        # Try top_level.txt first
        try:
            top_level = dist.read_text('top_level.txt')
            if top_level:
                names = [line.strip() for line in top_level.splitlines() if line.strip()]
                if names:
                    return names[0]
        except FileNotFoundError:
            pass

        # Fallback: guess from file structure
        files = list(dist.files or [])
        bad_names = {"__pycache__", "__init__.py"}
        top_level_modules = {
            file.parts[0]
            for file in files
            if len(file.parts) > 0
            and file.parts[0].isidentifier()
            and file.parts[0] not in bad_names
        }

        if top_level_modules:
            return sorted(top_level_modules)[0]

        return pkg_name  # final fallback

    except PackageNotFoundError:
        try:
            __import__(pkg_name)
            return pkg_name
        except ImportError:
            return None

def split_packages_and_modules(import_name_list: list[str]) -> Tuple[list[str], list[str]]:
    """Returns: packages, modules
    """
    packages = []
    modules = []

    for imp in import_name_list:
        try:
            mod = __import__(imp)
            if hasattr(mod, '__path__'):
                packages.append(imp)
            else:
                modules.append(imp)
        except ImportError:
            pass  # or log the error if needed

    return packages, modules
    
def package_names_to_import_names(list) -> list[str]:
    names = []
    for name in list:
        import_name = get_import_name_from_pkg_name(name)
        names.append(import_name)
    return names

def read_requirements_packages_only(path="src/requirements.txt") -> list[str]:
    packages = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "@" in line:  # Handle VCS or local paths
                name = line.split("@")[0].strip()
            else:
                name = line.split("==")[0].split(">=")[0].split("<=")[0].split("~=")[0].strip()
            packages.append(name)
    return packages

def find_package_path(package_name: str) -> str:
    from importlib import import_module
    try:
        module = import_module(package_name.replace("-", "_"))
        return pathlib.Path(module.__file__).parent
    except ImportError:
        return None

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