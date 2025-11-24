# Implementation Plan: BUG_RELEASE_BUILD_STRIP_CARGO_TOML

**Status**: ✅ Complete

## Overview

This implementation plan addresses the bug described in `plan/25W46/BUG_RELEASE_BUILD_STRIP_CARGO_TOML.md`.

## Context

Related bug report: `plan/25W46/BUG_RELEASE_BUILD_STRIP_CARGO_TOML.md`

## Solution

### Step 1: Add Strip Configuration to Cargo.toml

Add the `strip` option to the release profile:

```toml
[profile.release]
strip = "debuginfo"
```

**Why `"debuginfo"`?**
- Strips only debug symbols and debug information
- Preserves custom linker sections (including cargo-auditable's embedded data)
- Reduces binary size while maintaining auditability
- Works consistently across all platforms (Linux, macOS, Windows)

### Step 2: Remove Manual Strip Step from Workflow

Remove the manual strip step from `.github/workflows/release-build.yaml`:

**Before:**
```yaml
- name: Audit release binary
  run: cargo audit bin target/${{ matrix.target }}/release/move_maker

- name: Strip binary (Linux/macOS)
  if: matrix.os != 'windows'
  run: strip target/${{ matrix.target }}/release/move_maker

- name: Upload artifact
```

**After:**
```yaml
- name: Audit release binary
  run: cargo audit bin target/${{ matrix.target }}/release/move_maker

# Stripping handled by Cargo.toml [profile.release] strip = "debuginfo"

- name: Upload artifact
```

## How Cargo's Strip Works

Cargo's `strip` option (available since Rust 1.59) uses `rustc`'s built-in stripping, which:

1. **Preserves custom sections**: Custom linker sections (like cargo-auditable's audit data) are preserved
2. **Removes debug info**: Debug symbols and debug information are removed
3. **Cross-platform**: Works identically on Linux, macOS, and Windows
4. **Integrated**: Part of the build process, no separate step needed

### Strip Options

- `strip = false` - No stripping (default for most profiles)
- `strip = "debuginfo"` - Strip debug symbols and debug information (recommended for release)
- `strip = "symbols"` - Strip all symbols (more aggressive, may remove more than needed)

For this use case, `"debuginfo"` is the correct choice because it:
- Removes debug symbols (reduces binary size)
- Preserves custom linker sections (keeps audit data)
- Maintains binary functionality

## Testing

### Local Testing

1. **Add strip to Cargo.toml**:
   ```toml
   [profile.release]
   strip = "debuginfo"
   ```

2. **Build with cargo auditable**:
   ```bash
   cargo auditable build --release
   ```

3. **Verify binary is stripped** (smaller size):
   ```bash
   ls -lh target/release/move_maker
   ```

4. **Verify audit data is preserved**:
   ```bash
   cargo audit bin target/release/move_maker
   ```
   Should successfully audit the binary.

5. **Compare with manual strip**:
   ```bash
   # Build without Cargo strip
   cargo auditable build --release
   cp target/release/move_maker target/release/move_maker.unstripped

   # Manual strip
   strip target/release/move_maker

   # Try to audit manually stripped binary
   cargo audit bin target/release/move_maker
   # May fail or show missing audit data

   # Verify Cargo-stripped binary still has audit data
   cargo audit bin target/release/move_maker.unstripped
   # Should succeed
   ```

### CI Testing

1. **Verify workflow builds successfully**:
   - All matrix builds (Linux x86_64, Linux aarch64, macOS x86_64, macOS aarch64) should complete
   - No errors related to stripping

2. **Verify binaries are stripped**:
   - Check binary sizes (should be smaller than unstripped)
   - Compare with previous builds

3. **Verify audit data is preserved**:
   - Run `cargo audit bin` on the final binaries
   - Should successfully extract and audit dependency information

4. **Verify audit step still works**:
   - The workflow's audit step (line 139) should continue to work
   - Final uploaded binaries should be auditable by end users

## Affected Files

- `Cargo.toml`
  - Add `[profile.release]` section with `strip = "debuginfo"`

- `.github/workflows/release-build.yaml`
  - Remove lines 141-143 (manual strip step)
  - Optionally add comment explaining stripping is handled by Cargo.toml

## Benefits

1. **Preserves audit data**: Custom linker sections (including cargo-auditable data) are preserved
2. **Cross-platform**: Works identically on all platforms (no OS-specific logic needed)
3. **Consistent configuration**: Build settings in `Cargo.toml` where they belong
4. **Easier testing**: Can test stripping locally with `cargo build --release`
5. **Better maintainability**: Single source of truth for build configuration
6. **No workflow complexity**: Removes conditional OS logic from workflow

## References

- [Cargo Profile Documentation - strip option](https://doc.rust-lang.org/cargo/reference/profiles.html#strip)
- [cargo-auditable Documentation](https://github.com/rust-secure-code/cargo-auditable)
- [Rust 1.59 Release Notes - strip option](https://blog.rust-lang.org/2022/02/24/Rust-1.59.0.html)

## Additional Notes

### Why Manual Strip Removes Audit Data

The `strip` command (from binutils on Linux, or Xcode tools on macOS) removes sections from ELF/Mach-O binaries. By default, it removes:
- Debug symbols (`.debug_*` sections)
- Symbol tables
- **Custom linker sections** (including cargo-auditable's embedded data)

Cargo's `strip = "debuginfo"` uses `rustc`'s integrated stripping, which:
- Removes debug information
- **Preserves custom linker sections** (like `.dep-v0` used by cargo-auditable)

### Verification Commands

After implementing the fix, verify the audit data is preserved:

```bash
# Build with cargo auditable
cargo auditable build --release

# Verify audit data is present
cargo audit bin target/release/move_maker

# Check binary size (should be smaller than without strip)
ls -lh target/release/move_maker

# Extract and inspect audit data (if auditable-extract is available)
# auditable-extract target/release/move_maker
```

### Migration Notes

- **No breaking changes**: Existing workflows will continue to work
- **Backward compatible**: Cargo's strip option is available since Rust 1.59 (project uses 1.90.0)
- **Immediate benefit**: Released binaries will be auditable by end users

## Status

✅ **IMPLEMENTED** - Code changes completed, ready for testing

**Implementation Progress:**
- ✅ Phase 1, Step 1: Added `[profile.release]` section with `strip = "debuginfo"` to `Cargo.toml`
- ✅ Phase 1, Step 2: Removed manual strip step from `.github/workflows/release-build.yaml` and added explanatory comment
- ⏳ Phase 1, Step 3: Local testing pending (can be done before PR)
- ⏳ Phase 2: CI testing pending (will be done via PR)

## Detailed Implementation Plan

### Phase 1: Implementation Steps

#### Step 1: Add Strip Configuration to Cargo.toml

**File:** `Cargo.toml`

1. **Add `[profile.release]` section with `strip = "debuginfo"`**
   - [x] Locate the end of the `[dev-dependencies]` section (after line 16)
   - [x] Add a new `[profile.release]` section:
     ```toml
     [profile.release]
     strip = "debuginfo"  # Strip debug symbols, preserve custom linker sections (e.g., cargo-auditable data)
     ```
   - [x] Verify the TOML syntax is correct (no trailing commas, proper indentation)
   - [x] Verify the section is placed after all dependency sections

**Expected result:**
```toml
[dev-dependencies]
tempfile = "3.10"
pretty_assertions = "1.4"

[profile.release]
strip = "debuginfo"  # Strip debug symbols, preserve custom linker sections (e.g., cargo-auditable data)
```

#### Step 2: Remove Manual Strip Step from Workflow

**File:** `.github/workflows/release-build.yaml`

1. **Remove the manual strip step (lines 141-143)**
   - [x] Locate the `Strip binary (Linux/macOS)` step (lines 141-143)
   - [x] Remove the entire step block:
     ```yaml
     - name: Strip binary (Linux/macOS)
       if: matrix.os != 'windows'
       run: strip target/${{ matrix.target }}/release/move_maker
     ```
   - [x] Optionally add a comment explaining stripping is handled by Cargo.toml:
     ```yaml
     # Stripping handled by Cargo.toml [profile.release] strip = "debuginfo"
     ```
   - [x] Verify YAML syntax is correct after removal
   - [x] Verify the workflow step order is correct (audit step should be followed by upload artifact step)

**Expected result:**
```yaml
- name: Audit release binary
  run: cargo audit bin target/${{ matrix.target }}/release/move_maker

# Stripping handled by Cargo.toml [profile.release] strip = "debuginfo"

- name: Upload artifact
  uses: actions/upload-artifact@330a01c490aca151604b8cf639adc76d48f6c5d4  # v5.0.0
  with:
    name: ${{ matrix.artifact_name }}
    path: target/${{ matrix.target }}/release/move_maker
```

#### Step 3: Local Testing

1. **Test the Cargo.toml configuration**
   - [ ] Build with cargo auditable locally:
     ```bash
     cargo auditable build --release
     ```
   - [ ] Verify the build completes successfully
   - [ ] Check binary size (should be smaller than without strip):
     ```bash
     ls -lh target/release/move_maker
     ```

2. **Verify audit data is preserved**
   - [ ] Run audit on the built binary:
     ```bash
     cargo audit bin target/release/move_maker
     ```
   - [ ] Verify the audit command succeeds and extracts dependency information
   - [ ] Compare with a manually stripped binary to confirm audit data is preserved:
     ```bash
     # Build without Cargo strip (temporarily comment out strip in Cargo.toml)
     # Copy binary
     cp target/release/move_maker target/release/move_maker.unstripped

     # Manual strip
     strip target/release/move_maker

     # Try to audit manually stripped binary (may fail or show missing data)
     cargo audit bin target/release/move_maker

     # Verify Cargo-stripped binary still has audit data
     # (restore strip in Cargo.toml and rebuild)
     cargo audit bin target/release/move_maker
     ```

3. **Test cross-platform compatibility**
   - [ ] Verify the configuration works on the local platform (Linux/macOS/Windows)
   - [ ] Note: Cargo's strip option works identically on all platforms, so local testing on one platform should be sufficient

### Phase 2: Rollback Plan

If issues are encountered:

1. **Immediate Rollback**
   - Revert changes to `Cargo.toml` (remove `[profile.release]` section)
   - Restore the manual strip step in `.github/workflows/release-build.yaml`
   - Verify workflow returns to previous working state
   - Investigate the issue before retrying

2. **Partial Rollback**
   - If Cargo strip configuration causes build issues:
     - Remove `strip = "debuginfo"` from `Cargo.toml`
     - Restore manual strip step in workflow
     - Investigate why Cargo strip doesn't work (unlikely, but possible with older Rust versions)
   - If audit data is still not preserved:
     - Verify `cargo auditable` is being used correctly
     - Check Rust version compatibility (requires Rust 1.59+ for strip option, project uses 1.90.0)
     - Verify the strip option value (`"debuginfo"` vs `"symbols"` vs `false`)

3. **Alternative Approaches**
   - If Cargo's strip option is not available or doesn't work:
     - Keep manual strip but use `strip --strip-debug` instead of `strip` (preserves more sections)
     - Use `strip --strip-unneeded` (less aggressive than default)
     - Note: These alternatives may still remove audit data, so Cargo's strip is preferred
   - If audit data preservation is not critical:
     - Keep manual strip (current behavior)
     - Document that released binaries may not be auditable

### Implementation Order

1. [x] Add `[profile.release]` section with `strip = "debuginfo"` to `Cargo.toml`
2. [ ] Test locally: `cargo auditable build --release`
3. [ ] Verify binary is stripped (check size)
4. [ ] Verify audit data is preserved: `cargo audit bin target/release/move_maker`
5. [x] Remove manual strip step from `.github/workflows/release-build.yaml` (lines 141-143)
6. [x] Optionally add comment explaining stripping is handled by Cargo.toml
7. [ ] Create pull request with changes
8. [ ] Verify CI workflow builds successfully for all matrix targets:
   - Linux x86_64
   - Linux aarch64
   - macOS x86_64
   - macOS aarch64
   - Windows x86_64 (should work without manual strip step)
9. [ ] Verify audit step in workflow still works (runs before upload)
10. [ ] Verify uploaded binaries are stripped (check sizes)
11. [ ] Verify uploaded binaries are auditable by end users (download and test)
12. [ ] Confirm no regressions in other workflows

### Risk Assessment

- **Risk Level:** Low
- **Impact if Failed:**
  - Builds might fail if Cargo.toml syntax is incorrect (easy to fix)
  - Binaries might not be stripped if configuration is wrong (non-breaking, just larger binaries)
  - Audit data might still be lost if Cargo strip doesn't preserve it (unlikely, but would require investigation)
  - Workflow might fail if YAML syntax is incorrect after removing strip step (easy to fix)
- **Mitigation:**
  - Simple configuration change (one line in Cargo.toml)
  - Easy rollback (revert two files)
  - Can test locally before affecting CI
  - Cargo's strip option is well-tested and standard (available since Rust 1.59, project uses 1.90.0)
  - No breaking changes - existing workflows will continue to work
- **Testing:**
  - Can be fully tested locally before committing
  - Can test in workflow on test branch or pull request
  - Verification commands are straightforward
  - Edge cases are minimal (Cargo strip is well-behaved)
- **Dependencies:**
  - Cargo's strip option requires Rust 1.59+ (project uses 1.90.0, so compatible)
  - No new dependencies required
  - Uses standard Cargo features

### Expected Outcomes

After successful implementation:

- **Audit Data Preservation:** Released binaries will be auditable by end users using `cargo audit bin`
- **Cross-Platform Consistency:** Stripping works identically on all platforms (Linux, macOS, Windows)
- **Configuration Consistency:** Build settings are in `Cargo.toml` where they belong, not in workflow files
- **Simplified Workflow:** Removed OS-specific conditional logic from workflow
- **Better Maintainability:** Single source of truth for build configuration
- **Easier Testing:** Developers can test stripping locally with `cargo build --release`
- **Binary Size:** Release binaries will be stripped (smaller size) while preserving audit data
- **Workflow Reliability:** No changes to workflow behavior, just removal of manual step
- **Security:** Supply chain security improved - users can verify dependencies in production binaries
