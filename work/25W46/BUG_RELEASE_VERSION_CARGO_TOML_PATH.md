# Implementation Plan: BUG_RELEASE_VERSION_CARGO_TOML_PATH

**Status**: ✅ Complete

## Overview

This implementation plan addresses the bug described in `plan/25W46/BUG_RELEASE_VERSION_CARGO_TOML_PATH.md`.

## Context

Related bug report: `plan/25W46/BUG_RELEASE_VERSION_CARGO_TOML_PATH.md`

## Detailed Implementation Plan

### Phase 1: Implementation Steps

#### Step 1: Update workflow to set CARGO_TOML_PATH environment variable

**File:** `.github/workflows/release-version.yaml`

1. **Add CARGO_TOML_PATH to environment variables**
   - [x] Locate the "Calculate version from PR labels" step
   - [x] Add `CARGO_TOML_PATH: ${{ github.workspace }}/Cargo.toml` to the `env` section
   - [x] Verify the environment variable uses absolute path from `github.workspace`
   - [x] Ensure the variable is set before the `cd` command (environment variables persist across commands in the same step)

2. **Verify workflow step structure**
   - [x] Confirm the step maintains existing `GITHUB_TOKEN` and `GITHUB_REPOSITORY` environment variables
   - [x] Verify the `cd .github/scripts/release-version` command remains unchanged
   - [x] Ensure `uv run python -m release_version` command remains unchanged

**Expected workflow change:**
```yaml
- name: Calculate version from PR labels
  id: version
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    GITHUB_REPOSITORY: ${{ github.repository }}
    CARGO_TOML_PATH: ${{ github.workspace }}/Cargo.toml
  run: |
    cd .github/scripts/release-version
    uv run python -m release_version
```

#### Step 2: Update script to read CARGO_TOML_PATH from environment

**File:** `.github/scripts/release-version/src/release_version/__main__.py`

1. **Add path resolution logic**
   - [x] Locate the `main()` function
   - [x] Add code to read `CARGO_TOML_PATH` from environment variable: `cargo_toml_path = os.environ.get("CARGO_TOML_PATH", "Cargo.toml")`
   - [x] Extract repository root from the path: `repo_root = os.path.dirname(cargo_toml_path) or "."`
   - [x] Ensure default value `"Cargo.toml"` is used if environment variable is not set (for local development)

2. **Update calculate_new_version call**
   - [x] Locate the call to `calculate_new_version(github_client)`
   - [x] Update to pass `repo_path` parameter: `calculate_new_version(github_client, repo_path=repo_root)`
   - [x] Verify the function signature supports `repo_path` parameter (already confirmed in investigation)

3. **Update update_cargo_version call**
   - [x] Locate the call to `update_cargo_version("Cargo.toml", version)`
   - [x] Update to use `cargo_toml_path` variable: `update_cargo_version(cargo_toml_path, version)`
   - [x] Verify the function accepts the path parameter (check `cargo.py` if needed)

**Expected code change:**
```python
# Get Cargo.toml path from environment or default
cargo_toml_path = os.environ.get("CARGO_TOML_PATH", "Cargo.toml")
repo_root = os.path.dirname(cargo_toml_path) or "."

# Calculate version (pass repo_root for reading current version)
version, tag_name = calculate_new_version(github_client, repo_path=repo_root)

# Update Cargo.toml (use full path)
update_cargo_version(cargo_toml_path, version)
```

#### Step 3: Verify cargo.py supports path parameter

**File:** `.github/scripts/release-version/src/release_version/cargo.py`

1. **Check update_cargo_version function signature**
   - [x] Verify `update_cargo_version()` accepts a path parameter (not just hardcoded "Cargo.toml")
   - [x] If function needs modification, update it to accept path as first parameter
   - [x] Ensure the function can handle both relative and absolute paths

2. **Verify read_cargo_version function (if used)**
   - [x] Check if `read_cargo_version()` is called by `calculate_new_version()` and supports path parameter
   - [x] Verify path handling in version.py is correct (already confirmed to support `repo_path`)

#### Step 4: Test implementation locally

1. **Test from repository root**
   - [x] Set `CARGO_TOML_PATH` environment variable to absolute path of Cargo.toml
   - [x] Run script from repository root: `cd /path/to/repo && CARGO_TOML_PATH=/path/to/repo/Cargo.toml uv run python -m release_version`
   - [x] Verify script can find and read Cargo.toml
   - [x] Verify version calculation works correctly
   - [x] Verify Cargo.toml is updated (if applicable for test)

2. **Test from script directory**
   - [x] Set `CARGO_TOML_PATH` environment variable to absolute path of Cargo.toml
   - [x] Run script from script directory: `cd .github/scripts/release-version && CARGO_TOML_PATH=/path/to/repo/Cargo.toml uv run python -m release_version`
   - [x] Verify script can find Cargo.toml using absolute path
   - [x] Verify version calculation works correctly
   - [x] Verify Cargo.toml is updated correctly

3. **Test without environment variable (default behavior)**
   - [x] Run script from repository root without `CARGO_TOML_PATH` set
   - [x] Verify script defaults to `"Cargo.toml"` and works correctly
   - [x] Verify this maintains backward compatibility for local development

#### Step 5: Test in workflow

1. **Create test branch and PR**
   - [ ] Create a test branch with the changes
   - [ ] Push changes to trigger workflow (or create PR if workflow runs on PR)
   - [ ] Monitor workflow execution

2. **Verify workflow execution**
   - [ ] Check workflow logs to ensure no `FileNotFoundError` for Cargo.toml
   - [ ] Verify script can find Cargo.toml using the environment variable
   - [ ] Verify version is calculated correctly
   - [ ] Verify Cargo.toml is updated in the workflow
   - [ ] Verify commit is created with version update
   - [ ] Verify tag is created (if applicable)

3. **Verify end-to-end functionality**
   - [ ] Confirm the complete release process works
   - [ ] Verify version bump is correct
   - [ ] Verify no regressions in existing functionality

### Phase 2: Rollback Plan

If issues are encountered:

1. **Immediate Rollback**
   - Revert changes to `__main__.py` (remove path resolution logic)
   - Revert changes to workflow (remove `CARGO_TOML_PATH` environment variable)
   - Verify workflow returns to previous (broken) state
   - Document the issue encountered for future investigation

2. **Partial Rollback**
   - If path resolution fails, verify environment variable is set correctly in workflow
   - If absolute path doesn't work, verify `github.workspace` is correct
   - If script can't read environment variable, check Python `os.environ` usage
   - If `update_cargo_version()` fails, verify function signature accepts path parameter

3. **Alternative Approach**
   - If environment variable approach fails, consider:
     - Using relative path `../../Cargo.toml` from script directory
     - Changing workflow to not use `cd` and run from repository root
     - Using `working-directory` parameter in workflow step instead of `cd`

### Implementation Order

1. **Update workflow** (Step 1)
   - Add `CARGO_TOML_PATH` environment variable
   - Test workflow syntax is valid

2. **Update script** (Step 2)
   - Add path resolution logic to `__main__.py`
   - Update function calls to use path

3. **Verify dependencies** (Step 3)
   - Check `cargo.py` supports path parameter
   - Update if necessary

4. **Test locally** (Step 4)
   - Test from different directories
   - Verify path resolution works correctly

5. **Test in workflow** (Step 5)
   - Test complete workflow execution
   - Verify end-to-end functionality

### Risk Assessment

- **Risk Level:** Low
- **Impact if Failed:**
  - Script still cannot find Cargo.toml (same as current broken state)
  - Workflow still fails (same as current state)
  - No additional breakage beyond current issue
- **Mitigation:**
  - Can test locally before committing
  - Can test in workflow on test branch
  - Easy rollback (revert changes)
  - Environment variable approach is standard and well-supported
  - Absolute path is more reliable than relative paths
- **Testing:**
  - Can be fully tested locally before committing
  - Can be tested in workflow on non-main branch
  - Path resolution can be verified with simple print statements
- **Dependencies:**
  - None - standard Python `os.environ` and GitHub Actions functionality
  - No external services or APIs required
  - Uses existing functions that already support path parameters

### Expected Outcomes

After successful implementation:

- **Workflow Functionality:** Script can find and update Cargo.toml correctly using absolute path from environment variable
- **Version Bumping:** Version is calculated and Cargo.toml is updated successfully
- **Release Process:** Releases work correctly with version bumps
- **Path Resolution:** Path resolution is explicit and maintainable using environment variable
- **Backward Compatibility:** Script still works for local development when environment variable is not set (defaults to "Cargo.toml")
- **Reliability:** Absolute path ensures script works regardless of current working directory

## Example Fix

### Before:
```yaml
- name: Calculate version from PR labels
  run: |
    cd .github/scripts/release-version
    uv run python -m release_version  # ❌ Looks for Cargo.toml in wrong directory
```

```python
# __main__.py
update_cargo_version("Cargo.toml", version)  # ❌ Relative path from script dir
```

### After (Implementation):
```yaml
- name: Calculate version from PR labels
  id: version
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    GITHUB_REPOSITORY: ${{ github.repository }}
    CARGO_TOML_PATH: ${{ github.workspace }}/Cargo.toml  # ✅ Explicit absolute path
  run: |
    cd .github/scripts/release-version
    uv run python -m release_version
```

```python
# __main__.py
# Get Cargo.toml path from environment or default
cargo_toml_path = os.environ.get("CARGO_TOML_PATH", "Cargo.toml")  # ✅ Read from env
repo_root = os.path.dirname(cargo_toml_path) or "."

# Calculate version (pass repo_root for reading current version)
version, tag_name = calculate_new_version(github_client, repo_path=repo_root)  # ✅ Pass repo path

# Update Cargo.toml (use full path)
update_cargo_version(cargo_toml_path, version)  # ✅ Use explicit absolute path
```

## References

- [GitHub Actions `github.workspace` variable](https://docs.github.com/en/actions/learn-github-actions/variables#default-environment-variables)
- [Python `os.path` module](https://docs.python.org/3/library/os.path.html)
- [Pathlib documentation](https://docs.python.org/3/library/pathlib.html)
