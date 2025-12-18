"""Cargo.toml manipulation functions."""
import re
import sys
from pathlib import Path
from typing import Optional, Tuple

import tomlkit
from packaging.version import InvalidVersion, Version


def _split_version_with_build_metadata(version: str) -> Tuple[str, Optional[str]]:
    """Split version into base version and build metadata.

    SemVer 2.0.0 allows build metadata after a '+' character. This function
    splits the version string, handling edge cases like multiple '+' characters
    in build metadata.

    Args:
        version: Version string that may contain build metadata

    Returns:
        Tuple of (base_version, build_metadata) where build_metadata is None
        if no build metadata is present
    """
    # Split on the last '+' character (build metadata separator)
    # This handles cases where build metadata itself contains '+'
    if "+" in version:
        # Find the last '+' which separates base version from build metadata
        last_plus = version.rfind("+")
        base_version = version[:last_plus]
        build_metadata = version[last_plus + 1 :]
        return (base_version, build_metadata)
    return (version, None)


def _validate_semver_format(version: str) -> None:
    """Validate SemVer 2.0.0 format using regex.

    This is used for versions with build metadata, since packaging.version.Version
    (PEP 440) doesn't fully support SemVer 2.0.0 pre-release formats.

    Args:
        version: Version string to validate (may include pre-release and build metadata)

    Raises:
        ValueError: If version format is invalid
    """
    # SemVer 2.0.0 pattern:
    # - Core version: MAJOR.MINOR.PATCH (numeric)
    # - Optional pre-release: -IDENTIFIER (alphanumeric, dots, hyphens)
    # - Optional build metadata: +IDENTIFIER (alphanumeric, dots, hyphens)
    # Note: We split on '+' first, so this validates the base version + pre-release
    semver_pattern = r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
    if not re.match(semver_pattern, version):
        raise ValueError(
            f"Invalid SemVer 2.0.0 format: {version}. "
            "Expected format: MAJOR.MINOR.PATCH[-PRE-RELEASE]"
        )


def _validate_build_metadata(build_metadata: str) -> None:
    """Validate build metadata format according to SemVer 2.0.0.

    Build metadata must consist of alphanumeric characters, dots, and hyphens.
    Each identifier must be non-empty.

    Args:
        build_metadata: Build metadata string to validate

    Raises:
        ValueError: If build metadata format is invalid
    """
    if not build_metadata:
        raise ValueError("Build metadata cannot be empty")

    # SemVer 2.0.0: Build metadata identifiers are separated by dots
    # Each identifier can contain alphanumeric characters and hyphens
    identifiers = build_metadata.split(".")
    for identifier in identifiers:
        if not identifier:
            raise ValueError(
                f"Invalid build metadata format: {build_metadata}. "
                "Identifiers cannot be empty"
            )
        # Each identifier must be alphanumeric or contain hyphens
        if not re.match(r"^[0-9A-Za-z-]+$", identifier):
            raise ValueError(
                f"Invalid build metadata format: {build_metadata}. "
                "Identifiers must contain only alphanumeric characters and hyphens"
            )


def read_cargo_version(path: str = "Cargo.toml") -> str:
    """Read version from Cargo.toml.

    Supports standard semantic versions as well as versions with pre-release
    identifiers and build metadata (e.g., 1.2.3-pr123+abc1234) according to
    SemVer 2.0.0 specification.

    Args:
        path: Path to Cargo.toml file

    Returns:
        Version string from package.version (validated as semantic version)

    Raises:
        FileNotFoundError: If Cargo.toml doesn't exist
        ValueError: If version field is missing, empty, or invalid format
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

        # Reject versions with 'v' prefix (not standard for Cargo.toml)
        if version.startswith("v") or version.startswith("V"):
            raise ValueError(
                f"Invalid version format in Cargo.toml: {version}. "
                "Version should not include 'v' prefix. Expected semantic version (e.g., 1.0.0)"
            )

        # Split version into base version and build metadata (if present)
        # This allows us to validate SemVer 2.0.0 format with build metadata,
        # which packaging.version.Version (PEP 440) doesn't fully support
        base_version, build_metadata = _split_version_with_build_metadata(version)

        # If build metadata is present, use SemVer 2.0.0 validation
        # (packaging.version.Version doesn't support SemVer pre-release formats like 'pr26')
        if build_metadata is not None:
            # Validate base version (with optional pre-release) using SemVer 2.0.0 regex
            try:
                _validate_semver_format(base_version)
            except ValueError as e:
                raise ValueError(
                    f"Invalid version format in Cargo.toml: {version}. {str(e)}"
                ) from e

            # Validate build metadata format
            try:
                _validate_build_metadata(build_metadata)
            except ValueError as e:
                raise ValueError(
                    f"Invalid version format in Cargo.toml: {version}. {str(e)}"
                ) from e
        else:
            # For versions without build metadata, use packaging.version.Version
            # This maintains backward compatibility with existing validation
            try:
                Version(version)  # Raises InvalidVersion if invalid
            except InvalidVersion as e:
                raise ValueError(
                    f"Invalid version format in Cargo.toml: {version}. "
                    "Expected semantic version (e.g., 1.0.0)"
                ) from e

        return version
    except tomlkit.exceptions.TOMLKitError as e:
        print(f"Error parsing Cargo.toml: {e}")
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
        print(f"Error parsing Cargo.toml: {e}")
        raise ValueError(f"Invalid TOML format: {e}") from e
