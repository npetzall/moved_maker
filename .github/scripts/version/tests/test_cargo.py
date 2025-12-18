"""Tests for cargo module."""
import tempfile
from pathlib import Path

import pytest

from version.cargo import read_cargo_version, update_cargo_version


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


def test_read_cargo_version_invalid_format(datadir):
    """Test reading Cargo.toml with invalid version format."""
    cargo_toml = datadir / "invalid_format.toml"
    with pytest.raises(ValueError, match="Invalid version format in Cargo.toml"):
        read_cargo_version(str(cargo_toml))


def test_read_cargo_version_with_v_prefix(datadir):
    """Test reading Cargo.toml with version containing 'v' prefix (should be rejected)."""
    cargo_toml = datadir / "with_v_prefix.toml"
    with pytest.raises(
        ValueError,
        match="Version should not include 'v' prefix",
    ):
        read_cargo_version(str(cargo_toml))


def test_read_cargo_version_prerelease(datadir):
    """Test reading Cargo.toml with valid pre-release version."""
    cargo_toml = datadir / "prerelease.toml"
    version = read_cargo_version(str(cargo_toml))
    assert version == "1.0.0-alpha"


def test_read_cargo_version_build_metadata(datadir):
    """Test reading Cargo.toml with valid build metadata version."""
    cargo_toml = datadir / "build_metadata.toml"
    version = read_cargo_version(str(cargo_toml))
    assert version == "1.0.0+build.1"


def test_read_cargo_version_pr_with_build_metadata(datadir):
    """Test reading Cargo.toml with PR version format (pre-release + build metadata)."""
    cargo_toml = datadir / "pr_version_build_metadata.toml"
    version = read_cargo_version(str(cargo_toml))
    assert version == "0.2.1-pr26+87baede"


def test_read_cargo_version_invalid_build_metadata():
    """Test reading Cargo.toml with invalid build metadata format."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write(
            """[package]
name = "test"
version = "1.0.0+invalid@metadata"
"""
        )
        temp_path = Path(f.name)

    try:
        with pytest.raises(ValueError, match="Invalid build metadata format"):
            read_cargo_version(str(temp_path))
    finally:
        if temp_path.exists():
            temp_path.unlink()


def test_read_cargo_version_empty_build_metadata():
    """Test reading Cargo.toml with empty build metadata."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write(
            """[package]
name = "test"
version = "1.0.0+"
"""
        )
        temp_path = Path(f.name)

    try:
        with pytest.raises(ValueError, match="Build metadata cannot be empty"):
            read_cargo_version(str(temp_path))
    finally:
        if temp_path.exists():
            temp_path.unlink()


def test_update_cargo_version_valid(temp_cargo_toml):
    """Test updating version in valid Cargo.toml."""
    new_version = "2.0.0"
    result = update_cargo_version(str(temp_cargo_toml), new_version)

    # Verify update
    updated_version = read_cargo_version(str(temp_cargo_toml))
    assert updated_version == new_version
    # Verify return value is True when version changes
    assert result is True


def test_update_cargo_version_preserves_formatting(sample_cargo_toml_with_deps):
    """Test that updating version preserves formatting."""
    original_content = sample_cargo_toml_with_deps.read_text()
    new_version = "3.0.0"

    result = update_cargo_version(str(sample_cargo_toml_with_deps), new_version)

    # Verify version was updated
    updated_version = read_cargo_version(str(sample_cargo_toml_with_deps))
    assert updated_version == new_version
    # Verify return value is True when version changes
    assert result is True

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


def test_update_cargo_version_unchanged(temp_cargo_toml):
    """Test updating with same version (should return False)."""
    current_version = read_cargo_version(str(temp_cargo_toml))
    original_content = temp_cargo_toml.read_text()

    # Try to update with the same version
    result = update_cargo_version(str(temp_cargo_toml), current_version)

    # Verify return value is False when version unchanged
    assert result is False

    # Verify file was not modified
    assert temp_cargo_toml.read_text() == original_content

    # Verify version is still the same
    assert read_cargo_version(str(temp_cargo_toml)) == current_version


def test_update_cargo_version_pr_with_build_metadata(temp_cargo_toml):
    """Test updating Cargo.toml with PR version format (pre-release + build metadata)."""
    pr_version = "0.2.1-pr26+87baede"
    result = update_cargo_version(str(temp_cargo_toml), pr_version)

    # Verify update
    updated_version = read_cargo_version(str(temp_cargo_toml))
    assert updated_version == pr_version
    # Verify return value is True when version changes
    assert result is True


def test_update_cargo_version_pr_with_build_metadata_unchanged(datadir):
    """Test updating with same PR version (should return False)."""
    cargo_toml = datadir / "pr_version_build_metadata.toml"
    current_version = read_cargo_version(str(cargo_toml))
    original_content = cargo_toml.read_text()

    # Try to update with the same version
    result = update_cargo_version(str(cargo_toml), current_version)

    # Verify return value is False when version unchanged
    assert result is False

    # Verify file was not modified
    assert cargo_toml.read_text() == original_content

    # Verify version is still the same
    assert read_cargo_version(str(cargo_toml)) == current_version
