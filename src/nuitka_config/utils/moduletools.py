import pathlib

def collect_submodules(package_root: str) -> list[str]:
    base_path = pathlib.Path("src") / package_root
    submodules = []

    for py_file in base_path.rglob("*.py"):
        rel_path = py_file.relative_to("src").with_suffix("")
        parts = rel_path.parts
        if parts[-1] == "__init__":
            parts = parts[:-1]
        submodules.append(".".join(parts))

    return submodules
