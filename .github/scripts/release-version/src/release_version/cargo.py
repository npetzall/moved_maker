"""Cargo.toml manipulation functions."""
import sys
from pathlib import Path
from typing import Optional

import tomlkit


def read_cargo_version(path: str = "Cargo.toml") -> str:
    """Read version from Cargo.toml.

    Args:
        path: Path to Cargo.toml file

    Returns:
        Version string from package.version

    Raises:
        FileNotFoundError: If Cargo.toml doesn't exist
        ValueError: If version field is missing or invalid
    """
    try:
        cargo_path = Path(path)
        if not cargo_path.exists():
            raise FileNotFoundError(f"Cargo.toml not found at {path}")

        with open(cargo_path, "r", encoding="utf-8") as f:
            cargo = tomlkit.parse(f.read())

        if "package" not in cargo:
            raise ValueError("No [package] section found in Cargo.toml")

        if "version" not in cargo["package"]:
            raise ValueError("No version field found in [package] section")

        version = str(cargo["package"]["version"])
        if not version:
            raise ValueError("Version field is empty")

        return version
    except tomlkit.exceptions.TOMLKitError as e:
        print(f"Error parsing Cargo.toml: {e}", file=sys.stderr)
        raise ValueError(f"Invalid TOML format: {e}") from e


def update_cargo_version(path: str = "Cargo.toml", version: str = "") -> bool:
    """Update version in Cargo.toml.

    Only writes the file if the version is different from the current version.
    This prevents unnecessary file modifications when the version hasn't changed.

    Args:
        path: Path to Cargo.toml file
        version: New version string to set

    Returns:
        True if version was updated, False if version was unchanged

    Raises:
        FileNotFoundError: If Cargo.toml doesn't exist
        ValueError: If version is invalid or update fails
    """
    try:
        cargo_path = Path(path)
        if not cargo_path.exists():
            raise FileNotFoundError(f"Cargo.toml not found at {path}")

        if not version:
            raise ValueError("Version cannot be empty")

        # Read current version first
        current_version = read_cargo_version(path)

        # Check if version is different
        if current_version == version:
            print(f"Cargo.toml version is already {version}, no update needed")
            return False

        # Read current file
        with open(cargo_path, "r", encoding="utf-8") as f:
            cargo = tomlkit.parse(f.read())

        if "package" not in cargo:
            raise ValueError("No [package] section found in Cargo.toml")

        # Update version
        cargo["package"]["version"] = version

        # Write back
        with open(cargo_path, "w", encoding="utf-8") as f:
            f.write(tomlkit.dumps(cargo))

        # Verify update
        updated_version = read_cargo_version(path)
        if updated_version != version:
            raise ValueError(
                f"Version update failed: expected {version}, got {updated_version}"
            )

        print(f"Updated Cargo.toml version from {current_version} to {version}")
        return True
    except tomlkit.exceptions.TOMLKitError as e:
        print(f"Error parsing Cargo.toml: {e}", file=sys.stderr)
        raise ValueError(f"Invalid TOML format: {e}") from e
