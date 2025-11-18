# Bug: Cargo.lock isn't updated when Cargo.toml version changes

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

## Detailed Implementation Plan

### Phase 1: Implementation Steps

#### Step 1: Add Cargo.lock update to `__main__.py`

**File:** `.github/scripts/release-version/src/release_version/__main__.py`

1. **Add Cargo.lock update after Cargo.toml update**
   - [x] After `update_cargo_version()` succeeds and `version_updated` is `True`
   - [x] Run `cargo update --package move_maker` to update `Cargo.lock`
   - [x] Use `subprocess.run()` to execute the command
   - [x] Set `cwd` to `repo_root` to ensure correct working directory
   - [x] Handle errors appropriately (print error, exit with error code)
   - [x] Add progress logging: "Updating Cargo.lock with version {version}..."
   - [x] Add success logging: "✓ Cargo.lock updated to version {version}"

2. **Verify package name**
   - [x] Confirm package name is `move_maker` (from `Cargo.toml`)
   - [x] Read package name dynamically from `Cargo.toml` with fallback to `move_maker`
   - [x] Use correct package name in `cargo update` command

3. **Error handling**
   - [x] Catch `subprocess.CalledProcessError` exceptions
   - [x] Print error message with stdout/stderr
   - [x] Exit with error code if `cargo update` fails
   - [x] Ensure workflow fails if `Cargo.lock` update fails

**Implemented code change:**
```python
# Update Cargo.toml (use full path)
try:
    print(f"Updating Cargo.toml with version {version}...")
    version_updated = update_cargo_version(cargo_toml_path, version)
    if version_updated:
        print(f"✓ Cargo.toml updated to version {version}")

        # Update Cargo.lock with the new version
        # Read package name from Cargo.toml
        try:
            with open(cargo_toml_path, "r", encoding="utf-8") as f:
                cargo = tomlkit.parse(f.read())
            package_name = cargo.get("package", {}).get("name", "move_maker")
        except Exception as e:
            print(f"Warning: Could not read package name from Cargo.toml: {e}", file=sys.stderr)
            print("Using default package name: move_maker", file=sys.stderr)
            package_name = "move_maker"

        try:
            print(f"Updating Cargo.lock with version {version}...")
            result = subprocess.run(
                ["cargo", "update", "--package", package_name],
                cwd=repo_root,
                capture_output=True,
                text=True,
                check=True,
            )
            print(f"✓ Cargo.lock updated to version {version}")
        except subprocess.CalledProcessError as e:
            print(f"Error updating Cargo.lock: {e}", file=sys.stderr)
            print(f"stdout: {e.stdout}", file=sys.stderr)
            print(f"stderr: {e.stderr}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"ℹ Cargo.toml already at version {version}, no update needed")
except Exception as e:
    print(f"Error updating Cargo.toml: {e}", file=sys.stderr)
    sys.exit(1)
```

#### Step 2: Update workflow to commit both files

**File:** `.github/workflows/release-version.yaml`

1. **Update git add command**
   - [x] Locate the "Commit, push, and tag version update" step
   - [x] Change `git add Cargo.toml` to `git add Cargo.toml Cargo.lock`
   - [x] Ensure both files are staged together
   - [x] Verify commit message remains the same

2. **Verify workflow step structure**
   - [x] Confirm the step still runs conditionally (`if: steps.version-changed.outputs.changed == 'true'`)
   - [x] Ensure commit message includes version number
   - [x] Verify tag creation and push remain unchanged

**Implemented workflow change:**
```yaml
- name: Commit, push, and tag version update
  if: steps.version-changed.outputs.changed == 'true'
  run: |
    git add Cargo.toml Cargo.lock
    git commit -m "chore: bump version to ${{ steps.version.outputs.version }}"
    git push origin HEAD:main
    git tag -a "${{ steps.version.outputs.tag_name }}" -m "Release ${{ steps.version.outputs.tag_name }}"
    git push origin "${{ steps.version.outputs.tag_name }}"
```

#### Step 3: Update version change detection

**File:** `.github/workflows/release-version.yaml`

1. **Update version change detection**
   - [x] Locate the "Check if version changed" step
   - [x] Consider checking both `Cargo.toml` and `Cargo.lock` for changes
   - [x] Or keep current check (only `Cargo.toml`) since `Cargo.lock` will be updated by script
   - [x] Current approach (check only `Cargo.toml`) is acceptable since script updates `Cargo.lock` automatically

**Note:** The current approach of checking only `Cargo.toml` is acceptable because:
- The script will update `Cargo.lock` automatically after updating `Cargo.toml`
- If `Cargo.toml` changes, `Cargo.lock` will also change
- Checking both files would be redundant

#### Step 4: Test implementation locally

1. **Test Cargo.lock update**
   - [x] Code implementation complete - ready for workflow testing
   - [ ] Run script locally to update `Cargo.toml` (pending workflow testing)
   - [ ] Verify `cargo update --package move_maker` runs successfully (pending workflow testing)
   - [ ] Verify `Cargo.lock` version is updated correctly (pending workflow testing)
   - [ ] Check that version in `Cargo.lock` matches `Cargo.toml` (pending workflow testing)

2. **Test workflow changes**
   - [x] Code implementation complete - ready for workflow testing
   - [ ] Create test branch with changes (pending workflow testing)
   - [ ] Trigger workflow (or simulate workflow steps) (pending workflow testing)
   - [ ] Verify both files are staged correctly (pending workflow testing)
   - [ ] Verify both files are committed together (pending workflow testing)
   - [ ] Verify commit message is correct (pending workflow testing)

3. **Test edge cases**
   - [x] Code handles version unchanged scenario (doesn't update `Cargo.lock` if `Cargo.toml` unchanged)
   - [x] Code handles `cargo update` failures (exits with error code)
   - [ ] Test when `Cargo.lock` doesn't exist (pending workflow testing)

#### Step 5: Test in workflow

1. **Test version update scenario**
   - [x] Code implementation complete - ready for workflow testing
   - [ ] Create test branch with changes (pending workflow testing)
   - [ ] Ensure version will change (add commits or PR labels) (pending workflow testing)
   - [ ] Push to trigger workflow (pending workflow testing)
   - [ ] Monitor workflow execution logs (pending workflow testing)
   - [ ] Verify `Cargo.toml` is updated (pending workflow testing)
   - [ ] Verify `Cargo.lock` is updated (pending workflow testing)
   - [ ] Verify both files are committed together (pending workflow testing)
   - [ ] Verify commit message is correct (pending workflow testing)
   - [ ] Verify tag is created correctly (pending workflow testing)

2. **Test no version change scenario**
   - [x] Code implementation complete - ready for workflow testing
   - [ ] Create test branch with no version change (pending workflow testing)
   - [ ] Push to trigger workflow (pending workflow testing)
   - [ ] Verify workflow skips commit/tag step (pending workflow testing)
   - [ ] Verify `Cargo.lock` is not updated unnecessarily (pending workflow testing)

### Phase 2: Rollback Plan

If issues are encountered:

1. **Immediate Rollback**
   - Revert changes to `__main__.py` (remove `Cargo.lock` update)
   - Revert changes to workflow (remove `Cargo.lock` from `git add`)
   - Return to previous behavior (only `Cargo.toml` updated)

2. **Partial Rollback**
   - If `cargo update` fails, add better error handling
   - If workflow fails, verify `cargo` is available in workflow environment
   - If `Cargo.lock` update doesn't work, investigate `cargo update` command options

3. **Alternative Approach**
   - If `cargo update --package` doesn't work, try `cargo build` (updates `Cargo.lock` automatically)
   - If package name is incorrect, read from `Cargo.toml` dynamically
   - If working directory is wrong, verify `repo_root` calculation

### Implementation Order

1. **Add Cargo.lock update to script** (Step 1)
   - Add `cargo update --package move_maker` after `Cargo.toml` update
   - Add error handling and logging
   - Test locally

2. **Update workflow to commit both files** (Step 2)
   - Update `git add` command to include `Cargo.lock`
   - Test workflow syntax

3. **Test implementation** (Steps 3-5)
   - Test locally
   - Test in workflow
   - Verify end-to-end functionality

### Risk Assessment

- **Risk Level:** Low
- **Impact if Failed:**
  - `Cargo.lock` may not update correctly
  - Workflow may fail if `cargo update` fails
  - Both files may not be committed together
- **Mitigation:**
  - Can test locally before committing
  - Can test in workflow on test branch
  - Easy rollback (revert changes)
  - `cargo update --package` is standard Cargo command
  - Error handling ensures workflow fails clearly if update fails
- **Testing:**
  - Can be fully tested locally before committing
  - Can be tested in workflow on non-main branch
  - `cargo update` command can be verified manually
- **Dependencies:**
  - `cargo` must be available in workflow environment (already available in Rust workflows)
  - Package name must be correct (`move_maker`)

### Expected Outcomes

After successful implementation:

- **Version Consistency:** Both `Cargo.toml` and `Cargo.lock` have the same version after update
- **Release Process:** Both files are committed together in version bump commits
- **Build Consistency:** Version information is consistent across both files
- **Automation:** `Cargo.lock` is updated automatically when `Cargo.toml` version changes
- **Reliability:** Workflow handles `Cargo.lock` update correctly with proper error handling

## Example Fix

### Before:
```python
# __main__.py
version_updated = update_cargo_version(cargo_toml_path, version)
if version_updated:
    print(f"✓ Cargo.toml updated to version {version}")
# ❌ Cargo.lock is not updated
```

```yaml
# release-version.yaml
- name: Commit, push, and tag version update
  run: |
    git add Cargo.toml  # ❌ Only Cargo.toml
    git commit -m "chore: bump version to ${{ steps.version.outputs.version }}"
```

### After (Implementation):
```python
# __main__.py
version_updated = update_cargo_version(cargo_toml_path, version)
if version_updated:
    print(f"✓ Cargo.toml updated to version {version}")

    # Update Cargo.lock with the new version
    # Read package name from Cargo.toml
    try:
        with open(cargo_toml_path, "r", encoding="utf-8") as f:
            cargo = tomlkit.parse(f.read())
        package_name = cargo.get("package", {}).get("name", "move_maker")
    except Exception as e:
        print(f"Warning: Could not read package name from Cargo.toml: {e}", file=sys.stderr)
        print("Using default package name: move_maker", file=sys.stderr)
        package_name = "move_maker"

    try:
        print(f"Updating Cargo.lock with version {version}...")
        result = subprocess.run(
            ["cargo", "update", "--package", package_name],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"✓ Cargo.lock updated to version {version}")
    except subprocess.CalledProcessError as e:
        print(f"Error updating Cargo.lock: {e}", file=sys.stderr)
        print(f"stdout: {e.stdout}", file=sys.stderr)
        print(f"stderr: {e.stderr}", file=sys.stderr)
        sys.exit(1)
```

```yaml
# release-version.yaml
- name: Commit, push, and tag version update
  run: |
    git add Cargo.toml Cargo.lock  # ✅ Both files
    git commit -m "chore: bump version to ${{ steps.version.outputs.version }}"
```

## References

- [Cargo update documentation](https://doc.rust-lang.org/cargo/commands/cargo-update.html)
- [Cargo.lock file format](https://doc.rust-lang.org/cargo/guide/cargo-toml-vs-cargo-lock.html)
- [GitHub Actions workflow syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
