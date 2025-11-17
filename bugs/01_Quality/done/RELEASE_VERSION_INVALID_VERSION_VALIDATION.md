# Bug: release-version script doesn't validate version format from Cargo.toml and tags

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

## Detailed Implementation Plan

### Phase 1: Implementation Steps

#### Step 1: Add version validation to `read_cargo_version()`

**File:** `.github/scripts/release-version/src/release_version/cargo.py`

1. **Import packaging.version modules**
   - [x] Add import: `from packaging.version import InvalidVersion, Version`
   - [x] Verify `packaging` is already in dependencies (should be, as it's used in `version.py`)

2. **Add version format validation**
   - [x] Locate the `read_cargo_version()` function
   - [x] After extracting version string: `version = str(cargo["package"]["version"])`
   - [x] After checking version is not empty
   - [x] Add validation using `Version(version)` to check format
   - [x] Wrap in try-except to catch `InvalidVersion` exception
   - [x] Raise `ValueError` with descriptive message: `f"Invalid version format in Cargo.toml: {version}. Expected semantic version (e.g., 1.0.0)"`
   - [x] Preserve exception chain: `raise ValueError(...) from e`

**Expected code change:**
```python
from packaging.version import InvalidVersion, Version

def read_cargo_version(path: str = "Cargo.toml") -> str:
    # ... existing code ...
    version = str(cargo["package"]["version"])
    if not version:
        raise ValueError("Version field is empty")

    # Validate version format
    try:
        Version(version)  # Raises InvalidVersion if invalid
    except InvalidVersion as e:
        raise ValueError(
            f"Invalid version format in Cargo.toml: {version}. "
            "Expected semantic version (e.g., 1.0.0)"
        ) from e

    return version
```

3. **Update docstring**
   - [x] Update docstring to mention version format validation
   - [x] Update `Raises` section to mention `ValueError` for invalid format

#### Step 2: Add validation to calculated version (defensive programming)

**File:** `.github/scripts/release-version/src/release_version/version.py`

1. **Import Version class (if not already imported)**
   - [x] Check current imports at top of file
   - [x] Add import: `from packaging.version import Version` (or update existing import to include `Version`)
   - [x] Note: `InvalidVersion` is already imported, but `Version` class is needed for validation

2. **Add validation to `calculate_version()` return value**
   - [x] Locate the `calculate_version()` function
   - [x] After calculating `new_version` (all three paths: MAJOR, MINOR, PATCH)
   - [x] Add validation using `Version(new_version)` before returning
   - [x] Wrap in try-except to catch `InvalidVersion` exception
   - [x] Raise `InvalidVersion` with descriptive message: `f"Calculated invalid version: {new_version}. This should not happen - please report this bug."`
   - [x] This is defensive programming - calculated versions should always be valid, but this catches any bugs

**Expected code change:**
```python
# At top of file, update import (if needed):
from packaging.version import InvalidVersion, Version  # Add Version if not already imported

# In calculate_version() function:
def calculate_version(
    base_version: str, bump_type: str, commit_count: int
) -> str:
    # ... existing code ...
    if bump_type == "MAJOR":
        new_version = f"{major + 1}.0.0"
    elif bump_type == "MINOR":
        new_version = f"{major}.{minor + 1}.0"
    else:  # PATCH
        new_version = f"{major}.{minor}.{patch + commit_count}"

    # Validate calculated version (defensive programming)
    try:
        Version(new_version)
    except InvalidVersion as e:
        raise InvalidVersion(
            f"Calculated invalid version: {new_version}. "
            "This should not happen - please report this bug."
        ) from e

    return new_version
```

2. **Update docstring**
   - [x] Update docstring to mention validation of return value
   - [x] Update `Raises` section if needed

#### Step 3: Add validation when extracting version from tag

**File:** `.github/scripts/release-version/src/release_version/version.py`

1. **Verify Version class is imported**
   - [x] If Step 2 was completed, `Version` should already be imported
   - [x] If Step 2 is skipped, add import: `from packaging.version import Version` (or update existing import)
   - [x] Note: This step uses the same `Version` class as Step 2

2. **Add immediate validation after tag extraction**
   - [x] Locate the `calculate_new_version()` function
   - [x] Find where `base_version = latest_tag.lstrip("v")` is executed (around line 189)
   - [x] Add validation immediately after extracting `base_version` (before `get_tag_timestamp()` call)
   - [x] Use `Version(base_version)` to validate format
   - [x] Wrap in try-except to catch `InvalidVersion` exception
   - [x] Raise `ValueError` with descriptive message: `f"Invalid version format in git tag '{latest_tag}': {base_version}. Expected semantic version (e.g., 1.0.0)"`
   - [x] Preserve exception chain: `raise ValueError(...) from e`

**Expected code change:**
```python
# In calculate_new_version() function, after getting latest_tag:
# Extract version from tag (remove 'v' prefix)
base_version = latest_tag.lstrip("v")

# Validate tag version format immediately
try:
    Version(base_version)  # Raises InvalidVersion if invalid
except InvalidVersion as e:
    raise ValueError(
        f"Invalid version format in git tag '{latest_tag}': {base_version}. "
        "Expected semantic version (e.g., 1.0.0)"
    ) from e

# Get tag timestamp
tag_timestamp = get_tag_timestamp(latest_tag)
# ... rest of function ...
```

**Note:** Ensure `Version` is imported at the top of the file (see Step 2, item 1, or add import if Step 2 is skipped).

2. **Update docstring**
   - [x] Update docstring to mention tag version validation
   - [x] Update `Raises` section to mention `ValueError` for invalid tag versions

#### Step 4: Verify error handling in first release path

**File:** `.github/scripts/release-version/src/release_version/version.py`

1. **Verify error propagation**
   - [x] Locate the first release path in `calculate_new_version()` (the `if not latest_tag:` block)
   - [x] Verify that `read_cargo_version()` is called and exceptions will propagate correctly
   - [x] Test that when `read_cargo_version()` raises `ValueError`, it propagates to the caller
   - [x] Confirm no additional error handling is needed (exceptions should bubble up automatically)

**Note:** Since `read_cargo_version()` (from Step 1) will now validate and raise `ValueError` with a clear message indicating the version is from Cargo.toml, the first release path will automatically benefit from this validation. No code changes are needed in this step - it's a verification step to ensure error propagation works correctly.

#### Step 5: Test implementation locally

**Status:** ✅ **COMPLETED** - Tests implemented in Python test files.

1. **Implemented tests in `test_cargo.py`**
   - [x] `test_read_cargo_version_invalid_format()` - Tests invalid version format (e.g., "invalid-version-string")
   - [x] `test_read_cargo_version_with_v_prefix()` - Tests rejection of 'v' prefix in Cargo.toml
   - [x] `test_read_cargo_version_prerelease()` - Tests acceptance of valid pre-release versions (e.g., "1.0.0-alpha")
   - [x] `test_read_cargo_version_build_metadata()` - Tests acceptance of valid build metadata versions (e.g., "1.0.0+build.1")
   - [x] All tests verify error messages clearly indicate source is Cargo.toml

2. **Implemented tests in `test_version.py`**
   - [x] `test_calculate_new_version_invalid_tag()` - Tests invalid tag version format validation
   - [x] `test_calculate_new_version_valid_tag()` - Tests valid tag version processing
   - [x] `test_calculate_new_version_first_release_invalid_cargo_version()` - Tests first release scenario with invalid Cargo.toml version
   - [x] `test_calculate_version_validates_output()` - Tests defensive validation of calculated versions
   - [x] All tests verify error messages clearly indicate source (tag or Cargo.toml)

3. **Test execution**
   - [x] All tests pass: `uv run pytest tests/test_cargo.py tests/test_version.py -v`
   - [x] 30 tests total, all passing
   - [x] Tests cover all validation scenarios from implementation plan

#### Step 6: Test in workflow

1. **Create test branch and PR**
   - [ ] Create a test branch with invalid version in `Cargo.toml`
   - [ ] Push changes to trigger workflow (or create PR if workflow runs on PR)
   - [ ] Monitor workflow execution

2. **Verify workflow execution with invalid version**
   - [ ] Check workflow logs to ensure validation error is raised
   - [ ] Verify script exits with code 1 when invalid version is detected
   - [ ] Verify error message is clear and indicates source (Cargo.toml or tag)
   - [ ] Verify workflow fails appropriately (doesn't proceed with invalid version)
   - [ ] Check that no commit or tag is created when validation fails

3. **Test with valid version**
   - [ ] Set valid version in `Cargo.toml`
   - [ ] Run workflow and verify it succeeds
   - [ ] Verify version is used correctly in tags and commits

### Phase 2: Rollback Plan

If issues are encountered:

1. **Immediate Rollback**
   - Revert changes to `cargo.py` (remove version validation)
   - Revert changes to `version.py` (remove tag validation and calculated version validation)
   - Verify script returns to previous (vulnerable) state
   - Document the issue encountered for future investigation

2. **Partial Rollback**
   - If validation is too strict (rejects valid versions):
    - Review `packaging.version.Version()` behavior
    - Adjust validation to accept valid semantic versions
    - Consider using `packaging.version.parse()` instead if more lenient
   - If validation is too lenient (accepts invalid versions):
    - Review semantic versioning specification
    - Tighten validation rules if needed
   - If error messages are unclear:
    - Improve error message text
    - Add more context about expected format

3. **Alternative Approach**
   - If `packaging.version.Version()` causes issues, consider:
    - Using regex pattern matching for semantic version format
    - Using a different validation library
    - Creating custom validation function
   - If validation in `read_cargo_version()` causes issues:
    - Move validation to `calculate_new_version()` first release path
    - Add validation in both places for redundancy

### Implementation Order

1. **Add validation to `read_cargo_version()`** (Step 1)
   - This is the primary fix - validates versions at the source
   - Most important for first release scenario
   - Test thoroughly with various invalid versions

2. **Add validation when extracting version from tag** (Step 3)
   - Validates tag versions immediately after extraction
   - Provides clear error messages indicating version came from a tag
   - Important for repositories with existing invalid tags

3. **Add validation to calculated versions** (Step 2)
   - Defensive programming - should never fail in practice
   - Adds safety net for any bugs in calculation logic
   - Lower priority but good practice

4. **Test locally** (Step 5)
   - Test with various valid and invalid versions from Cargo.toml
   - Test with valid and invalid tags
   - Verify error messages are clear and indicate source
   - Verify script behavior is correct

5. **Test in workflow** (Step 6)
   - Test complete workflow execution
   - Verify end-to-end functionality
   - Verify error handling in CI/CD environment

### Risk Assessment

- **Risk Level:** Low
- **Impact if Failed:**
  - Validation might be too strict and reject valid versions (easily fixable)
  - Validation might be too lenient and accept invalid versions (less likely, but fixable)
  - Error messages might be unclear (easily fixable)
  - No additional breakage beyond current vulnerability
- **Mitigation:**
  - Can test locally before committing
  - Can test in workflow on test branch
  - Easy rollback (revert changes)
  - `packaging.version.Version()` is well-tested and standard
  - Validation is additive - doesn't change existing behavior for valid versions
- **Testing:**
  - Can be fully tested locally before committing
  - Can be tested in workflow on non-main branch
  - Validation can be verified with simple test cases
  - Edge cases can be tested manually
- **Dependencies:**
  - `packaging` library is already a dependency (used in `version.py`)
  - No new dependencies required
  - Uses standard Python exception handling

### Expected Outcomes

After successful implementation:

- **Version Validation:** All versions from `Cargo.toml` are validated as semantic versions
- **Tag Validation:** All versions extracted from git tags are validated immediately with clear error messages
- **Error Detection:** Invalid versions are caught early with clear error messages indicating source
- **Workflow Safety:** Workflow fails appropriately when invalid versions are detected (from Cargo.toml or tags)
- **Data Integrity:** Only valid semantic versions are used in tags and commits
- **Developer Experience:** Clear error messages help developers fix invalid versions quickly, with context about whether they came from Cargo.toml or a tag
- **Defensive Programming:** Calculated versions are also validated (should never fail, but provides safety net)
- **Consistency:** All version validation uses the same mechanism (`packaging.version.Version()`)

## Example Fix

### Before:
```python
# cargo.py
def read_cargo_version(path: str = "Cargo.toml") -> str:
    # ... existing code ...
    version = str(cargo["package"]["version"])
    if not version:
        raise ValueError("Version field is empty")

    return version  # ❌ No format validation
```

```python
# version.py - first release path
if not latest_tag:
    cargo_path = f"{repo_path}/Cargo.toml" if repo_path != "." else "Cargo.toml"
    version = read_cargo_version(cargo_path)  # ❌ May return invalid version
    return (version, f"v{version}")  # ❌ Invalid version used in tag
```

### After:
```python
# cargo.py
from packaging.version import InvalidVersion, Version

def read_cargo_version(path: str = "Cargo.toml") -> str:
    # ... existing code ...
    version = str(cargo["package"]["version"])
    if not version:
        raise ValueError("Version field is empty")

    # Validate version format
    try:
        Version(version)  # ✅ Raises InvalidVersion if invalid
    except InvalidVersion as e:
        raise ValueError(
            f"Invalid version format in Cargo.toml: {version}. "
            "Expected semantic version (e.g., 1.0.0)"
        ) from e

    return version  # ✅ Only returns validated versions
```

```python
# version.py - first release path
if not latest_tag:
    cargo_path = f"{repo_path}/Cargo.toml" if repo_path != "." else "Cargo.toml"
    version = read_cargo_version(cargo_path)  # ✅ Now validates format
    return (version, f"v{version}")  # ✅ Only valid versions used
```

```python
# version.py - tag extraction path
# Extract version from tag (remove 'v' prefix)
base_version = latest_tag.lstrip("v")

# Validate tag version format immediately
try:
    Version(base_version)  # ✅ Raises InvalidVersion if invalid
except InvalidVersion as e:
    raise ValueError(
        f"Invalid version format in git tag '{latest_tag}': {base_version}. "
        "Expected semantic version (e.g., 1.0.0)"
    ) from e  # ✅ Clear error message indicating source is a tag

# Get tag timestamp
tag_timestamp = get_tag_timestamp(latest_tag)
# ... rest of function ...
```

```python
# version.py - calculated version validation (defensive)
def calculate_version(
    base_version: str, bump_type: str, commit_count: int
) -> str:
    # ... existing code ...
    new_version = f"{major}.{minor}.{patch + commit_count}"

    # Validate calculated version (defensive programming)
    try:
        Version(new_version)  # ✅ Should never fail, but validates
    except InvalidVersion as e:
        raise InvalidVersion(
            f"Calculated invalid version: {new_version}. "
            "This should not happen - please report this bug."
        ) from e

    return new_version
```

## References

- [Python `packaging.version` documentation](https://packaging.pypa.io/en/latest/version.html)
- [Semantic Versioning specification](https://semver.org/)
- [Python `packaging.version.Version` source](https://github.com/pypa/packaging/blob/main/src/packaging/version.py)
- [Cargo version field documentation](https://doc.rust-lang.org/cargo/reference/manifest.html#the-version-field)
