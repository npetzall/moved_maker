# BUG: Release Build Workflow - Incorrect Artifact Paths and Naming Conflicts in Release Creation

**Status**: ✅ Complete

## Description

The `release-build.yaml` workflow has two critical issues:

1. **Incorrect Artifact Paths**: When `download-artifact` downloads artifacts, each artifact is placed in a subdirectory named after the artifact. However, the workflow references the artifact names directly as file paths, which will cause the release creation to fail because the files are actually located in subdirectories.

2. **Naming Conflicts**: All binaries are built with the same name (`move_maker`), which will cause conflicts when uploading to GitHub releases. The `gh release create` command uses the basename of each file as the asset name, so multiple files named `move_maker` would overwrite each other or fail to upload.

## Current State

**File**: `.github/workflows/release-build.yaml`

### Artifact Upload (lines 145-168)

The workflow uploads single files as artifacts:
```yaml
- name: Upload artifact
  uses: actions/upload-artifact@330a01c490aca151604b8cf639adc76d48f6c5d4  # v5.0.0
  with:
    name: ${{ matrix.artifact_name }}
    path: target/${{ matrix.target }}/release/move_maker
    retention-days: 1

- name: Upload checksum
  uses: actions/upload-artifact@30a01c490aca151604b8cf639adc76d48f6c5d4  # v5.0.0
  with:
    name: ${{ matrix.artifact_name }}.sha256
    path: target/${{ matrix.target }}/release/move_maker.sha256
    retention-days: 1
```

**Artifacts created:**
- `move_maker-linux-x86_64` (contains file `move_maker`)
- `move_maker-linux-x86_64.sha256` (contains file `move_maker.sha256`)
- `move_maker-linux-aarch64` (contains file `move_maker`)
- `move_maker-linux-aarch64.sha256` (contains file `move_maker.sha256`)
- `move_maker-macos-x86_64` (contains file `move_maker`)
- `move_maker-macos-x86_64.sha256` (contains file `move_maker.sha256`)
- `move_maker-macos-aarch64` (contains file `move_maker`)
- `move_maker-macos-aarch64.sha256` (contains file `move_maker.sha256`)

### Artifact Download (lines 216-219)

The workflow downloads all artifacts:
```yaml
- name: Download all artifacts
  uses: actions/download-artifact@018cc2cf5baa6db3ef3c5f8a56943fffe632ef53  # v6.0.0
  with:
    path: artifacts
```

**Actual file structure after download:**
```
artifacts/
  ├── move_maker-linux-x86_64/
  │   └── move_maker
  ├── move_maker-linux-x86_64.sha256/
  │   └── move_maker.sha256
  ├── move_maker-linux-aarch64/
  │   └── move_maker
  ├── move_maker-linux-aarch64.sha256/
  │   └── move_maker.sha256
  ├── move_maker-macos-x86_64/
  │   └── move_maker
  ├── move_maker-macos-x86_64.sha256/
  │   └── move_maker.sha256
  ├── move_maker-macos-aarch64/
  │   └── move_maker
  └── move_maker-macos-aarch64.sha256/
      └── move_maker.sha256
```

### Release Creation (lines 221-236)

The workflow references incorrect paths:
```yaml
- name: Create GitHub Release
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    gh release create "${{ github.ref_name }}" \
      --title "Release ${{ github.ref_name }}" \
      --notes-file release_notes.md \
      --verify-tag \
      artifacts/move_maker-linux-x86_64 \
      artifacts/move_maker-linux-x86_64.sha256 \
      artifacts/move_maker-linux-aarch64 \
      artifacts/move_maker-linux-aarch64.sha256 \
      artifacts/move_maker-macos-x86_64 \
      artifacts/move_maker-macos-x86_64.sha256 \
      artifacts/move_maker-macos-aarch64 \
      artifacts/move_maker-macos-aarch64.sha256
```

**Problems:**
1. These paths reference directories, not files. The actual files are located in subdirectories.
2. Even if paths were fixed, all binaries are named `move_maker`, which would cause naming conflicts in the GitHub release (only the last uploaded file would remain).

## Expected State

The workflow should:

1. **Rename binaries during build** to have platform-specific names (e.g., `move_maker-linux-x86_64`)
2. **Upload binary and checksum together** as a single artifact per platform
3. **Use `merge-multiple: true`** when downloading artifacts to get a flat directory structure
4. **Use wildcards** in `gh release create` to upload all files at once

### Build Job Changes

```yaml
- name: Build release binary with embedded dependency info
  run: cargo auditable build --release --target ${{ matrix.target }}

- name: Rename binary for platform-specific release
  run: |
    mv target/${{ matrix.target }}/release/move_maker \
       target/${{ matrix.target }}/release/${{ matrix.artifact_name }}

- name: Install cargo-audit for binary auditing
  run: cargo install cargo-audit

- name: Audit release binary
  run: cargo audit bin target/${{ matrix.target }}/release/${{ matrix.artifact_name }}

# Stripping handled by Cargo.toml [profile.release] strip = "debuginfo"

- name: Create checksum
  run: |
    python3 .github/scripts/create-checksum.py \
      target/${{ matrix.target }}/release/${{ matrix.artifact_name }} \
      target/${{ matrix.target }}/release/${{ matrix.artifact_name }}.sha256

- name: Upload artifact (binary and checksum)
  uses: actions/upload-artifact@330a01c490aca151604b8cf639adc76d48f6c5d4  # v5.0.0
  with:
    name: ${{ matrix.artifact_name }}
    path: |
      target/${{ matrix.target }}/release/${{ matrix.artifact_name }}
      target/${{ matrix.target }}/release/${{ matrix.artifact_name }}.sha256
    retention-days: 1
```

### Release Job Changes

```yaml
- name: Download all artifacts
  uses: actions/download-artifact@018cc2cf5baa6db3ef3c5f8a56943fffe632ef53  # v6.0.0
  with:
    path: artifacts
    merge-multiple: true

- name: Create GitHub Release
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    gh release create "${{ github.ref_name }}" \
      --title "Release ${{ github.ref_name }}" \
      --notes-file release_notes.md \
      --verify-tag \
      artifacts/*
```

**Result:** All files will be in a flat `artifacts/` directory with unique names, and `gh release create` will upload them all using the wildcard pattern.

## Impact

### Workflow Reliability Impact
- **Severity**: High
- **Priority**: High

- Release creation will fail because files don't exist at the specified paths
- GitHub releases will not be created, blocking the release process
- No error message will clearly indicate the path issue (gh CLI will just say files don't exist)

### User Experience Impact
- **Severity**: High
- **Priority**: High

- Releases will not be published
- Users cannot download release binaries
- Release process appears to complete but fails silently at the final step

## Root Cause

### Issue 1: Artifact Path Structure

The `download-artifact` action (v4+) places each downloaded artifact in its own subdirectory named after the artifact. When a single file is uploaded as an artifact, it is downloaded into a subdirectory with the artifact name, and the file retains its original name within that subdirectory.

**Example:**
- Upload: `name: move_maker-linux-x86_64`, `path: target/.../move_maker` (single file)
- Download: Creates `artifacts/move_maker-linux-x86_64/move_maker`
- Workflow expects: `artifacts/move_maker-linux-x86_64` (incorrect - this is a directory)

### Issue 2: Binary Naming Conflicts

Cargo builds all binaries with the same name (`move_maker`) regardless of target platform. When `gh release create` uploads files, it uses the basename as the asset name. Multiple files with the same basename would:
- Overwrite each other (only the last one remains)
- Or fail to upload if GitHub detects the conflict

**Example:**
- All platforms produce: `move_maker`
- `gh release create` sees: 4 files all named `move_maker`
- Result: Only one asset in the release, or upload failure


## Related Implementation Plan

See `work/25W46/BUG_RELEASE_BUILD_ARTIFACT_PATH_ISSUE.md` for the detailed implementation plan.
