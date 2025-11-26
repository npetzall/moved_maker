"""Entry point for create-checksum package."""

import argparse
import os
import sys
import tempfile
from pathlib import Path

from create_checksum.checksum import calculate_hash, is_valid_algorithm


def write_checksum_atomic(output_path: Path, checksum_line: str) -> None:
    """
    Write checksum line to file using atomic write (write to temp file, then rename).

    Creates parent directories if they don't exist.

    Args:
        output_path: Path to the output file
        checksum_line: The checksum line to write

    Raises:
        IOError: If the file cannot be written
    """
    # Create parent directories if they don't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Atomic write: write to temporary file, then rename
    # This prevents partial file corruption if the process is interrupted
    temp_dir = output_path.parent
    temp_file = tempfile.NamedTemporaryFile(
        mode="w", dir=temp_dir, delete=False, suffix=".tmp"
    )
    try:
        temp_file.write(checksum_line)
        temp_file.flush()
        os.fsync(temp_file.fileno())  # Ensure data is written to disk
        temp_file.close()
        # Atomic rename
        os.replace(temp_file.name, str(output_path))
    except Exception as e:
        # Clean up temp file on error
        try:
            os.unlink(temp_file.name)
        except OSError:
            pass
        raise IOError(f"Error writing checksum file: {e}") from e


def main() -> int:
    """Main entry point for create-checksum application."""
    parser = argparse.ArgumentParser(
        description="Create checksum file for a binary using specified algorithm"
    )
    parser.add_argument(
        "--file",
        required=True,
        help="Path to binary file to create checksum for",
    )
    parser.add_argument(
        "--algo",
        required=True,
        help="Hash algorithm to use (currently only 'sha256' supported)",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to output checksum file",
    )

    args = parser.parse_args()

    # Validate algorithm
    if not is_valid_algorithm(args.algo):
        print(
            f"Error: Unsupported algorithm '{args.algo}'. Only 'sha256' is currently supported.",
            file=sys.stderr,
        )
        return 1

    # Verify binary file exists
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: Binary not found at {file_path}", file=sys.stderr)
        return 1

    # Calculate hash
    try:
        hash_hex = calculate_hash(str(file_path), args.algo)
    except IOError as e:
        print(f"Error reading binary: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    # Get filename for checksum line
    filename = file_path.name
    checksum_line = f"{hash_hex}  {filename}\n"

    # Write checksum file using atomic write
    output_path = Path(args.output)
    try:
        write_checksum_atomic(output_path, checksum_line)
    except IOError as e:
        print(f"Error writing checksum file: {e}", file=sys.stderr)
        return 1

    # Print to stdout (matches current behavior)
    print(checksum_line, end="")

    return 0


if __name__ == "__main__":
    sys.exit(main())
