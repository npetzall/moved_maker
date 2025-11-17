# Bug: Release Build Workflow - Incorrect Artifact Paths and Naming Conflicts in Release Creation

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

## Solution

### Recommended Solution: Rename During Build + Merge Multiple + Wildcards

This solution addresses both issues comprehensively:

1. **Rename binaries during build** to have platform-specific names
2. **Upload binary and checksum together** as a single artifact per platform
3. **Use `merge-multiple: true`** when downloading to get a flat directory structure
4. **Use wildcards** in `gh release create` to upload all files

**Benefits:**
- ✅ Solves path issues (flat directory structure)
- ✅ Solves naming conflicts (unique filenames from the start)
- ✅ Simpler workflow (fewer steps, less complexity)
- ✅ Binary and checksum stay together (single artifact per platform)
- ✅ Clean release command (wildcard instead of listing all files)
- ✅ Files have correct names in the GitHub release

**Implementation:**

See "Expected State" section above for complete code changes.

### Alternative Solutions (Not Recommended)

#### Option 1: Fix Paths Only (Doesn't Solve Naming Conflicts)

Update paths to include subdirectory structure, but this doesn't address the naming conflict issue:

```yaml
- name: Create GitHub Release
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    gh release create "${{ github.ref_name }}" \
      --title "Release ${{ github.ref_name }}" \
      --notes-file release_notes.md \
      --verify-tag \
      artifacts/move_maker-linux-x86_64/move_maker \
      artifacts/move_maker-linux-x86_64.sha256/move_maker.sha256 \
      # ... etc
```

**Cons:**
- Doesn't solve naming conflicts (all binaries still named `move_maker`)
- Verbose paths
- Still requires separate artifacts for binary and checksum

#### Option 2: Reorganize After Download

Add a step to move and rename files after download:

```yaml
- name: Reorganize artifacts
  run: |
    for dir in artifacts/*/; do
      if [ -d "$dir" ]; then
        mv "$dir"* artifacts/ 2>/dev/null || true
        rmdir "$dir" 2>/dev/null || true
      fi
    done
    # Rename files to match artifact names
    mv artifacts/move_maker artifacts/move_maker-linux-x86_64 2>/dev/null || true
    # ... repeat for all artifacts
```

**Cons:**
- More complex, requires renaming logic
- Risk of file name conflicts during reorganization
- More error-prone
- Doesn't address the root cause (binaries should be named correctly from the start)

## Testing

### Local Testing

1. **Simulate the build and rename process:**
```bash
# Build for a specific target
cargo build --release --target aarch64-apple-darwin

# Rename binary
mv target/aarch64-apple-darwin/release/move_maker \
   target/aarch64-apple-darwin/release/move_maker-macos-aarch64

# Create checksum
python3 .github/scripts/create-checksum.py \
  target/aarch64-apple-darwin/release/move_maker-macos-aarch64 \
  target/aarch64-apple-darwin/release/move_maker-macos-aarch64.sha256

# Verify files exist with correct names
ls -la target/aarch64-apple-darwin/release/move_maker-macos-aarch64*
```

2. **Simulate artifact download with merge-multiple:**
```bash
# Create artifacts directory structure (simulating merge-multiple: true)
mkdir -p artifacts
cp target/aarch64-apple-darwin/release/move_maker-macos-aarch64 artifacts/
cp target/aarch64-apple-darwin/release/move_maker-macos-aarch64.sha256 artifacts/

# Verify flat structure
ls -la artifacts/

# Test wildcard expansion
echo artifacts/*
```

3. **Verify gh release command would work:**
```bash
# Dry run (won't actually create release)
gh release create "v0.1.0-test" \
  --title "Test Release" \
  --notes "Test" \
  artifacts/* \
  --dry-run || echo "Command would fail"
```

### CI Testing

1. Add a verification step before release creation:
```yaml
- name: Verify artifact files
  run: |
    # Verify all expected files exist with correct names
    expected_files=(
      "move_maker-linux-x86_64"
      "move_maker-linux-x86_64.sha256"
      "move_maker-linux-aarch64"
      "move_maker-linux-aarch64.sha256"
      "move_maker-macos-x86_64"
      "move_maker-macos-x86_64.sha256"
      "move_maker-macos-aarch64"
      "move_maker-macos-aarch64.sha256"
    )

    for file in "${expected_files[@]}"; do
      if [ ! -f "artifacts/$file" ]; then
        echo "::error::File not found: artifacts/$file"
        echo "::error::Expected flat directory structure with unique filenames"
        exit 1
      fi
      echo "✅ Found: artifacts/$file"
    done

    # Verify no duplicate names
    duplicates=$(ls artifacts/ | sort | uniq -d)
    if [ -n "$duplicates" ]; then
      echo "::error::Duplicate filenames found: $duplicates"
      exit 1
    fi

    echo "✅ All files verified with unique names"
```

2. Test with a pre-release tag to verify the fix works end-to-end

## Affected Files

- `.github/workflows/release-build.yaml`
  - **Build job (lines 137-166):**
    - Add rename step after build (after line 138)
    - Update audit command to use renamed binary (line 144)
    - Move checksum creation before upload (after audit step)
    - Update upload to include both binary and checksum (lines 148-166)
  - **Release job (lines 214-242):**
    - Add `merge-multiple: true` to download-artifact (line 217)
    - Update `gh release create` to use wildcard `artifacts/*` (line 235)

## References

- [GitHub Actions: Download workflow artifacts](https://docs.github.com/en/actions/using-workflows/storing-workflow-data-as-artifacts#downloading-workflow-artifacts)
- [actions/download-artifact documentation](https://github.com/actions/download-artifact)
- [GitHub CLI: gh release create](https://cli.github.com/manual/gh_release_create)

## Additional Notes

### Understanding Artifact Structure

When using `download-artifact`:
- If you download a **single artifact by name**, it's placed in the specified path
- If you download **all artifacts** (no `name` specified), each artifact is placed in a subdirectory named after the artifact (default behavior)
- With `merge-multiple: true`, all artifacts are merged into a flat directory structure
- Single-file artifacts maintain their original filename within the artifact subdirectory (unless `merge-multiple: true` is used)

### Version Compatibility

The subdirectory structure behavior is consistent across:
- `download-artifact@v4`
- `download-artifact@v5`
- `download-artifact@v6`

The `merge-multiple` option is available in `download-artifact@v4+` and is the recommended solution for this use case.

### GitHub CLI Wildcard Support

The `gh release create` command supports shell wildcard expansion:
- `artifacts/*` expands to all files in the artifacts directory
- This works with bash/zsh shell expansion
- All matching files are uploaded as release assets

### Binary Naming in Cargo

Cargo builds binaries with the package name by default, regardless of target platform. To have platform-specific names:
- Rename the binary after build (recommended for this use case)
- Or use build scripts to customize output names (more complex)

## Status

✅ **IN PROGRESS** - Implementation started, code changes complete, awaiting testing

## Implementation Plan

### Phase 1: Build Job Changes

#### Step 1: Add rename step after build

1. **Add rename binary step**
   - [x] Add new step after "Build release binary with embedded dependency info" (after line 138)
   - [x] Step name: "Rename binary for platform-specific release"
   - [x] Use `mv` command to rename `move_maker` to `${{ matrix.artifact_name }}`
   - [x] Verify step is placed before audit step

2. **Update audit step**
   - [x] Update "Audit release binary" step (line 144) to use renamed binary path
   - [x] Change path from `target/${{ matrix.target }}/release/move_maker` to `target/${{ matrix.target }}/release/${{ matrix.artifact_name }}`
   - [x] Verify audit command references correct binary name

#### Step 2: Move checksum creation before upload

1. **Move checksum step**
   - [x] Move "Create checksum" step to occur after "Audit release binary" step
   - [x] Update checksum script to use renamed binary: `${{ matrix.artifact_name }}`
   - [x] Update checksum output path to use renamed binary: `${{ matrix.artifact_name }}.sha256`
   - [x] Verify checksum is created for the correctly named binary

#### Step 3: Update artifact upload

1. **Combine binary and checksum upload**
   - [x] Update "Upload artifact" step (lines 148-153) to upload both files
   - [x] Change `path` from single file to multi-line format with both:
     - `target/${{ matrix.target }}/release/${{ matrix.artifact_name }}`
     - `target/${{ matrix.target }}/release/${{ matrix.artifact_name }}.sha256`
   - [x] Remove separate "Upload checksum" step (lines 161-166)
   - [x] Verify artifact name remains `${{ matrix.artifact_name }}`

### Phase 2: Release Job Changes

#### Step 4: Update artifact download

1. **Add merge-multiple option**
   - [x] Update "Download all artifacts" step (lines 214-217)
   - [x] Add `merge-multiple: true` to the `with` section
   - [x] Verify this will create a flat directory structure

#### Step 5: Update release creation

1. **Use wildcard for file upload**
   - [x] Update "Create GitHub Release" step (lines 227-242)
   - [x] Replace all individual file paths with wildcard: `artifacts/*`
   - [x] Verify command will upload all files in artifacts directory
   - [x] Remove all individual file path arguments

### Phase 3: Testing

#### Step 6: Local testing

1. **Test build and rename process**
   - [ ] Build for one target locally:
     ```bash
     cargo build --release --target aarch64-apple-darwin
     ```
   - [ ] Manually rename binary:
     ```bash
     mv target/aarch64-apple-darwin/release/move_maker \
        target/aarch64-apple-darwin/release/move_maker-macos-aarch64
     ```
   - [ ] Create checksum:
     ```bash
     python3 .github/scripts/create-checksum.py \
       target/aarch64-apple-darwin/release/move_maker-macos-aarch64 \
       target/aarch64-apple-darwin/release/move_maker-macos-aarch64.sha256
     ```
   - [ ] Verify both files exist with correct names
   - [ ] Test audit command with renamed binary:
     ```bash
     cargo audit bin target/aarch64-apple-darwin/release/move_maker-macos-aarch64
     ```

2. **Test artifact structure simulation**
   - [ ] Create artifacts directory:
     ```bash
     mkdir -p artifacts
     ```
   - [ ] Copy files to simulate merge-multiple behavior:
     ```bash
     cp target/aarch64-apple-darwin/release/move_maker-macos-aarch64* artifacts/
     ```
   - [ ] Verify flat structure: `ls -la artifacts/`
   - [ ] Test wildcard expansion: `echo artifacts/*`

3. **Test gh release command (dry run)**
   - [ ] Test wildcard expansion with gh CLI:
     ```bash
     gh release create "v0.1.0-test" \
       --title "Test Release" \
       --notes "Test" \
       artifacts/* \
       --dry-run
     ```
   - [ ] Verify command accepts wildcard pattern
   - [ ] Verify all files would be uploaded

#### Step 7: CI verification

1. **Test with test tag**
   - [ ] Create a test tag (e.g., `v0.0.0-test`)
   - [ ] Push tag to trigger release-build workflow
   - [ ] Verify build job completes for all matrix targets:
     - [ ] Linux x86_64
     - [ ] Linux aarch64
     - [ ] macOS x86_64
     - [ ] macOS aarch64
   - [ ] Verify binaries are renamed correctly in each build
   - [ ] Verify checksums are created with correct names
   - [ ] Verify artifacts are uploaded with both binary and checksum

2. **Verify release job**
   - [ ] Verify artifacts download with merge-multiple creates flat structure
   - [ ] Verify all files have unique names (no conflicts)
   - [ ] Verify `gh release create` command succeeds with wildcard
   - [ ] Verify all 8 files (4 binaries + 4 checksums) are uploaded to release
   - [ ] Verify asset names in GitHub release match expected names
   - [ ] Delete test tag after verification

3. **Add verification step (optional)**
   - [ ] Consider adding "Verify artifact files" step before release creation
   - [ ] Verify all expected files exist with correct names
   - [ ] Verify no duplicate filenames
   - [ ] This provides early failure detection if something goes wrong

### Phase 4: Rollback Plan

If issues are encountered:

1. **Immediate Rollback**
   - [ ] Revert changes to `.github/workflows/release-build.yaml`
   - [ ] Restore original build job structure (no rename, separate uploads)
   - [ ] Restore original release job structure (no merge-multiple, explicit paths)
   - [ ] Verify workflow returns to previous working state
   - [ ] Investigate the issue before retrying

2. **Partial Rollback Options**
   - [ ] If rename causes issues: Keep rename but revert to separate artifact uploads
   - [ ] If merge-multiple causes issues: Keep rename but use explicit paths with subdirectories
   - [ ] If wildcard doesn't work: Keep merge-multiple but list files explicitly
   - [ ] If checksum creation fails: Verify Python script works with new paths

3. **Alternative Approaches**
   - [ ] If `merge-multiple: true` is not available: Use reorganization step after download
   - [ ] If wildcards don't work: List all files explicitly in `gh release create`
   - [ ] If rename fails: Consider using symlinks or copying instead of moving

### Implementation Order

1. [x] Update build job: Add rename step after build (after line 138)
2. [x] Update build job: Update audit step to use renamed binary (line 144)
3. [x] Update build job: Move checksum creation before upload (after audit step)
4. [x] Update build job: Update checksum script paths to use renamed binary
5. [x] Update build job: Combine binary and checksum in single upload (lines 148-153)
6. [x] Update build job: Remove separate checksum upload step (lines 161-166)
7. [ ] Test build job changes locally for one target
8. [x] Update release job: Add `merge-multiple: true` to download step (line 217)
9. [x] Update release job: Replace file paths with wildcard in release command (line 235)
10. [ ] Test artifact download and wildcard locally (simulated)
11. [x] Validate YAML syntax of workflow file
12. [ ] Create test branch with all changes
13. [ ] Create test tag to trigger release workflow
14. [ ] Verify build job completes successfully for all matrix targets
15. [ ] Verify binaries are renamed correctly in artifacts
16. [ ] Verify checksums are created correctly
17. [ ] Verify release job downloads artifacts correctly
18. [ ] Verify release job creates release with all files
19. [ ] Verify all 8 files appear in GitHub release with correct names
20. [ ] Clean up test tag
21. [ ] Merge changes to main branch
22. [ ] Verify production workflow runs with real release tag

### Risk Assessment

- **Risk Level:** Medium
- **Impact if Failed:**
  - Release creation could fail if paths are incorrect
  - Binaries might not be uploaded if naming conflicts occur
  - Workflow might fail if YAML syntax is incorrect
  - Artifacts might not download correctly if merge-multiple doesn't work as expected
  - Release might be created with wrong file names or missing files
- **Mitigation:**
  - Changes are incremental and can be tested step-by-step
  - Can test locally before affecting CI
  - Can test with test tag before affecting production releases
  - Easy rollback (revert workflow file)
  - Verification step can catch issues early
  - All changes are in one file (easier to review and revert)
- **Testing:**
  - Can be fully tested locally for build process
  - Can test artifact structure locally
  - Can test with test tag before production
  - Verification commands are straightforward
  - Can add verification step to catch issues early
- **Dependencies:**
  - `merge-multiple` option requires `download-artifact@v4+` (currently using v6, so compatible)
  - `gh release create` wildcard support requires shell expansion (bash/zsh, available on GitHub runners)
  - Python script for checksum creation (already in use)
  - No new dependencies required
- **Performance Considerations:**
  - Minimal performance impact: Rename operation is fast
  - Uploading two files together vs separately has no significant difference
  - `merge-multiple: true` might be slightly faster than default (fewer directory operations)
  - Wildcard expansion is handled by shell (negligible overhead)

### Expected Outcomes

After successful implementation:

- **Path Issues Resolved:** Artifacts download to flat directory structure, eliminating path confusion
- **Naming Conflicts Resolved:** All binaries have unique platform-specific names from the start
- **Simplified Workflow:** Binary and checksum uploaded together as single artifact per platform
- **Cleaner Release Command:** Wildcard pattern instead of listing 8 files explicitly
- **Correct Asset Names:** GitHub release assets have descriptive platform-specific names
- **Better Organization:** Binary and checksum stay together in same artifact
- **Easier Maintenance:** Fewer steps, less complexity, clearer intent
- **Improved Reliability:** No path issues, no naming conflicts, fewer failure points
- **Better User Experience:** Release assets have clear, descriptive names matching release notes
- **Consistent Structure:** All platforms follow same pattern (binary + checksum per artifact)
