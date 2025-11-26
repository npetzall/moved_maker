"""Pytest configuration and fixtures."""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_binary_file(temp_dir):
    """Create a sample binary file for testing."""
    binary_file = temp_dir / "test.bin"
    # Write some binary data
    binary_file.write_bytes(b"Hello, World!\x00\x01\x02\x03")
    return binary_file


@pytest.fixture
def sample_binary_file_large(temp_dir):
    """Create a larger binary file for testing."""
    binary_file = temp_dir / "large.bin"
    # Write 10KB of data
    data = b"x" * 10240
    binary_file.write_bytes(data)
    return binary_file


@pytest.fixture
def sample_binary_file_empty(temp_dir):
    """Create an empty binary file for testing."""
    binary_file = temp_dir / "empty.bin"
    binary_file.write_bytes(b"")
    return binary_file
