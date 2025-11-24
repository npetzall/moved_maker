# BUG: Cargo.lock isn't updated when Cargo.toml version changes

**Status**: ✅ Complete

## Description

The `release-version` script updates the version in `Cargo.toml` but does not update `Cargo.lock` to reflect the new version. Additionally, the workflow only commits `Cargo.toml` but not `Cargo.lock`, leaving the lock file out of sync with the manifest. This can cause build inconsistencies and version mismatches between the manifest and lock file.

## Current State

✅ **FIXED** - All code changes have been implemented. The `__main__.py` script now updates `Cargo.lock` after updating `Cargo.toml`, and the workflow commits both files together.

**Previous (incorrect) state:**
- `update_cargo_version()` function in `cargo.py` updates only `Cargo.toml`
- `Cargo.lock` is not updated after version change
- Workflow commits only `Cargo.toml` (line 72 in `release-version.yaml`)
- `Cargo.lock` remains with the old version number
- Version mismatch between `Cargo.toml` and `Cargo.lock` can cause confusion
- Build tools may report inconsistent version information

**Current (correct) state:**
- `__main__.py` now runs `cargo update --package <package_name>` after updating `Cargo.toml`
- Package name is read dynamically from `Cargo.toml` with fallback to `move_maker`
- `Cargo.lock` is automatically updated when `Cargo.toml` version changes
- Workflow commits both `Cargo.toml` and `Cargo.lock` together (line 72 in `release-version.yaml`)
- Both files are staged together: `git add Cargo.toml Cargo.lock`
- Version information is consistent across both files

**Code location:**
- `.github/scripts/release-version/src/release_version/cargo.py`
  - Function: `update_cargo_version()` (lines 63-121)
  - Only updates `Cargo.toml`, does not update `Cargo.lock`
- `.github/scripts/release-version/src/release_version/__main__.py`
  - Function: `main()` (lines 46-56)
  - Calls `update_cargo_version()` but does not update `Cargo.lock`
- `.github/workflows/release-version.yaml`
  - Step: "Commit, push, and tag version update" (lines 69-76)
  - Only stages `Cargo.toml` with `git add Cargo.toml`
  - Does not stage or commit `Cargo.lock`

**Example scenario:**
- `Cargo.toml` has version `0.1.0`
- `Cargo.lock` has version `0.1.0` in the `[[package]]` section for `move_maker`
- Release workflow calculates new version `0.2.0`
- `Cargo.toml` is updated to `0.2.0`
- `Cargo.lock` still shows `0.1.0` for `move_maker` package
- Workflow commits only `Cargo.toml`
- Repository has inconsistent version information

**Observed behavior:**
```
Updating Cargo.toml with version 0.2.0...
✓ Cargo.toml updated to version 0.2.0
# Cargo.lock is not updated
# Workflow commits only Cargo.toml
git add Cargo.toml
git commit -m "chore: bump version to 0.2.0"
# Cargo.lock remains uncommitted with old version
```

## Expected State

The release workflow should update both `Cargo.toml` and `Cargo.lock` when the version changes, and commit both files together.

**Expected implementation:**
1. After updating `Cargo.toml`, run `cargo update --package move_maker` to update `Cargo.lock`
2. Verify that `Cargo.lock` was updated correctly
3. Stage both `Cargo.toml` and `Cargo.lock` for commit
4. Commit both files together in a single commit
5. Push both files together

**Expected behavior:**
- `Cargo.toml` is updated to new version (e.g., `0.2.0`)
- `Cargo.lock` is updated to new version via `cargo update --package move_maker`
- Both files are staged with `git add Cargo.toml Cargo.lock`
- Both files are committed together: `git commit -m "chore: bump version to 0.2.0"`
- Both files are pushed together
- Version information is consistent across both files

**Proposed solution:**
1. Add `Cargo.lock` update step in `__main__.py` after `Cargo.toml` update
2. Run `cargo update --package move_maker` when version is updated
3. Update workflow to stage both files: `git add Cargo.toml Cargo.lock`
4. Ensure both files are committed and pushed together

## Impact

### Build Consistency Impact
- **Severity**: Medium
- **Priority**: Medium

Without `Cargo.lock` update:
- Version mismatch between `Cargo.toml` and `Cargo.lock` can cause confusion
- Build tools may report inconsistent version information
- Developers may see different versions in different files
- CI/CD builds may have inconsistent version metadata

### Release Process Impact
- **Severity**: Medium
- **Priority**: Medium

- `Cargo.lock` should be committed with version changes for consistency
- Lock file is part of the versioned release state
- Missing `Cargo.lock` update means the release commit doesn't fully reflect the version change
- Future builds may have inconsistent version information

### Developer Experience Impact
- **Severity**: Low
- **Priority**: Low

- Developers may notice version mismatch between files
- May cause confusion about which version is correct
- Minor inconvenience when checking version information

## Root Cause

The `update_cargo_version()` function and the release workflow only handle `Cargo.toml` updates. `Cargo.lock` requires a separate `cargo update` command to sync the version, which is not currently executed. Additionally, the workflow only stages `Cargo.toml` for commit, not `Cargo.lock`.

## Affected Files

- `.github/scripts/release-version/src/release_version/__main__.py`
  - Function: `main()` (add `Cargo.lock` update after `Cargo.toml` update)
- `.github/workflows/release-version.yaml`
  - Step: "Commit, push, and tag version update" (add `Cargo.lock` to `git add` command)

## Investigation Needed

1. [ ] Verify: `cargo update --package move_maker` updates only the package version in `Cargo.lock`
2. [ ] Test: Running `cargo update --package move_maker` after updating `Cargo.toml` version
3. [ ] Verify: `Cargo.lock` version field is updated correctly
4. [ ] Test: Workflow can run `cargo update` command successfully
5. [ ] Verify: Both files are committed together correctly

## Status

✅ **IMPLEMENTED** - All code changes have been implemented. The `__main__.py` script now updates `Cargo.lock` after updating `Cargo.toml`, and the workflow commits both files together. Ready for workflow testing.


## Related Implementation Plan

See `work/25W46/BUG_RELEASE_VERSION_CARGO_LOCK_NOT_UPDATED.md` for the detailed implementation plan.
