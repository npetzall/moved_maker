"""Tests for cargo module."""
import tempfile
from pathlib import Path

import pytest

from release_version.cargo import read_cargo_version, update_cargo_version


def test_read_cargo_version_valid(temp_cargo_toml):
    """Test reading valid Cargo.toml."""
    version = read_cargo_version(str(temp_cargo_toml))
    assert version == "1.0.0"


def test_read_cargo_version_file_not_found():
    """Test reading non-existent Cargo.toml."""
    with pytest.raises(FileNotFoundError):
        read_cargo_version("nonexistent.toml")


def test_read_cargo_version_missing_version():
    """Test reading Cargo.toml without version field."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write(
            """[package]
name = "test"
"""
        )
        temp_path = Path(f.name)

    try:
        with pytest.raises(ValueError, match="No version field"):
            read_cargo_version(str(temp_path))
    finally:
        if temp_path.exists():
            temp_path.unlink()


def test_read_cargo_version_invalid_toml():
    """Test reading invalid TOML format."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write("invalid toml content [")
        temp_path = Path(f.name)

    try:
        with pytest.raises(ValueError, match="Invalid TOML format"):
            read_cargo_version(str(temp_path))
    finally:
        if temp_path.exists():
            temp_path.unlink()


def test_update_cargo_version_valid(temp_cargo_toml):
    """Test updating version in valid Cargo.toml."""
    new_version = "2.0.0"
    update_cargo_version(str(temp_cargo_toml), new_version)

    # Verify update
    updated_version = read_cargo_version(str(temp_cargo_toml))
    assert updated_version == new_version


def test_update_cargo_version_preserves_formatting(sample_cargo_toml_with_deps):
    """Test that updating version preserves formatting."""
    original_content = sample_cargo_toml_with_deps.read_text()
    new_version = "3.0.0"

    update_cargo_version(str(sample_cargo_toml_with_deps), new_version)

    # Verify version was updated
    updated_version = read_cargo_version(str(sample_cargo_toml_with_deps))
    assert updated_version == new_version

    # Verify dependencies section still exists
    updated_content = sample_cargo_toml_with_deps.read_text()
    assert "[dependencies]" in updated_content
    assert "some-dep" in updated_content


def test_update_cargo_version_file_not_found():
    """Test updating non-existent Cargo.toml."""
    with pytest.raises(FileNotFoundError):
        update_cargo_version("nonexistent.toml", "1.0.0")


def test_update_cargo_version_empty_version(temp_cargo_toml):
    """Test updating with empty version."""
    with pytest.raises(ValueError, match="Version cannot be empty"):
        update_cargo_version(str(temp_cargo_toml), "")
