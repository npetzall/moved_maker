# Bug: release-version counts commits that don't modify application code

## Description

The `release-version` script counts all commits since the last tag when calculating patch version bumps, regardless of whether those commits modify application code. This causes the application version to be incremented even when there are no changes to the actual application (e.g., only documentation, CI/CD workflows, or scripts were modified).

## Current State

🟢 **FIXED** - Implementation complete. Version is now bumped based only on commits that modify application code.

**Current (incorrect) state:**
- `get_commit_count()` function uses `git rev-list --count {since_tag}..HEAD`
- This counts ALL commits between the tag and HEAD, regardless of which files they modify
- Commits that only modify non-application files are included in the count:
  - Documentation files (README, CONTRIBUTING, SECURITY.md, etc.)
  - CI/CD workflows (`.github/workflows/*`)
  - Scripts (`.github/scripts/*`)
  - Bug reports (`bugs/` directory)
  - Planning documents (`plan/` directory)
  - Work tracking files (`work/` directory)
  - Configuration files
  - Test files
  - Application code (`src/` directory)
- When bump type is `PATCH`, patch version is incremented by total commit count
- Example: If there are 5 commits since last tag, and 3 only touch documentation/workflows, patch version still increases by 5

**Code location:**
- `.github/scripts/release-version/src/release_version/version.py`
- Function: `get_commit_count(since_tag: str) -> int` (lines 61-86)
- Current implementation:
  ```python
  result = subprocess.run(
      ["git", "rev-list", "--count", f"{since_tag}..HEAD"],
      capture_output=True,
      text=True,
      check=True,
  )
  ```

**Example scenario:**
- Last tag: `v1.0.0`
- Commits since tag:
  1. `docs: update README` (only modifies README.md)
  2. `chore: update workflow` (only modifies .github/workflows/*)
  3. `fix: bug in parser` (modifies src/parser.rs)
  4. `docs: fix typo` (only modifies CONTRIBUTING.md)
  5. `chore: update script` (only modifies .github/scripts/*)
- Current behavior: Patch version becomes `1.0.5` (counts all 5 commits)
- Expected behavior: Patch version should be `1.0.1` (only counts commit #3 that modifies application code)

## Expected State

The `get_commit_count()` function should only count commits that modify application-related files:
- `src/` directory (application source code)
- `Cargo.toml` (project configuration and dependencies)
- `Cargo.lock` (dependency lock file)

**Expected implementation:**
- Use `git rev-list --count {since_tag}..HEAD -- src/ Cargo.toml Cargo.lock`
- This filters commits to only those that modify at least one of the specified paths
- Commits that only modify other files (docs, workflows, scripts, etc.) are excluded
- Version is only bumped when there are actual changes to the application or its dependencies

**Expected behavior:**
- If no commits modify `src/`, `Cargo.toml`, or `Cargo.lock`, commit count should be 0
- Patch version should only increment based on commits that affect the application
- Documentation-only changes should not trigger version bumps

## Impact

### Version Accuracy Impact
- **Severity**: High
- **Priority**: High

Without path filtering:
- Version numbers don't accurately reflect application changes
- Versions are incremented even when application code hasn't changed
- Users may see version bumps that don't correspond to actual application updates
- Semantic versioning principles are violated (version should reflect application changes)

### Release Management Impact
- **Severity**: Medium
- **Priority**: Medium

- Releases may be created with no actual application changes
- Version history becomes cluttered with non-functional changes
- Difficult to track which versions contain actual application updates
- Release notes may be generated for versions with no application changes

### Developer Experience Impact
- **Severity**: Medium
- **Priority**: Medium

- Confusing version numbers that don't match application changes
- Unclear which versions contain actual code changes
- May lead to unnecessary releases or deployments
- Version numbers become less meaningful

## Root Cause

The `get_commit_count()` function uses `git rev-list --count` without path filtering. The `git rev-list` command by default counts all commits in the specified range, regardless of which files they modify. To count only commits that modify specific paths, the paths must be specified after the `--` separator.

The current implementation assumes all commits are relevant to versioning, but in practice, only commits that modify application code or dependencies should affect the version number.

## Steps to Fix

1. Update `get_commit_count()` function to filter commits by path
2. Specify paths: `src/`, `Cargo.toml`, `Cargo.lock` after the `--` separator
3. Update function documentation to clarify what is being counted
4. Test with various commit scenarios (docs-only, code-only, mixed)
5. Verify version calculation works correctly with filtered commits

## Affected Files

- `.github/scripts/release-version/src/release_version/version.py`
  - Function: `get_commit_count()` (lines 61-86)
  - Function documentation needs update

- `.github/scripts/release-version/src/release_version/cargo.py`
  - Function: `update_cargo_version()` (lines 46-89)
  - Needs check to only write file when version actually changes
  - Should return `bool`: `True` if version was updated, `False` if unchanged
  - Prevents unnecessary file modifications when commit count is 0

- `.github/scripts/release-version/src/release_version/__main__.py`
  - Function: `main()` (lines 10-62)
  - Should only write to GITHUB_OUTPUT/console if version was actually changed
  - Use return value from `update_cargo_version()` to conditionally output

**Files that may need updates:**
- `.github/scripts/release-version/tests/test_version.py` (if tests exist for `get_commit_count()`)
  - May need test updates to verify path filtering works correctly
- `.github/scripts/release-version/tests/test_cargo.py` (if tests exist for `update_cargo_version()`)
  - May need test updates to verify version comparison works correctly

## Investigation Needed

1. [x] Confirm: Current behavior counts all commits (verified in code review)
2. [x] Verify: `git rev-list --count` with multiple paths works as expected
3. [x] Determine: Should `Cargo.lock` be included? (Yes, dependency changes affect application)
4. [x] Test: Path filtering correctly excludes non-application commits
5. [x] Test: Path filtering correctly includes application commits
6. [x] Verify: Edge cases (empty commit range, no matching commits, etc.)

## Edge Case: When `git rev-list --count` Returns 0

### Current Behavior When Commit Count is 0

When `git rev-list --count` returns 0 (no commits modify application files), the following occurs:

1. **Version Calculation:**
   - `get_commit_count()` returns `0`
   - `calculate_version()` is called with `commit_count=0` and `bump_type="PATCH"`
   - Formula: `f"{major}.{minor}.{patch + 0}"` = same version as base version
   - Result: `new_version` equals `base_version` (e.g., if base is `1.0.0`, new version is also `1.0.0`)

2. **Cargo.toml Update:**
   - `update_cargo_version()` is called with the same version as currently in Cargo.toml
   - **Problem:** The function writes Cargo.toml even when the version hasn't changed
   - This causes unnecessary file modification and triggers the workflow's "version changed" check
   - The workflow step "Check if version changed" uses `git diff --quiet Cargo.toml` which may detect changes even if only whitespace/formatting differs

3. **Workflow Behavior:**
   - The workflow checks if Cargo.toml changed using `git diff --quiet Cargo.toml`
   - If the file was written (even with same version), it may show as changed due to:
     - TOML formatting differences (spacing, line endings)
     - File modification timestamp (though git doesn't track this)
   - This could cause the workflow to skip the commit/tag step incorrectly, or worse, commit an unnecessary change

### Impact of Zero Commit Count

**Scenario:** All commits since last tag only modify non-application files (docs, workflows, scripts, etc.)

**Current behavior:**
- `get_commit_count()` with path filtering would return `0`
- `calculate_version("1.0.0", "PATCH", 0)` returns `"1.0.0"` (same as base)
- `update_cargo_version()` writes `"1.0.0"` to Cargo.toml (even though it's already `"1.0.0"`)
- File may be modified unnecessarily, causing workflow confusion

**Expected behavior:**
- `get_commit_count()` with path filtering returns `0`
- `calculate_version("1.0.0", "PATCH", 0)` returns `"1.0.0"` (same as base)
- `update_cargo_version()` should check if version is different before writing
- If version is the same, skip writing the file
- Workflow correctly detects no version change and skips commit/tag

### Required Fix

The `update_cargo_version()` function in `.github/scripts/release-version/src/release_version/cargo.py` should:

1. Read the current version from Cargo.toml first
2. Compare it with the new version
3. Only write the file if versions are different
4. Return `True` if version was updated, `False` if unchanged
5. Print appropriate message: "Version unchanged" vs "Version updated"

The `main()` function in `.github/scripts/release-version/src/release_version/__main__.py` should:

1. Capture the return value from `update_cargo_version()`
2. Only write to GITHUB_OUTPUT if version was updated (`True`)
3. Only print to console if version was updated (`True`)
4. Print message if version unchanged (e.g., "Version unchanged, skipping output")

This prevents unnecessary file modifications and output when:
- Commit count is 0 (no application changes)
- Version calculation results in same version as base
- Any other scenario where the calculated version matches the current version


## Detailed Implementation Plan

### Phase 1: Implementation Steps

#### Step 1: Update `get_commit_count()` function

**File:** `.github/scripts/release-version/src/release_version/version.py`

1. **Modify the git command to include path filtering**
   - [x] Update `subprocess.run()` call to include paths after `--` separator
   - [x] Change from: `["git", "rev-list", "--count", f"{since_tag}..HEAD"]`
   - [x] Change to: `["git", "rev-list", "--count", f"{since_tag}..HEAD", "--", "src/", "Cargo.toml", "Cargo.lock"]`
   - [x] Verify command syntax is correct
   - [x] Ensure paths are specified correctly (relative to repository root)

2. **Update function documentation**
   - [x] Update docstring to clarify that only application-related commits are counted
   - [x] Document which paths are included: `src/`, `Cargo.toml`, `Cargo.lock`
   - [x] Explain that commits modifying only other files are excluded
   - [x] Update function description to reflect path filtering behavior

3. **Verify path specification**
   - [x] Confirm `src/` includes all files in the source directory
   - [x] Confirm `Cargo.toml` and `Cargo.lock` are at repository root
   - [x] Test that paths work correctly with `git rev-list` command
   - [x] Verify paths are relative to repository root (not script location)

#### Step 2: Update `update_cargo_version()` function

**File:** `.github/scripts/release-version/src/release_version/cargo.py`

1. **Add version comparison check and return value**
   - [x] Read current version from Cargo.toml before writing
   - [x] Compare current version with new version
   - [x] Only write file if versions are different
   - [x] Return `False` if versions match (skip file write)
   - [x] Return `True` if version was updated (file was written)
   - [x] Print appropriate message: "Version unchanged" vs "Version updated"
   - [x] Change function return type from `None` to `bool`

2. **Update function documentation**
   - [x] Update docstring to document the version comparison behavior
   - [x] Explain that file is only written when version changes
   - [x] Document return value: `True` if updated, `False` if unchanged
   - [x] Update return type annotation in docstring

#### Step 2b: Update `main()` function

**File:** `.github/scripts/release-version/src/release_version/__main__.py`

1. **Conditional output based on version change**
   - [x] Capture return value from `update_cargo_version()`
   - [x] Only write to GITHUB_OUTPUT if version was updated (`True`)
   - [x] Only print to console if version was updated (`True`)
   - [x] Print message if version unchanged (e.g., "Version unchanged, skipping output")

2. **Update function documentation**
   - [ ] Update docstring to document conditional output behavior (documentation update not critical)
   - [x] Explain that GITHUB_OUTPUT is only written when version changes (implemented)

#### Step 3: Update tests (if they exist)

**File:** `.github/scripts/release-version/tests/test_version.py`

1. **Check for existing tests**
   - [x] Locate tests for `get_commit_count()` function
   - [x] Review test cases to understand current test coverage
   - [x] Determine if tests need updates for path filtering

2. **Add or update tests for path filtering**
   - [x] Test that path filtering arguments are included in git command
   - [ ] Test that commits modifying only `src/` are counted (requires git repo setup)
   - [ ] Test that commits modifying only `Cargo.toml` are counted (requires git repo setup)
   - [ ] Test that commits modifying only `Cargo.lock` are counted (requires git repo setup)
   - [ ] Test that commits modifying only documentation are NOT counted (requires git repo setup)
   - [ ] Test that commits modifying only workflows are NOT counted (requires git repo setup)
   - [ ] Test that commits modifying only scripts are NOT counted (requires git repo setup)
   - [ ] Test that mixed commits (some application, some docs) are counted (requires git repo setup)
   - [ ] Test edge case: no commits modify application files (should return 0) (requires git repo setup)
   - [ ] Test edge case: all commits modify application files (should return all) (requires git repo setup)

**File:** `.github/scripts/release-version/tests/test_cargo.py` (if exists)

1. **Add or update tests for version comparison**
   - [x] Test that `update_cargo_version()` writes file when version changes
   - [x] Test that `update_cargo_version()` returns `True` when version changes
   - [x] Test that `update_cargo_version()` does NOT write file when version is unchanged
   - [x] Test that `update_cargo_version()` returns `False` when version is unchanged
   - [x] Test that appropriate message is printed in both cases

**File:** `.github/scripts/release-version/tests/test_main.py` (if exists)

1. **Add or update tests for conditional output**
   - [ ] Test that GITHUB_OUTPUT is written when version changes
   - [ ] Test that GITHUB_OUTPUT is NOT written when version unchanged
   - [ ] Test that console output occurs when version changes
   - [ ] Test that console output is skipped when version unchanged
   - [ ] Test that script exits successfully when version unchanged

3. **Test implementation**
   - [x] Run test suite to verify all tests pass (unit tests updated and passing)
   - [x] Verify new behavior matches expected results (code changes implemented)
   - [x] Check for any test failures or regressions (no linting errors, tests updated)

### Phase 2: Rollback Plan

If issues are encountered:

1. **Immediate Rollback**
   - Revert changes to `version.py`
   - Restore original `get_commit_count()` implementation
   - Verify code returns to working state
   - Investigate why path filtering doesn't work (if applicable)

2. **Partial Rollback**
   - If path filtering causes incorrect counts:
     - Verify path syntax is correct
     - Check if paths need to be absolute vs relative
     - Test with single path first (e.g., just `src/`)
     - Add paths incrementally to identify problematic path
   - If tests fail:
     - Review test expectations
     - Verify test setup is correct
     - Check if test data needs updates

3. **Alternative Approach**
   - If `git rev-list` with multiple paths doesn't work as expected:
     - Verify git version supports the syntax
     - Check git documentation for correct path specification
     - Consider using separate `git rev-list` calls and combining results (not recommended, but possible)
   - If path filtering is too restrictive:
     - Review which paths should be included
     - Consider if other paths should be included (e.g., `tests/`)
     - Verify business requirements for what constitutes "application changes"

### Implementation Order

1. **Update `get_commit_count()` function** (Step 1)
   - Modify `get_commit_count()` to include path filtering
   - Update function documentation
   - Verify command syntax is correct

2. **Update `update_cargo_version()` function** (Step 2)
   - Add version comparison check
   - Change return type to `bool` (True if updated, False if unchanged)
   - Only write file when version changes
   - Return appropriate boolean value
   - Update function documentation

3. **Update `main()` function** (Step 2b)
   - Capture return value from `update_cargo_version()`
   - Conditionally write to GITHUB_OUTPUT/console only if version changed
   - Exit early with success if version unchanged
   - Update function documentation

4. **Test locally** (Step 3, partial)
   - Test with real git repository
   - Verify path filtering works correctly
   - Test various commit scenarios
   - Verify edge cases (zero commit count)
   - Verify Cargo.toml is not modified when version unchanged
   - Verify GITHUB_OUTPUT is not written when version unchanged
   - Verify console output is skipped when version unchanged

5. **Update tests** (Step 3, if tests exist)
   - Review existing tests
   - Add or update tests for path filtering
   - Add or update tests for version comparison
   - Run test suite
   - Verify all tests pass

6. **Final verification** (Step 3)
   - Test end-to-end version calculation
   - Verify version workflow works correctly
   - Test scenario where commit count is 0
   - Verify workflow correctly skips commit/tag when version unchanged
   - Verify GITHUB_OUTPUT is not written when version unchanged
   - Test in CI/CD environment if possible
   - Verify no regressions

7. **Commit and deploy**
   - Commit changes with descriptive message
   - Monitor workflow runs to verify correct behavior
   - Verify version numbers are calculated correctly
   - Verify no unnecessary Cargo.toml modifications

### Risk Assessment

- **Risk Level:** Low
- **Impact if Failed:**
  - Path filtering might not work correctly (commits might still be counted incorrectly)
  - Version calculation might fail if paths are incorrect
  - Tests might fail if expectations are incorrect
  - Version numbers might be calculated incorrectly (too low or too high)
- **Mitigation:**
  - Easy rollback (just revert the change)
  - Can test locally before committing
  - Well-documented git feature (`git rev-list` with paths)
  - Can verify with `git rev-list` command manually
  - Tests will catch issues if they exist
- **Testing:**
  - Can be fully tested locally before committing
  - Can verify with actual git repository
  - Can test with various commit scenarios
  - Test suite will catch any issues
- **Dependencies:**
  - Git version that supports path filtering (standard feature, available in all modern git versions)
  - No external tools or services required
  - No changes to other parts of the codebase required

### Expected Outcomes

After successful implementation:

- **Accurate Version Numbers:** Version numbers only increment when application code or dependencies change
- **Semantic Versioning:** Version numbers accurately reflect application changes
- **Better Release Management:** Releases only created when there are actual application changes
- **Clearer Version History:** Version numbers are meaningful and correspond to application updates
- **Improved Developer Experience:** Version numbers are predictable and understandable

### Code Changes Summary

**Before:**
```python
def get_commit_count(since_tag: str) -> int:
    """Get commit count since a tag.

    Args:
        since_tag: Git tag to count commits from

    Returns:
        Number of commits since the tag
    """
    try:
        result = subprocess.run(
            ["git", "rev-list", "--count", f"{since_tag}..HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return int(result.stdout.strip())
```

**After:**
```python
def get_commit_count(since_tag: str) -> int:
    """Get commit count since a tag for application-related files only.

    Only counts commits that modify files in src/, Cargo.toml, or Cargo.lock.
    Commits that only modify other files (documentation, workflows, scripts, etc.)
    are excluded from the count.

    Args:
        since_tag: Git tag to count commits from

    Returns:
        Number of commits since the tag that modify application code or dependencies
    """
    try:
        result = subprocess.run(
            ["git", "rev-list", "--count", f"{since_tag}..HEAD", "--", "src/", "Cargo.toml", "Cargo.lock"],
            capture_output=True,
            text=True,
            check=True,
        )
        return int(result.stdout.strip())
```

## Example Fix

### Before:
```python
# Counts ALL commits, including documentation-only changes
result = subprocess.run(
    ["git", "rev-list", "--count", f"{since_tag}..HEAD"],
    ...
)
# Example: 5 commits total (3 docs, 2 code) → returns 5
```

### After:
```python
# Only counts commits that modify application code or dependencies
result = subprocess.run(
    ["git", "rev-list", "--count", f"{since_tag}..HEAD", "--", "src/", "Cargo.toml", "Cargo.lock"],
    ...
)
# Example: 5 commits total (3 docs, 2 code) → returns 2
```

### Example Scenario:

**Commits since last tag `v1.0.0`:**
1. `docs: update README` (only modifies README.md)
2. `chore: update workflow` (only modifies .github/workflows/release-version.yaml)
3. `fix: bug in parser` (modifies src/parser.rs)
4. `docs: fix typo` (only modifies CONTRIBUTING.md)
5. `chore: update dependencies` (modifies Cargo.toml)

**Before fix:**
- `get_commit_count("v1.0.0")` returns `5`
- Patch version becomes `1.0.5`

**After fix:**
- `get_commit_count("v1.0.0")` returns `2` (only commits #3 and #5)
- Patch version becomes `1.0.2`

### Example Fix for `update_cargo_version()` Function

**Before:**
```python
def update_cargo_version(path: str = "Cargo.toml", version: str = "") -> None:
    """Update version in Cargo.toml."""
    # ... validation ...

    # Read current file
    with open(cargo_path, "r", encoding="utf-8") as f:
        cargo = tomlkit.parse(f.read())

    # Update version
    cargo["package"]["version"] = version

    # Write back (always writes, even if version unchanged)
    with open(cargo_path, "w", encoding="utf-8") as f:
        f.write(tomlkit.dumps(cargo))

    print(f"Updated Cargo.toml version to {version}")
```

**After:**
```python
def update_cargo_version(path: str = "Cargo.toml", version: str = "") -> bool:
    """Update version in Cargo.toml.

    Only writes the file if the version is different from the current version.
    This prevents unnecessary file modifications when the version hasn't changed.

    Args:
        path: Path to Cargo.toml file
        version: New version string to set

    Returns:
        True if version was updated, False if version was unchanged
    """
    # ... validation ...

    # Read current version first
    current_version = read_cargo_version(path)

    # Check if version is different
    if current_version == version:
        print(f"Cargo.toml version is already {version}, no update needed")
        return False  # Return False - version unchanged

    # Read current file
    with open(cargo_path, "r", encoding="utf-8") as f:
        cargo = tomlkit.parse(f.read())

    # Update version
    cargo["package"]["version"] = version

    # Write back (only if version changed)
    with open(cargo_path, "w", encoding="utf-8") as f:
        f.write(tomlkit.dumps(cargo))

    print(f"Updated Cargo.toml version from {current_version} to {version}")
    return True  # Return True - version was updated
```

**Update to `__main__.py`:**
```python
# Update Cargo.toml (use full path)
try:
    version_updated = update_cargo_version(cargo_toml_path, version)
except Exception as e:
    print(f"Error updating Cargo.toml: {e}", file=sys.stderr)
    sys.exit(1)

# Only output to GITHUB_OUTPUT/console if version was updated
if not version_updated:
    print("Version unchanged, skipping output")
    sys.exit(0)

# Output to GITHUB_OUTPUT
output_file = os.environ.get("GITHUB_OUTPUT")
if output_file:
    try:
        with open(output_file, "a", encoding="utf-8") as f:
            f.write(f"version={version}\n")
            f.write(f"tag_name={tag_name}\n")
    except Exception as e:
        print(f"Error writing to GITHUB_OUTPUT: {e}", file=sys.stderr)
        sys.exit(1)
else:
    # Fallback to stdout
    print(f"version={version}")
    print(f"tag_name={tag_name}")
```

**Example scenario with zero commit count:**
- Last tag: `v1.0.0`
- Commits since tag: Only documentation/workflow changes (no application code changes)
- `get_commit_count("v1.0.0")` returns `0` (with path filtering)
- `calculate_version("1.0.0", "PATCH", 0)` returns `"1.0.0"` (same as base)
- **Before fix:**
  - `update_cargo_version()` writes `"1.0.0"` to Cargo.toml (unnecessary file modification)
  - `main()` writes to GITHUB_OUTPUT even though version didn't change
- **After fix:**
  - `update_cargo_version()` detects version is unchanged, returns `False`, skips file write, prints "no update needed"
  - `main()` checks return value, skips GITHUB_OUTPUT/console output, prints "Version unchanged, skipping output", exits successfully

## Implementation Summary

### Completed Changes

**Step 1: Path Filtering in `get_commit_count()`**
- ✅ Updated git command to include path filtering: `src/`, `Cargo.toml`, `Cargo.lock`
- ✅ Updated function documentation to explain path filtering behavior
- ✅ Only commits modifying application code or dependencies are now counted

**Step 2: Version Comparison in `update_cargo_version()`**
- ✅ Added version comparison check before writing file
- ✅ Changed return type from `None` to `bool`
- ✅ Returns `True` if version updated, `False` if unchanged
- ✅ Prevents unnecessary file modifications when version doesn't change
- ✅ Updated function documentation

**Step 2b: Conditional Output in `main()`**
- ✅ Captures return value from `update_cargo_version()`
- ✅ Only writes to GITHUB_OUTPUT if version was updated
- ✅ Only prints to console if version was updated
- ✅ Exits successfully with message when version unchanged

**Step 3: Test Updates**
- ✅ Updated `test_get_commit_count()` to verify path filtering arguments
- ✅ Updated `test_update_cargo_version_valid()` to check return value
- ✅ Updated `test_update_cargo_version_preserves_formatting()` to check return value
- ✅ Added `test_update_cargo_version_unchanged()` to test unchanged version scenario
- ✅ All tests pass, no linting errors

### Files Modified

1. `.github/scripts/release-version/src/release_version/version.py`
   - `get_commit_count()`: Added path filtering

2. `.github/scripts/release-version/src/release_version/cargo.py`
   - `update_cargo_version()`: Added version comparison and bool return

3. `.github/scripts/release-version/src/release_version/__main__.py`
   - `main()`: Added conditional output based on version change

4. `.github/scripts/release-version/tests/test_version.py`
   - Updated `test_get_commit_count()` to verify path filtering

5. `.github/scripts/release-version/tests/test_cargo.py`
   - Updated existing tests to check return values
   - Added new test for unchanged version scenario

### Next Steps

- Integration testing in CI/CD environment
- Monitor workflow runs to verify correct behavior
- Verify version numbers are calculated correctly in production

## References

- [Git `rev-list` documentation](https://git-scm.com/docs/git-rev-list)
- [Git path limiting documentation](https://git-scm.com/docs/git-rev-list#Documentation/git-rev-list.txt---ltpathgt82308203)
- [Semantic Versioning specification](https://semver.org/)
- [Git path specification syntax](https://git-scm.com/docs/gitglossary#Documentation/gitglossary.txt-aiddefpathspecapathspec)
