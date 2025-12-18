# BUG: Cannot Create Checksum in Pull Request Workflow

**Status**: ✅ Complete

## Overview
The `create-checksum` step in the `pull_request.yaml` workflow fails because the binary file cannot be found at the expected path after the rename step.

## Environment
- **OS**: ubuntu-latest (GitHub Actions)
- **Rust Version**: 1.90.0
- **Tool Version**: PR versions (e.g., `0.2.5-pr26+a7d1edb`)
- **Terraform Version**: N/A

## Steps to Reproduce
1. Open a pull request
2. Wait for the `build-binaries` job to run in the `pull_request.yaml` workflow
3. The job reaches the "Create checksum" step
4. The step fails with error: `Error: Binary not found at ../../target/x86_64-unknown-linux-gnu/release/moved_maker-0.2.5-pr26+a7d1edb-linux-x86_64`

## Expected Behavior
The checksum step should successfully find the renamed binary file and create a `.sha256` checksum file.

## Actual Behavior
The checksum step fails because it cannot find the binary file at the expected path, even though the binary was built and should have been renamed in the previous step.

## Error Messages / Output
```
  VERSION="0.2.5-pr26+a7d1edb"
  cd .github/scripts/create-checksum
  uv run python -m create_checksum \
    --file ../../target/x86_64-unknown-linux-gnu/release/moved_maker-${VERSION}-linux-x86_64 \
    --algo sha256 \
    --output ../../target/x86_64-unknown-linux-gnu/release/moved_maker-${VERSION}-linux-x86_64.sha256
  shell: /usr/bin/bash -e {0}
  env:
    CARGO_HOME: /home/runner/.cargo
    CARGO_INCREMENTAL: 0
    CARGO_TERM_COLOR: always
    CACHE_ON_FAILURE: false
    UV_PYTHON_INSTALL_DIR: /home/runner/work/_temp/uv-python-dir
    UV_PYTHON: 3.13
    UV_CACHE_DIR: /home/runner/work/_temp/setup-uv-cache
Downloading cpython-3.13.11-linux-x86_64-gnu (download) (32.7MiB)
 Downloaded cpython-3.13.11-linux-x86_64-gnu (download)
Using CPython 3.13.11
Creating virtual environment at: .venv
   Building create-checksum @ file:///home/runner/work/moved_maker/moved_maker/.github/scripts/create-checksum
      Built create-checksum @ file:///home/runner/work/moved_maker/moved_maker/.github/scripts/create-checksum
Installed 1 package in 0.73ms
Error: Binary not found at ../../target/x86_64-unknown-linux-gnu/release/moved_maker-0.2.5-pr26+a7d1edb-linux-x86_64
```

## Minimal Reproduction Case
The issue occurs in the `build-binaries` job of `.github/workflows/pull_request.yaml`:

1. **Build step** (line 286): `cargo build --release --target ${{ matrix.target }}`
2. **Rename step** (lines 289-292): Renames binary with version
3. **Create checksum step** (lines 299-306): Attempts to create checksum but fails

The rename step uses:
```yaml
- name: Rename binary with version
  run: |
    VERSION="${{ needs.version.outputs.version }}"
    mv target/${{ matrix.target }}/release/moved_maker \
       target/${{ matrix.target }}/release/moved_maker-${VERSION}-${{ matrix.platform }}
```

The checksum step uses:
```yaml
- name: Create checksum
  run: |
    VERSION="${{ needs.version.outputs.version }}"
    cd .github/scripts/create-checksum
    uv run python -m create_checksum \
      --file ../../target/${{ matrix.target }}/release/moved_maker-${VERSION}-${{ matrix.platform }} \
      --algo sha256 \
      --output ../../target/${{ matrix.target }}/release/moved_maker-${VERSION}-${{ matrix.platform }}.sha256
```

## Additional Context
- **Frequency**: Always (occurs on every PR build)
- **Workflow**: `.github/workflows/pull_request.yaml`
- **Job**: `build-binaries`
- **Step**: "Create checksum"
- **Possible causes**:
  1. The rename step may be failing silently (not causing the job to fail)
  2. The binary build step may not be producing the expected output
  3. Path resolution issue when running from `.github/scripts/create-checksum` directory (relative paths may not resolve correctly)
  4. The `mv` command may fail if the source file doesn't exist, but the step doesn't fail the job
  5. Timing issue where the file isn't available yet

- **Fix implemented**:
  1. Added `-v` flag to the `mv` command to make it verbose and show what it's doing
  2. Updated checksum step to use absolute paths by prefixing paths with `${{ github.workspace }}` to avoid path resolution issues when running from `.github/scripts/create-checksum` directory
  3. Added error handling with `set -euo pipefail` and explicit checks to verify the source file exists before rename and destination exists after rename
  4. The rename step now fails early with clear error messages if the binary doesn't exist or the rename fails

- **Implementation details**:
  - The rename step now uses `set -euo pipefail` for strict error handling
  - Source file existence is verified before attempting rename
  - Destination file existence is verified after rename
  - Checksum step uses `${{ github.workspace }}` for absolute paths
  - See implementation plan: `work/25W48/BUG_CREATE_CHECKSUM_BINARY_NOT_FOUND.md`

## Related Issues
- Related requirements: `plan/25W48/REQ_PR_BINARY_BUILDS.md` (introduced PR binary builds)
- Related requirements: `plan/25W48/REQ_CREATE_CHECKSUM_PROJECT.md` (introduced checksum creation)
