# Create Checksum

A Python script to create SHA256 checksum files for binary artifacts. The script calculates the SHA256 hash of a file and writes it in the standard checksum format: `<hash>  <filename>`.

## Usage

### Setup

Install dependencies using `uv`:

```bash
cd .github/scripts/create-checksum
uv sync --extra dev
```

### Running the Script

Run the script using `uv run`:

```bash
uv run python -m create_checksum --file <binary_file> --algo sha256 --output <output_file>
```

### Command-Line Arguments

- `--file`: Path to binary file to create checksum for (required)
- `--algo`: Hash algorithm to use (required, currently only `sha256` supported)
- `--output`: Path to output checksum file (required)

### Example Usage

```bash
# Create checksum for a binary file
uv run python -m create_checksum \
  --file target/x86_64-unknown-linux-gnu/release/moved_maker \
  --algo sha256 \
  --output target/x86_64-unknown-linux-gnu/release/moved_maker.sha256
```

### Output Format

The script writes checksum files in the standard format:
```
<hash>  <filename>
```

For example:
```
a1b2c3d4e5f6...  moved_maker
```

The checksum is also printed to stdout for convenience.

### Features

- **Atomic File Writing**: Checksum files are written atomically (write to temporary file, then rename) to prevent partial file corruption if the process is interrupted
- **Parent Directory Creation**: Parent directories for the output file are created automatically if they don't exist
- **Algorithm Selection**: Currently supports SHA256, with infrastructure in place for future algorithm support
- **Error Handling**: Comprehensive error handling for missing files, unreadable files, and invalid algorithms

### Testing

Run tests using pytest:

```bash
uv run pytest
```

For verbose output:

```bash
uv run pytest -v
```

## Constraints and Requirements

- **Python Version**: Requires Python 3.11 or higher
- **Dependencies**: Uses only Python standard library (no external dependencies)
- **Supported Algorithms**: Currently only SHA256 is supported, though the infrastructure supports adding more algorithms in the future

## Integration

The script is integrated into GitHub Actions workflows:
- `release-build.yaml`: Creates checksum files for release artifacts

The script is invoked from the workflow using:

```bash
cd .github/scripts/create-checksum
uv run python -m create_checksum \
  --file <binary_path> \
  --algo sha256 \
  --output <checksum_path>
```
