# Implementation Plan: Remove Cross-compilation from Release Build

## Overview

Remove cross-compilation from the release build workflow and build only native targets to:
- Eliminate cross-compilation linker errors
- Reduce macOS runner costs (10x more expensive)
- Simplify the build process
- Improve reliability

## Target State

**Build Matrix:**
- `x86_64-unknown-linux-gnu` on `ubuntu-latest` (native)
- `aarch64-apple-darwin` on `macos-latest` (native)

**Removed:**
- `aarch64-unknown-linux-gnu` on `ubuntu-latest` (cross-compile)
- `x86_64-apple-darwin` on `macos-latest` (Rosetta 2)

---

## Phase 1: Update Workflow Matrix

### 1.1 Update build matrix configuration

**File**: `.github/workflows/release-build.yaml`

**Location**: Lines 97-110

**Task**: Update the matrix `include` section to remove cross-compilation targets

- [ ] Open `.github/workflows/release-build.yaml`
- [ ] Locate the `strategy.matrix.include` section (lines 97-110)
- [ ] Remove the `aarch64-unknown-linux-gnu` entry (lines 102-104)
- [ ] Remove the `x86_64-apple-darwin` entry (lines 105-107)
- [ ] Keep only:
  - `x86_64-unknown-linux-gnu` on `ubuntu-latest`
  - `aarch64-apple-darwin` on `macos-latest`
- [ ] Verify the matrix now has exactly 2 entries

**Expected result:**
```yaml
strategy:
  matrix:
    include:
      - os: ubuntu-latest
        target: x86_64-unknown-linux-gnu
        artifact_name: move_maker-linux-x86_64
      - os: macos-latest
        target: aarch64-apple-darwin
        artifact_name: move_maker-macos-aarch64
```

---

## Phase 2: Verify Workflow Steps

### 2.1 Verify Rust installation step

**File**: `.github/workflows/release-build.yaml`

**Location**: Lines 119-123

**Task**: Verify the Rust installation step works correctly with native targets

- [ ] Check that `targets: ${{ matrix.target }}` is still appropriate
- [ ] Verify that for native targets, this will install the correct toolchain
- [ ] Confirm no changes needed (native targets don't require special setup)

**Note**: The `targets` parameter is still needed even for native builds to ensure the correct target is available.

### 2.2 Verify test execution

**File**: `.github/workflows/release-build.yaml`

**Location**: Lines 133-134

**Task**: Verify tests run correctly for native targets

- [ ] Confirm `cargo nextest run` works for native targets without modification
- [ ] Verify no target specification needed (runs for host architecture by default)
- [ ] Confirm test results upload step (lines 144-150) will work correctly

**Note**: Native builds can run tests directly without emulation.

### 2.2.1 Verify test results renaming

**File**: `.github/workflows/release-build.yaml`

**Location**: Lines 136-142

**Task**: Verify test results renaming works with updated matrix

- [ ] Review the renaming step that uses `${{ matrix.artifact_name }}-test.xml`
- [ ] Verify that with the updated matrix, the artifact names will be:
  - `move_maker-linux-x86_64-test.xml` (for Ubuntu build)
  - `move_maker-macos-aarch64-test.xml` (for macOS build)
- [ ] Confirm the renaming logic is dynamic and doesn't need modification
- [ ] Verify the upload step (line 149) uses the correct path: `target/nextest/${{ matrix.artifact_name }}-test.xml`
- [ ] Verify the upload artifact name (line 148) uses `test-results-${{ matrix.os }}-${{ matrix.target }}` which will correctly identify:
  - `test-results-ubuntu-latest-x86_64-unknown-linux-gnu`
  - `test-results-macos-latest-aarch64-apple-darwin`

**Note**: The renaming logic is already dynamic based on `matrix.artifact_name`, so no changes are needed. However, verify that the resulting artifact names are correct and don't conflict.

### 2.3 Verify build step

**File**: `.github/workflows/release-build.yaml`

**Location**: Lines 155-156

**Task**: Verify the build command works for native targets

- [ ] Confirm `cargo auditable build --release --target ${{ matrix.target }}` works for native targets
- [ ] Verify no cross-compilation tooling needed
- [ ] Confirm the target specification is still correct (explicit is better than implicit)

**Note**: Even for native builds, specifying the target explicitly is good practice.

### 2.4 Verify binary renaming step

**File**: `.github/workflows/release-build.yaml`

**Location**: Lines 158-161

**Task**: Verify binary renaming works with updated artifact names

- [ ] Confirm the path `target/${{ matrix.target }}/release/move_maker` is correct
- [ ] Verify `${{ matrix.artifact_name }}` will resolve correctly for remaining targets
- [ ] Confirm no changes needed

### 2.5 Verify artifact upload

**File**: `.github/workflows/release-build.yaml`

**Location**: Lines 177-184

**Task**: Verify artifact upload works with updated matrix

- [ ] Confirm artifact names are correct:
  - `move_maker-linux-x86_64`
  - `move_maker-macos-aarch64`
- [ ] Verify artifact paths are correct
- [ ] Confirm no changes needed

---

## Phase 3: Update Documentation

### 3.1 Update README if it mentions supported platforms

**File**: `README.md`

**Task**: Update any references to supported architectures

- [ ] Search for references to "aarch64", "ARM64", "x86_64-apple-darwin", or "Intel Mac"
- [ ] Update to reflect only supported platforms:
  - Linux AMD64 (x86_64)
  - macOS ARM64 (Apple Silicon)
- [ ] Remove any mentions of cross-compilation
- [ ] Update installation instructions if they reference removed platforms

### 3.2 Update any architecture-specific documentation

**Task**: Check for other documentation that mentions architectures

- [ ] Search for files mentioning "aarch64-unknown-linux-gnu"
- [ ] Search for files mentioning "x86_64-apple-darwin"
- [ ] Update or remove references as appropriate
- [ ] Check `DEVELOPMENT.md`, `CONTRIBUTING.md`, or similar files

---

## Phase 4: Testing

### 4.1 Local testing

**Task**: Test the workflow changes locally if possible

- [ ] Verify the workflow YAML syntax is valid
- [ ] Use `act` or similar tool to test workflow locally (optional)
- [ ] Manually verify the matrix configuration is correct

### 4.2 Create test tag

**Task**: Test the workflow with a test tag

- [ ] Create a test tag (e.g., `v0.0.0-test`)
- [ ] Push the tag to trigger the release workflow
- [ ] Monitor the workflow execution
- [ ] Verify both matrix jobs complete successfully:
  - Ubuntu job builds `x86_64-unknown-linux-gnu`
  - macOS job builds `aarch64-apple-darwin`
- [ ] Verify artifacts are created correctly
- [ ] Verify test results are uploaded
- [ ] Delete the test tag after verification

### 4.3 Verify release artifacts

**Task**: Verify the release artifacts are correct

- [ ] Check that only 2 artifacts are created (not 4)
- [ ] Verify artifact names:
  - `move_maker-linux-x86_64`
  - `move_maker-macos-aarch64`
- [ ] Verify checksums are generated correctly
- [ ] Test downloading and running the binaries (if possible)

---

## Phase 5: Cleanup and Verification

### 5.1 Remove unused references

**Task**: Clean up any code or config that references removed targets

- [ ] Search codebase for "aarch64-unknown-linux-gnu"
- [ ] Search codebase for "x86_64-apple-darwin"
- [ ] Remove or update any hardcoded references
- [ ] Check for any CI/CD scripts that might reference these targets

### 5.2 Update decision document status

**File**: `plan/02_W47/RELEASE_BUILD_CROSS_COMPILATION_LINKER_ERROR.md`

**Task**: Mark the decision as implemented

- [ ] Update status from "DECIDED" to "IMPLEMENTED"
- [ ] Add implementation date
- [ ] Add link to this implementation plan

### 5.3 Verify workflow runs successfully

**Task**: Final verification

- [ ] Confirm workflow runs without errors
- [ ] Verify no cross-compilation errors occur
- [ ] Confirm build times are acceptable
- [ ] Verify cost reduction (fewer macOS runner minutes)
- [ ] Document any issues encountered and resolutions

---

## Phase 6: Post-Implementation

### 6.1 Monitor first real release

**Task**: Monitor the first actual release after changes

- [ ] Watch the workflow execution for the next release
- [ ] Verify all steps complete successfully
- [ ] Confirm artifacts are correct
- [ ] Verify release is created properly
- [ ] Document any issues

### 6.2 Update related documentation

**Task**: Update any user-facing documentation

- [ ] Update installation instructions if needed
- [ ] Update platform support documentation
- [ ] Add note about platform support if users ask about removed platforms

---

## Checklist Summary

### Phase 1: Update Workflow Matrix
- [ ] Update build matrix configuration

### Phase 2: Verify Workflow Steps
- [ ] Verify Rust installation step
- [ ] Verify test execution
- [ ] Verify test results renaming
- [ ] Verify build step
- [ ] Verify binary renaming step
- [ ] Verify artifact upload

### Phase 3: Update Documentation
- [ ] Update README if it mentions supported platforms
- [ ] Update any architecture-specific documentation

### Phase 4: Testing
- [ ] Local testing
- [ ] Create test tag
- [ ] Verify release artifacts

### Phase 5: Cleanup and Verification
- [ ] Remove unused references
- [ ] Update decision document status
- [ ] Verify workflow runs successfully

### Phase 6: Post-Implementation
- [ ] Monitor first real release
- [ ] Update related documentation

---

## Notes

- **Breaking Change**: This removes support for ARM64 Linux and Intel macOS releases
- **Cost Savings**: Reduces macOS runner usage by 50% (from 2 jobs to 1 job)
- **Reliability**: Eliminates cross-compilation complexity and potential errors
- **Testing**: Native builds can be tested directly without emulation overhead

## Related Files

- `.github/workflows/release-build.yaml` - Main workflow file to modify
- `plan/02_W47/RELEASE_BUILD_CROSS_COMPILATION_LINKER_ERROR.md` - Decision document
- `README.md` - May need updates for platform support

## References

- Decision document: `plan/02_W47/RELEASE_BUILD_CROSS_COMPILATION_LINKER_ERROR.md`
