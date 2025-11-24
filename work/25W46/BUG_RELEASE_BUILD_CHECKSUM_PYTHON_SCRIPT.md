# Implementation Plan: BUG_RELEASE_BUILD_CHECKSUM_PYTHON_SCRIPT

**Status**: ✅ Complete

## Overview

This implementation plan addresses the bug described in `plan/25W46/BUG_RELEASE_BUILD_CHECKSUM_PYTHON_SCRIPT.md`.

## Context

Related bug report: `plan/25W46/BUG_RELEASE_BUILD_CHECKSUM_PYTHON_SCRIPT.md`

## Solution

Create a separate Python script file at `.github/scripts/create-checksum.py`:

```python
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
```

Then in the workflow:
```yaml
- name: Create checksum
  run: |
    python3 .github/scripts/create-checksum.py \
      target/${{ matrix.target }}/release/move_maker \
      target/${{ matrix.target }}/release/move_maker.sha256
```

**Benefits:**
- Reusable script
- Can be tested independently
- Can be extended with features
- Cleaner workflow YAML
- Better error handling than shell script
- Cross-platform compatibility

## Implementation Details

### Checksum Format

The script should produce output in the standard format:
```
<hash>  <filename>
```

Example:
```
a1b2c3d4e5f6...  move_maker
```

This matches the format produced by `sha256sum` and `shasum -a 256`.

### Error Handling

The Python script should:
- Check if binary file exists before reading
- Handle file read errors gracefully
- Handle file write errors gracefully
- Exit with non-zero code on errors
- Print error messages to stderr

### Python Availability

Python 3 is available by default on GitHub Actions runners:
- **Ubuntu runners**: Python 3.x pre-installed
- **macOS runners**: Python 3.x pre-installed
- **Windows runners**: Python 3.x pre-installed

No additional setup step is required.

## Testing

### Local Testing

Test the Python script locally:

```bash
# Create a test binary
echo "test binary" > test_binary

# Test the script
python3 .github/scripts/create-checksum.py \
  test_binary \
  test_binary.sha256

# Verify checksum file was created
cat test_binary.sha256

# Verify format matches sha256sum
sha256sum test_binary
```

### CI Testing

1. **Test on all matrix platforms**:
   - Ubuntu (x86_64, aarch64)
   - macOS (x86_64, aarch64)

2. **Verify checksum format**:
   - Checksum file should match standard format
   - Checksum should match output from `sha256sum` or `shasum -a 256`

3. **Verify error handling**:
   - Test with missing binary file
   - Test with read-only directory (should fail gracefully)

## Affected Files

- `.github/workflows/release-build.yaml`
  - Lines 155-159: ✅ Replaced shell-based checksum creation with Python script call
- `.github/scripts/create-checksum.py`
  - ✅ New file created: Python script for checksum generation

## Benefits

1. **Cross-platform**: Works identically on all operating systems
2. **No OS detection**: Eliminates need for `if command -v sha256sum` checks
3. **Better error handling**: Python provides better error messages and handling
4. **Maintainability**: Single implementation instead of OS-specific branches
5. **Consistency**: Same output format across all platforms
6. **Extensibility**: Easy to add features like verification, multiple algorithms, etc.

## References

- [Python hashlib documentation](https://docs.python.org/3/library/hashlib.html)
- [GitHub Actions: Python setup](https://docs.github.com/en/actions/guides/building-and-testing-python)
- [SHA256 checksum format](https://en.wikipedia.org/wiki/SHA-2)

## Additional Notes

### Python Version

GitHub Actions runners include Python 3 by default:
- Ubuntu: Python 3.8+ (varies by runner version)
- macOS: Python 3.8+ (varies by runner version)
- Windows: Python 3.8+ (varies by runner version)

The script uses `python3` which is available on all runners. No `setup-python` action is needed.

### Checksum Format Compatibility

The output format (`<hash>  <filename>`) matches:
- `sha256sum` output format (Linux)
- `shasum -a 256` output format (macOS)
- Standard checksum file format

This ensures compatibility with existing tooling that reads checksum files.

### Performance

Python's `hashlib` is efficient and handles large files well:
- Uses buffered reading (4096 bytes at a time)
- Memory efficient for large binaries
- Performance is comparable to native tools

## Status

✅ **IMPLEMENTED** - Code changes completed, ready for testing

**Implementation Progress:**
- ✅ Phase 1, Step 1: Created `.github/scripts/create-checksum.py` with full implementation
- ✅ Phase 1, Step 2: Updated `.github/workflows/release-build.yaml` to use Python script
- ⏳ Phase 1, Step 3: Local testing pending (can be done before PR)
- ⏳ Phase 2: CI testing pending (will be done via PR)

## Detailed Implementation Plan

### Phase 1: Implementation Steps

#### Step 1: Create Python Script for Checksum Generation

**File:** `.github/scripts/create-checksum.py`

1. **Create the script file**
   - [x] Create directory `.github/scripts/` if it doesn't exist
   - [x] Create new file `.github/scripts/create-checksum.py`
   - [x] Add shebang line: `#!/usr/bin/env python3`
   - [x] Add docstring describing the script's purpose
   - [x] Import required modules: `hashlib`, `sys`, `os`, `argparse`

2. **Implement `calculate_sha256` function**
   - [x] Create function that takes `file_path` as parameter
   - [x] Initialize `hashlib.sha256()` hash object
   - [x] Open file in binary mode (`"rb"`)
   - [x] Read file in 4096-byte chunks using `iter(lambda: f.read(4096), b"")`
   - [x] Update hash with each chunk
   - [x] Return hex digest of the hash
   - [x] Add docstring to function

3. **Implement `main` function**
   - [x] Create argument parser with description
   - [x] Add `binary` positional argument (path to binary file)
   - [x] Add `output` positional argument (path to checksum file)
   - [x] Parse arguments
   - [x] Verify binary file exists using `os.path.exists()`
   - [x] Exit with error code 1 if binary doesn't exist, print error to stderr
   - [x] Call `calculate_sha256` in try-except block
   - [x] Handle `IOError` exceptions, print error to stderr, exit with code 1
   - [x] Extract filename from binary path using `os.path.basename()`
   - [x] Format checksum line: `f"{hash_hex}  {filename}\n"`
   - [x] Write checksum file in try-except block
   - [x] Handle `IOError` exceptions when writing, print error to stderr, exit with code 1
   - [x] Print checksum line to stdout (without newline, using `end=""`)
   - [x] Exit with code 0 on success

4. **Add main guard**
   - [x] Add `if __name__ == "__main__":` block
   - [x] Call `main()` function

5. **Verify script syntax and structure**
   - [x] Run `python3 -m py_compile .github/scripts/create-checksum.py` to check syntax
   - [x] Verify script is executable (optional, for local use)
   - [x] Verify all imports are standard library (no external dependencies)

**Expected result:**
```python
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
```

#### Step 2: Update Workflow to Use Python Script

**File:** `.github/workflows/release-build.yaml`

1. **Replace the checksum creation step (lines 147-156)**
   - [x] Locate the `Create checksum` step (lines 147-156)
   - [x] Remove the entire shell-based step:
     ```yaml
     - name: Create checksum
       shell: bash
       run: |
         cd target/${{ matrix.target }}/release
         if command -v sha256sum >/dev/null 2>&1; then
           sha256sum move_maker > move_maker.sha256
         else
           shasum -a 256 move_maker > move_maker.sha256
         fi
         cat move_maker.sha256
     ```
   - [x] Replace with Python script call:
     ```yaml
     - name: Create checksum
       run: |
         python3 .github/scripts/create-checksum.py \
           target/${{ matrix.target }}/release/move_maker \
           target/${{ matrix.target }}/release/move_maker.sha256
     ```
   - [x] Verify YAML syntax is correct (proper indentation, no trailing backslashes issues)
   - [x] Verify the step order is correct (after build, before upload checksum)

**Expected result:**
```yaml
- name: Create checksum
  run: |
    python3 .github/scripts/create-checksum.py \
      target/${{ matrix.target }}/release/move_maker \
      target/${{ matrix.target }}/release/move_maker.sha256

- name: Upload checksum
  uses: actions/upload-artifact@30a01c490aca151604b8cf639adc76d48f6c5d4  # v5.0.0
  with:
    name: ${{ matrix.artifact_name }}.sha256
    path: target/${{ matrix.target }}/release/move_maker.sha256
    retention-days: 1
```

#### Step 3: Local Testing

1. **Test the Python script locally**
   - [ ] Create a test binary file:
     ```bash
     echo "test binary content" > test_binary
     ```
   - [ ] Run the script:
     ```bash
     python3 .github/scripts/create-checksum.py test_binary test_binary.sha256
     ```
   - [ ] Verify script exits with code 0
   - [ ] Verify checksum file is created: `test_binary.sha256`
   - [ ] Verify checksum file format matches standard format:
     ```bash
     cat test_binary.sha256
     # Should output: <hash>  test_binary
     ```
   - [ ] Verify checksum matches native tool output:
     ```bash
     # Compare with sha256sum (Linux) or shasum -a 256 (macOS)
     sha256sum test_binary  # or: shasum -a 256 test_binary
     # The hash should match the first part of the checksum file
     ```

2. **Test error handling**
   - [ ] Test with missing binary file:
     ```bash
     python3 .github/scripts/create-checksum.py nonexistent_file output.sha256
     # Should exit with code 1 and print error to stderr
     ```
   - [ ] Test with read-only directory (if possible):
     ```bash
     chmod 555 test_dir
     python3 .github/scripts/create-checksum.py test_binary test_dir/output.sha256
     # Should exit with code 1 and print error to stderr
     chmod 755 test_dir  # Restore permissions
     ```

3. **Test with actual binary (if available)**
   - [ ] Build the project locally:
     ```bash
     cargo build --release
     ```
   - [ ] Run script on actual binary:
     ```bash
     python3 .github/scripts/create-checksum.py \
       target/release/move_maker \
       target/release/move_maker.sha256
     ```
   - [ ] Verify checksum file is created and format is correct
   - [ ] Compare with native tool output to verify hash matches

### Phase 2: Rollback Plan

If issues are encountered:

1. **Immediate Rollback**
   - Revert changes to `.github/workflows/release-build.yaml` (restore shell-based checksum step)
   - Remove `.github/scripts/create-checksum.py` if created
   - Verify workflow returns to previous working state
   - Investigate the issue before retrying

2. **Partial Rollback**
   - If Python script has bugs:
     - Fix script issues and retest locally
     - Verify script works on all platforms (Linux, macOS)
     - Re-test in workflow
   - If workflow integration has issues:
     - Verify Python 3 is available on runners (should be by default)
     - Check script path is correct: `.github/scripts/create-checksum.py`
     - Verify script arguments are correct (binary path, output path)
     - Check YAML syntax and indentation
   - If checksum format doesn't match:
     - Verify script output format matches `sha256sum`/`shasum -a 256` format
     - Check filename extraction logic
     - Verify spacing in checksum line (two spaces between hash and filename)

3. **Alternative Approaches**
   - If Python script doesn't work on all platforms:
     - Verify Python 3 is available (should be by default on GitHub Actions runners)
     - Consider using `python` instead of `python3` (though `python3` is preferred)
     - Check if script needs to be made executable (not required for `python3` invocation)
   - If checksum format compatibility issues:
     - Verify script produces exact format: `<hash>  <filename>\n`
     - Compare with native tool output character-by-character
     - Ensure filename matches exactly (no path components)

### Implementation Order

1. [x] Create `.github/scripts/create-checksum.py` with full implementation
2. [ ] Test script locally with test binary
3. [ ] Verify checksum format matches native tools
4. [ ] Test error handling (missing file, permission errors)
5. [ ] Test with actual project binary (if available locally)
6. [x] Update `.github/workflows/release-build.yaml` to use Python script
7. [ ] Create pull request with changes
8. [ ] Verify CI workflow builds successfully for all matrix targets:
   - Linux x86_64
   - Linux aarch64
   - macOS x86_64
   - macOS aarch64
9. [ ] Verify checksum creation step completes successfully on all platforms
10. [ ] Verify checksum files are created and uploaded correctly
11. [ ] Verify checksum format matches standard format (download and inspect artifacts)
12. [ ] Verify checksum values match expected format (compare with native tools if possible)
13. [ ] Confirm no regressions in release workflow
14. [ ] Verify checksum files can be used by standard tools (e.g., `sha256sum -c`)

### Risk Assessment

- **Risk Level:** Low
- **Impact if Failed:**
  - Workflow might fail if Python script has syntax errors (easy to fix)
  - Checksum files might not be created if script fails (workflow will fail, easy to detect)
  - Checksum format might not match standard format (would break compatibility, but easy to fix)
  - Script might not work on all platforms (unlikely, Python 3 is standard on all runners)
- **Mitigation:**
  - Simple script using only standard library (no external dependencies)
  - Can be fully tested locally before committing
  - Easy rollback (revert two files)
  - Python 3 is available by default on all GitHub Actions runners
  - Script follows standard checksum format (compatible with existing tools)
  - Error handling included (exits with proper codes, prints errors to stderr)
- **Testing:**
  - Can be fully tested locally before affecting CI
  - Can test script independently of workflow
  - Can verify checksum format matches native tools
  - Can test error handling scenarios
  - Can test in workflow on test branch or pull request
  - Verification commands are straightforward
- **Dependencies:**
  - Python 3 (available by default on all GitHub Actions runners)
  - Standard library only (`hashlib`, `sys`, `os`, `argparse`)
  - No external dependencies required
  - No additional setup steps needed

### Expected Outcomes

After successful implementation:

- **Cross-Platform Compatibility:** Checksum creation works identically on all platforms (Linux, macOS, Windows)
- **Simplified Workflow:** Removed OS-specific conditional logic (`if command -v sha256sum`)
- **Better Error Handling:** Python provides clearer error messages and proper exit codes
- **Consistent Output:** Same checksum format across all platforms
- **Maintainability:** Single implementation instead of OS-specific branches
- **Testability:** Script can be tested independently of workflow
- **Extensibility:** Easy to add features like verification, multiple hash algorithms, etc.
- **Workflow Reliability:** No changes to workflow behavior, just replacement of implementation
- **Compatibility:** Checksum files remain compatible with existing tooling (sha256sum, shasum, etc.)
