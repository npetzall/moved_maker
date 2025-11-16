"""Pytest configuration and fixtures."""
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_github_client():
    """Create a mock GitHub client."""
    client = MagicMock()
    return client


@pytest.fixture
def mock_repo():
    """Create a mock repository object."""
    repo = MagicMock()
    repo.full_name = "owner/repo"
    return repo


@pytest.fixture
def mock_pr():
    """Create a mock pull request object."""
    pr = MagicMock()
    pr.number = 1
    pr.merged_at = None
    pr.updated_at = None
    pr.labels = []
    return pr


@pytest.fixture
def temp_cargo_toml():
    """Create a temporary Cargo.toml file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write(
            """[package]
name = "test-package"
version = "1.0.0"
edition = "2021"
"""
        )
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def sample_cargo_toml_with_deps():
    """Create a temporary Cargo.toml with dependencies."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write(
            """[package]
name = "test-package"
version = "2.3.1"
edition = "2021"

[dependencies]
some-dep = "1.0.0"
"""
        )
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    if temp_path.exists():
        temp_path.unlink()
