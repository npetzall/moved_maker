"""Tests for checksum module."""

import hashlib
import subprocess
import sys
from pathlib import Path

import pytest

from create_checksum.checksum import (
    calculate_hash,
    calculate_sha256,
    is_valid_algorithm,
)


class TestCalculateSha256:
    """Tests for calculate_sha256 function."""

    def test_calculate_sha256_valid_file(self, sample_binary_file):
        """Test hash calculation with valid file."""
        hash_hex = calculate_sha256(str(sample_binary_file))

        # Verify it's a valid hex string
        assert len(hash_hex) == 64  # SHA256 produces 64 hex characters
        assert all(c in "0123456789abcdef" for c in hash_hex)

        # Verify it matches expected hash
        expected_hash = hashlib.sha256(sample_binary_file.read_bytes()).hexdigest()
        assert hash_hex == expected_hash

    def test_calculate_sha256_different_file_sizes(self, sample_binary_file, sample_binary_file_large, sample_binary_file_empty):
        """Test hash calculation with different file sizes."""
        # Small file
        hash_small = calculate_sha256(str(sample_binary_file))
        assert len(hash_small) == 64

        # Large file
        hash_large = calculate_sha256(str(sample_binary_file_large))
        assert len(hash_large) == 64
        assert hash_small != hash_large  # Different files should have different hashes

        # Empty file
        hash_empty = calculate_sha256(str(sample_binary_file_empty))
        assert len(hash_empty) == 64
        expected_empty_hash = hashlib.sha256(b"").hexdigest()
        assert hash_empty == expected_empty_hash

    def test_calculate_sha256_missing_file(self, temp_dir):
        """Test hash calculation with missing file raises IOError."""
        missing_file = temp_dir / "nonexistent.bin"

        with pytest.raises(IOError):
            calculate_sha256(str(missing_file))

    def test_calculate_sha256_unreadable_file(self, temp_dir):
        """Test hash calculation with unreadable file raises IOError."""
        # On Unix systems, we can create a file and remove read permissions
        # This test may not work on all systems, so we'll skip if it fails
        unreadable_file = temp_dir / "unreadable.bin"
        unreadable_file.write_bytes(b"test")
        try:
            unreadable_file.chmod(0o000)  # Remove all permissions
            with pytest.raises(IOError):
                calculate_sha256(str(unreadable_file))
        finally:
            # Restore permissions for cleanup
            unreadable_file.chmod(0o644)


class TestCalculateHash:
    """Tests for calculate_hash function with algorithm selection."""

    def test_calculate_hash_sha256(self, sample_binary_file):
        """Test hash calculation with sha256 algorithm."""
        hash_hex = calculate_hash(str(sample_binary_file), "sha256")

        # Verify it matches direct sha256 calculation
        expected_hash = calculate_sha256(str(sample_binary_file))
        assert hash_hex == expected_hash

    def test_calculate_hash_invalid_algorithm(self, sample_binary_file):
        """Test hash calculation with invalid algorithm raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported algorithm"):
            calculate_hash(str(sample_binary_file), "md5")

        with pytest.raises(ValueError, match="Unsupported algorithm"):
            calculate_hash(str(sample_binary_file), "sha1")


class TestIsValidAlgorithm:
    """Tests for is_valid_algorithm function."""

    def test_is_valid_algorithm_sha256(self):
        """Test that sha256 is recognized as valid."""
        assert is_valid_algorithm("sha256") is True

    def test_is_valid_algorithm_invalid(self):
        """Test that invalid algorithms are rejected."""
        assert is_valid_algorithm("md5") is False
        assert is_valid_algorithm("sha1") is False
        assert is_valid_algorithm("") is False
        assert is_valid_algorithm("invalid") is False


class TestCLI:
    """Tests for CLI interface."""

    def get_cli_command(self, *args):
        """Helper to build CLI command."""
        return [
            sys.executable,
            "-m",
            "create_checksum",
        ] + list(args)

    def test_cli_valid_arguments(self, sample_binary_file, temp_dir):
        """Test CLI with valid arguments."""
        output_file = temp_dir / "output.sha256"

        result = subprocess.run(
            self.get_cli_command(
                "--file", str(sample_binary_file),
                "--algo", "sha256",
                "--output", str(output_file)
            ),
            capture_output=True,
            text=True,
            cwd=".github/scripts/create-checksum",
        )

        assert result.returncode == 0
        assert output_file.exists()

        # Verify output file content
        output_content = output_file.read_text()
        assert output_content.endswith("  test.bin\n")
        hash_part = output_content.split()[0]
        assert len(hash_part) == 64

        # Verify stdout matches file output
        assert result.stdout == output_content

    def test_cli_missing_file(self, temp_dir):
        """Test CLI with missing binary file."""
        output_file = temp_dir / "output.sha256"
        missing_file = temp_dir / "nonexistent.bin"

        result = subprocess.run(
            self.get_cli_command(
                "--file", str(missing_file),
                "--algo", "sha256",
                "--output", str(output_file)
            ),
            capture_output=True,
            text=True,
            cwd=".github/scripts/create-checksum",
        )

        assert result.returncode == 1
        assert "Binary not found" in result.stderr
        assert not output_file.exists()

    def test_cli_invalid_algorithm(self, sample_binary_file, temp_dir):
        """Test CLI with invalid algorithm."""
        output_file = temp_dir / "output.sha256"

        result = subprocess.run(
            self.get_cli_command(
                "--file", str(sample_binary_file),
                "--algo", "md5",
                "--output", str(output_file)
            ),
            capture_output=True,
            text=True,
            cwd=".github/scripts/create-checksum",
        )

        assert result.returncode == 1
        assert "Unsupported algorithm" in result.stderr
        assert not output_file.exists()

    def test_cli_missing_required_arguments(self, temp_dir):
        """Test CLI with missing required arguments."""
        # Missing --file
        result = subprocess.run(
            self.get_cli_command(
                "--algo", "sha256",
                "--output", str(temp_dir / "output.sha256")
            ),
            capture_output=True,
            text=True,
            cwd=".github/scripts/create-checksum",
        )
        assert result.returncode != 0

        # Missing --algo
        result = subprocess.run(
            self.get_cli_command(
                "--file", str(temp_dir / "test.bin"),
                "--output", str(temp_dir / "output.sha256")
            ),
            capture_output=True,
            text=True,
            cwd=".github/scripts/create-checksum",
        )
        assert result.returncode != 0

        # Missing --output
        result = subprocess.run(
            self.get_cli_command(
                "--file", str(temp_dir / "test.bin"),
                "--algo", "sha256"
            ),
            capture_output=True,
            text=True,
            cwd=".github/scripts/create-checksum",
        )
        assert result.returncode != 0

    def test_cli_creates_parent_directories(self, sample_binary_file, temp_dir):
        """Test CLI creates parent directories for output file."""
        output_file = temp_dir / "nested" / "deep" / "output.sha256"
        assert not output_file.parent.exists()

        result = subprocess.run(
            self.get_cli_command(
                "--file", str(sample_binary_file),
                "--algo", "sha256",
                "--output", str(output_file)
            ),
            capture_output=True,
            text=True,
            cwd=".github/scripts/create-checksum",
        )

        assert result.returncode == 0
        assert output_file.parent.exists()
        assert output_file.exists()

    def test_cli_checksum_file_format(self, sample_binary_file, temp_dir):
        """Test that checksum file format matches expected format."""
        output_file = temp_dir / "output.sha256"

        result = subprocess.run(
            self.get_cli_command(
                "--file", str(sample_binary_file),
                "--algo", "sha256",
                "--output", str(output_file)
            ),
            capture_output=True,
            text=True,
            cwd=".github/scripts/create-checksum",
        )

        assert result.returncode == 0

        # Verify format: <hash>  <filename>\n
        output_content = output_file.read_text()
        parts = output_content.strip().split("  ")
        assert len(parts) == 2
        assert len(parts[0]) == 64  # SHA256 hex length
        assert parts[1] == "test.bin"  # Filename

    def test_cli_atomic_write(self, sample_binary_file, temp_dir):
        """Test that file writing is atomic (temp file then rename)."""
        output_file = temp_dir / "output.sha256"

        result = subprocess.run(
            self.get_cli_command(
                "--file", str(sample_binary_file),
                "--algo", "sha256",
                "--output", str(output_file)
            ),
            capture_output=True,
            text=True,
            cwd=".github/scripts/create-checksum",
        )

        assert result.returncode == 0
        assert output_file.exists()

        # Verify no temp files remain
        temp_files = list(temp_dir.glob("*.tmp"))
        assert len(temp_files) == 0

        # Verify file content is complete (not partial)
        content = output_file.read_text()
        assert content.endswith("\n")
        assert len(content.split()) == 2  # hash and filename

    def test_cli_different_file_sizes(self, sample_binary_file, sample_binary_file_large, sample_binary_file_empty, temp_dir):
        """Test CLI with different file sizes."""
        # Small file
        output_small = temp_dir / "small.sha256"
        result = subprocess.run(
            self.get_cli_command(
                "--file", str(sample_binary_file),
                "--algo", "sha256",
                "--output", str(output_small)
            ),
            capture_output=True,
            text=True,
            cwd=".github/scripts/create-checksum",
        )
        assert result.returncode == 0

        # Large file
        output_large = temp_dir / "large.sha256"
        result = subprocess.run(
            self.get_cli_command(
                "--file", str(sample_binary_file_large),
                "--algo", "sha256",
                "--output", str(output_large)
            ),
            capture_output=True,
            text=True,
            cwd=".github/scripts/create-checksum",
        )
        assert result.returncode == 0

        # Empty file
        output_empty = temp_dir / "empty.sha256"
        result = subprocess.run(
            self.get_cli_command(
                "--file", str(sample_binary_file_empty),
                "--algo", "sha256",
                "--output", str(output_empty)
            ),
            capture_output=True,
            text=True,
            cwd=".github/scripts/create-checksum",
        )
        assert result.returncode == 0

        # Verify all files have different hashes (except empty might match expected)
        hash_small = output_small.read_text().split()[0]
        hash_large = output_large.read_text().split()[0]
        hash_empty = output_empty.read_text().split()[0]

        assert hash_small != hash_large
        assert hash_small != hash_empty
        assert hash_large != hash_empty
