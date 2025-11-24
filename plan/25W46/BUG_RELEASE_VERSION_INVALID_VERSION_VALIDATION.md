# BUG: release-version script doesn't validate version format from Cargo.toml and tags

**Status**: ✅ Complete

## Description

The `release-version` script doesn't validate that version strings read from `Cargo.toml` or extracted from git tags are valid semantic versions. When performing the first release (no tags exist), the script reads the version directly from `Cargo.toml` without format validation. When tags exist, the script extracts the version from the tag without immediate validation, which could result in invalid versions being used in calculations, written to `GITHUB_OUTPUT`, committed to the repository, and used as git tags.

## Current State

**Status:** ⚠️ **IDENTIFIED** - Issue confirmed, validation missing in first release path.

**Current (incorrect) state:**
- `read_cargo_version()` only checks:
  - File exists ✅
  - `[package]` section exists ✅
  - `version` field exists ✅
  - Version is not empty ✅
- **Does NOT validate version format** ❌
- First release path uses version from `Cargo.toml` without validation
- Tag version extraction doesn't validate immediately:
  - `base_version = latest_tag.lstrip("v")` extracts version without validation
  - Validation only happens later in `calculate_version()` via `packaging.version.parse()`
  - Error message doesn't clearly indicate version came from a tag
- Calculated versions are validated (via `packaging.version.parse()` in `calculate_version()`)
- Invalid versions could pass through and be used in tags and commits

**Code path (first release):**
```python
if not latest_tag:
    # First release - use version from Cargo.toml
    cargo_path = f"{repo_path}/Cargo.toml" if repo_path != "." else "Cargo.toml"
    version = read_cargo_version(cargo_path)  # Returns version string without validation
    return (version, f"v{version}")  # Returns without validation
```

**Code path (when tags exist):**
```python
# Extract version from tag (remove 'v' prefix)
base_version = latest_tag.lstrip("v")  # ❌ No immediate validation
# ... later in calculate_version() ...
parsed_version = packaging_version.parse(base_version)  # Validation happens here, but error message doesn't indicate it's from a tag
```

**Example of invalid version that would pass:**
```toml
[package]
version = "invalid-version-string"
```

**Example of invalid tag that would cause issues:**
```bash
git tag vinvalid-version-string  # Invalid tag in repository
# Script would fail later with unclear error message
```

## Expected State

All version strings should be validated as valid semantic versions before being used:
- Versions read from `Cargo.toml` should be validated using `packaging.version.Version()`
- Versions extracted from git tags should be validated immediately after extraction
- Invalid versions should raise `ValueError` or `InvalidVersion` with descriptive error messages
- Script should exit with code 1 if invalid version is detected
- Error messages should clearly indicate where the invalid version came from (Cargo.toml, tag, or calculated)

## Impact

### Release Process Impact
- **Severity**: High
- **Priority**: High

**Impact if invalid version is used:**
- Script exits with code 0 (success) even with invalid version (first release scenario)
- Invalid version written to `GITHUB_OUTPUT`
- Workflow attempts to commit and tag with invalid version
- Tag creation might succeed (git allows any tag name)
- `Cargo.toml` update succeeds (just writes the string)
- **Result: Invalid version in repository and tags**
- If invalid tag exists, script fails later with unclear error message
- Future version calculations may fail when trying to parse invalid base version from tag
- Release automation breaks down

### Data Integrity Impact
- **Severity**: Medium
- **Priority**: High

- Invalid versions in tags pollute git history
- Invalid versions in `Cargo.toml` may cause issues for other tools
- Semantic versioning standards are violated
- Version comparison and sorting may fail

### Developer Experience Impact
- **Severity**: Medium
- **Priority**: Medium

- Errors may not be caught until later in the release process
- Debugging invalid versions is more difficult after they're committed
- Workflow failures may be confusing without clear validation errors

## Root Cause

The `read_cargo_version()` function in `cargo.py` only performs basic checks (file exists, section exists, field exists, not empty) but doesn't validate that the version string conforms to semantic versioning standards. The first release path in `version.py` uses the version directly from `Cargo.toml` without additional validation. When tags exist, the script extracts the version from the tag (`base_version = latest_tag.lstrip("v")`) without immediate validation - validation only happens later in `calculate_version()` via `packaging.version.parse()`, and the error message doesn't clearly indicate the version came from a tag. Unlike these paths, calculated versions are validated through `packaging.version.parse()` in `calculate_version()`.

## Affected Files

- `.github/scripts/release-version/src/release_version/cargo.py`
  - `read_cargo_version()` function needs version format validation
- `.github/scripts/release-version/src/release_version/version.py`
  - `calculate_new_version()` function's first release path should validate version (though this becomes redundant if `read_cargo_version()` validates)
  - `calculate_new_version()` function's tag extraction path should validate version immediately after extraction
  - `calculate_version()` already validates base_version, but calculated versions could also be validated before returning

## Investigation Summary

1. ✅ Confirmed: `read_cargo_version()` doesn't validate version format
2. ✅ Confirmed: First release path uses unvalidated version from `Cargo.toml`
3. ✅ Confirmed: Tag version extraction doesn't validate immediately (validation happens later in `calculate_version()`)
4. ✅ Confirmed: Error messages for invalid tag versions don't clearly indicate source
5. ✅ Confirmed: Calculated versions are validated (via `packaging.version.parse()`)
6. ✅ Confirmed: All error paths properly exit with code 1
7. ✅ Identified: `packaging.version.Version()` should be used for validation
8. ✅ Identified: Error messages should clearly indicate source of invalid version (Cargo.toml, tag, or calculated)

## Status

✅ **IMPLEMENTED** - Code changes and tests completed for Steps 1-5.

**Implementation:**
- `read_cargo_version()` in `cargo.py` (validates versions from Cargo.toml, rejects 'v' prefix)
- `calculate_version()` in `version.py` (defensive validation of calculated versions)
- `calculate_new_version()` in `version.py` (validates versions extracted from git tags)

**Tests:**
- Added 4 new tests in `test_cargo.py` for Cargo.toml version validation
- Added 4 new tests in `test_version.py` for tag validation and error propagation
- All 30 tests passing

Ready for workflow testing (Step 6).


## Related Implementation Plan

See `work/25W46/BUG_RELEASE_VERSION_INVALID_VERSION_VALIDATION.md` for the detailed implementation plan.
