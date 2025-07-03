from pathlib import Path

def write_script(path: Path, command: list[str], runner: str = "nuitka"):
    script_type = path.suffix.lower()
    command = [runner] + command

    if script_type == ".bat":
        with path.open("w", encoding="utf-8") as f:
            f.write("@echo off\n")
            f.write("REM Generated Nuitka build script\n\n")
            f.write("setlocal\n\n")
            f.write("REM Run Nuitka with arguments\n")
            f.write(command[0])
            for arg in command[1:]:
                f.write(f" ^\n    {arg}")
            f.write("\n\nendlocal\n")

    elif script_type == ".sh":
        with path.open("w", encoding="utf-8") as f:
            f.write("#!/bin/sh\n")
            f.write("# Generated Nuitka build script\n\n")
            f.write("set -e\n\n")
            f.write(" \\\n    ".join(command))
            f.write("\n")

    elif script_type == ".ps1":
        with path.open("w", encoding="utf-8") as f:
            f.write("#!/usr/bin/env pwsh\n")
            f.write("# Generated Nuitka build script\n\n")
            f.write(f"{command[0]}`\n")
            for arg in command[1:]:
                f.write(f"    {arg}`\n")
            f.write("\n")

    else:
        raise ValueError(f"Unsupported script extension: {script_type}")
