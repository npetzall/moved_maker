"""Core checksum calculation functionality."""

import hashlib
from typing import Literal

# Supported algorithms (currently only sha256, but extensible)
SupportedAlgorithm = Literal["sha256"]


def calculate_sha256(file_path: str) -> str:
    """
    Calculate SHA256 hash of a file.

    Args:
        file_path: Path to the file to hash

    Returns:
        Hexadecimal string representation of the SHA256 hash

    Raises:
        IOError: If the file cannot be read
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def calculate_hash(file_path: str, algorithm: SupportedAlgorithm) -> str:
    """
    Calculate hash of a file using the specified algorithm.

    Args:
        file_path: Path to the file to hash
        algorithm: Hash algorithm to use (currently only "sha256" supported)

    Returns:
        Hexadecimal string representation of the hash

    Raises:
        IOError: If the file cannot be read
        ValueError: If the algorithm is not supported
    """
    if algorithm == "sha256":
        return calculate_sha256(file_path)
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")


def is_valid_algorithm(algorithm: str) -> bool:
    """
    Check if an algorithm name is valid and supported.

    Args:
        algorithm: Algorithm name to validate

    Returns:
        True if the algorithm is supported, False otherwise
    """
    return algorithm == "sha256"
