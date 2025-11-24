# BUG: release-version doesn't calculate version when no tags exist

**Status**: ✅ Complete

## Description

The `release-version` script doesn't calculate a new version when no git tags exist (first release scenario). Instead, it returns the version from `Cargo.toml` unchanged, even when there are merged PRs with version labels or commits that should trigger a version bump. This causes the first release to use the base version (e.g., `0.1.0`) without considering PR labels or commit count, resulting in no version update when one is expected.

## Current State

✅ **IMPLEMENTATION COMPLETE** - All code changes have been implemented. The `calculate_new_version()` function now calculates versions for both tagged and untagged scenarios. All functions have been updated with proper logging. Ready for testing.

**Current (incorrect) state:**
- `calculate_new_version()` function in `version.py` checks for latest tag
- If no tag exists, it immediately returns the version from `Cargo.toml` without any calculation
- No PR label analysis is performed
- No commit counting is performed
- No version bump calculation occurs
- The function returns early at line 197: `return (version, f"v{version}")`
- This causes `update_cargo_version()` to detect no change and skip the update
- Workflow completes successfully but no version bump occurs

**Code location:**
- `.github/scripts/release-version/src/release_version/version.py`
- Function: `calculate_new_version()` (lines 173-233)
- Current implementation (lines 190-197):
  ```python
  if not latest_tag:
      # First release - use version from Cargo.toml
      cargo_path = f"{repo_path}/Cargo.toml" if repo_path != "." else "Cargo.toml"
      version = read_cargo_version(cargo_path)
      print(
          f"No previous tag found (first release), using base version from Cargo.toml: {version}"
      )
      return (version, f"v{version}")  # ❌ Returns without calculation
  ```

**Example scenario:**
- No tags exist in repository
- `Cargo.toml` has version `0.1.0`
- 40+ commits exist modifying application code (`src/`, `Cargo.toml`, `Cargo.lock`)
- Multiple PRs have been merged (some may have `version: minor` or `version: major` labels)
- Current behavior: Version remains `0.1.0`, no version bump occurs
- Expected behavior: Version should be calculated based on PR labels and/or commit count

**Observed behavior:**
```
No previous tag found (first release), using base version from Cargo.toml: 0.1.0
Cargo.toml version is already 0.1.0, no update needed
Version unchanged, skipping output
```

## Expected State

The `calculate_new_version()` function should calculate a new version even when no tags exist:

1. **Get base version from Cargo.toml** (e.g., `0.1.0`)
2. **Get all merged PRs** (use timestamp `0` to get all PRs since repository creation)
3. **Determine bump type from PR labels** (MAJOR, MINOR, or PATCH)
4. **Count commits modifying application code** (all commits if no tag exists)
5. **Calculate new version** using `calculate_version()` function
6. **Return calculated version** instead of base version

**Expected implementation:**
- When `latest_tag` is `None`, still perform version calculation
- Use `github_client.get_merged_prs_since(0)` to get all merged PRs
- Use `determine_bump_type(prs)` to analyze PR labels
- Use `get_commit_count(None)` or count all commits modifying `src/`, `Cargo.toml`, `Cargo.lock`
- Use `calculate_version(base_version, bump_type, commit_count)` to calculate new version
- Return the calculated version instead of base version

**Expected behavior:**
- If PRs have `version: major` labels → MAJOR bump (e.g., `0.1.0` → `1.0.0`)
- If PRs have `version: minor` labels → MINOR bump (e.g., `0.1.0` → `0.2.0`)
- If no version labels → PATCH bump based on commit count (e.g., `0.1.0` → `0.1.40` if 40 commits)
- Version is always calculated and updated, even for first release

## Impact

### Version Accuracy Impact
- **Severity**: High
- **Priority**: High

Without version calculation for first release:
- First release always uses base version from `Cargo.toml` (typically `0.1.0`)
- PR labels are ignored for first release
- Commit count is ignored for first release
- Version doesn't reflect actual changes made before first release
- Semantic versioning principles are violated (version should reflect all changes)

### Release Management Impact
- **Severity**: High
- **Priority**: High

- First release may have incorrect version number
- Subsequent releases will be calculated from incorrect base version
- Version history starts with potentially incorrect version
- Difficult to track actual application state at first release
- May require manual version correction

### Developer Experience Impact
- **Severity**: Medium
- **Priority**: Medium

- Confusing behavior: version doesn't change despite many commits
- Unclear why first release uses base version without calculation
- May require manual intervention to set correct first version
- Workflow appears to work but doesn't actually update version

## Root Cause

The `calculate_new_version()` function assumes that when no tags exist, the version in `Cargo.toml` is already correct and doesn't need calculation. However, this assumption is incorrect because:

1. The repository may have many commits before the first release
2. PRs may have version labels that should trigger version bumps
3. The base version in `Cargo.toml` (e.g., `0.1.0`) may not reflect the actual state of the application
4. The function returns early without performing any calculation logic

The function should treat "no tags" as a special case where:
- Base version comes from `Cargo.toml` (correct)
- But version calculation still needs to occur (missing)
- PR labels should still be analyzed (missing)
- Commit count should still be considered (missing)


## Related Implementation Plan

See `work/25W46/BUG_RELEASE_VERSION_NO_TAG_CALCULATION.md` for the detailed implementation plan.
