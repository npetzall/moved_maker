#!/usr/bin/env python3
"""Create SHA256 checksum file for a binary."""
import hashlib
import sys
import os
import argparse


def calculate_sha256(file_path):
    """Calculate SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def main():
    parser = argparse.ArgumentParser(description="Create SHA256 checksum file")
    parser.add_argument("binary", help="Path to binary file")
    parser.add_argument("output", help="Path to output checksum file")
    args = parser.parse_args()

    # Verify binary exists
    if not os.path.exists(args.binary):
        print(f"Error: Binary not found at {args.binary}", file=sys.stderr)
        sys.exit(1)

    # Calculate SHA256
    try:
        hash_hex = calculate_sha256(args.binary)
    except IOError as e:
        print(f"Error reading binary: {e}", file=sys.stderr)
        sys.exit(1)

    # Get filename for checksum line
    filename = os.path.basename(args.binary)
    checksum_line = f"{hash_hex}  {filename}\n"

    # Write checksum file
    try:
        with open(args.output, "w") as f:
            f.write(checksum_line)
    except IOError as e:
        print(f"Error writing checksum file: {e}", file=sys.stderr)
        sys.exit(1)

    # Print to stdout (matches current behavior)
    print(checksum_line, end="")

    sys.exit(0)


if __name__ == "__main__":
    main()
