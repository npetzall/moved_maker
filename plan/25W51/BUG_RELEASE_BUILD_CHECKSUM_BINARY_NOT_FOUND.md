# BUG: Cannot Create Checksum in Release Build Workflow

**Status**: ✅ Complete

## Overview
The `create-checksum` step in the `release-build.yaml` workflow fails because the binary file cannot be found at the expected path. This is the same issue that was fixed in `pull_request.yaml` - the checksum step uses relative paths that don't resolve correctly when running from the `.github/scripts/create-checksum` directory.

## Environment
- **OS**: ubuntu-latest, macos-latest (GitHub Actions)
- **Rust Version**: 1.90.0
- **Tool Version**: Release versions (e.g., `v0.2.5`)
- **Terraform Version**: N/A

## Steps to Reproduce
1. Trigger a release build workflow (by pushing a version tag to main)
2. Wait for the `build-and-release` job to run in the `release-build.yaml` workflow
3. The job reaches the "Create checksum" step
4. The step fails with error: `Error: Binary not found at ../../target/...`

## Expected Behavior
The checksum step should successfully find the renamed binary file and create a `.sha256` checksum file.

## Actual Behavior
The checksum step fails because it cannot find the binary file at the expected path, even though the binary was built and should have been renamed in the previous step.

## Error Messages / Output
```
cd .github/scripts/create-checksum
uv run python -m create_checksum \
  --file ../../target/${{ matrix.target }}/release/${{ matrix.artifact_name }} \
  --algo sha256 \
  --output ../../target/${{ matrix.target }}/release/${{ matrix.artifact_name }}.sha256
Error: Binary not found at ../../target/...
```

## Minimal Reproduction Case
The issue occurs in the `build-and-release` job of `.github/workflows/release-build.yaml`:

1. **Build step** (line 225): `cargo auditable build --release --target ${{ matrix.target }}`
2. **Rename step** (lines 227-230): Renames binary for platform-specific release
3. **Create checksum step** (lines 240-246): Attempts to create checksum but fails

The rename step uses:
```yaml
- name: Rename binary for platform-specific release
  run: |
    mv target/${{ matrix.target }}/release/moved_maker \
       target/${{ matrix.target }}/release/${{ matrix.artifact_name }}
```

The checksum step uses:
```yaml
- name: Create checksum
  run: |
    cd .github/scripts/create-checksum
    uv run python -m create_checksum \
      --file ../../target/${{ matrix.target }}/release/${{ matrix.artifact_name }} \
      --algo sha256 \
      --output ../../target/${{ matrix.target }}/release/${{ matrix.artifact_name }}.sha256
```

## Additional Context
- **Frequency**: Always (occurs on every release build)
- **Workflow**: `.github/workflows/release-build.yaml`
- **Job**: `build-and-release`
- **Step**: "Create checksum"
- **Root cause**: Path resolution issue when running from `.github/scripts/create-checksum` directory - relative paths like `../../target/...` may not resolve correctly
- **Same issue fixed in**: `plan/25W48/BUG_CREATE_CHECKSUM_BINARY_NOT_FOUND.md` (pull_request.yaml workflow)
- **Fix approach**: Use absolute paths by prefixing paths with `${{ github.workspace }}` in the checksum step, similar to the fix applied in `pull_request.yaml`
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
  - See implementation plan: `work/25W51/BUG_RELEASE_BUILD_CHECKSUM_BINARY_NOT_FOUND.md`

## Related Issues
- Related bug (same issue, different workflow): `plan/25W48/BUG_CREATE_CHECKSUM_BINARY_NOT_FOUND.md` (fixed in pull_request.yaml)
- Related implementation plan: `work/25W48/BUG_CREATE_CHECKSUM_BINARY_NOT_FOUND.md` (shows the fix pattern)
