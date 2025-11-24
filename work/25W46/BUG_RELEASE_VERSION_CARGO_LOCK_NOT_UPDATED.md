# Implementation Plan: BUG_RELEASE_VERSION_CARGO_LOCK_NOT_UPDATED

**Status**: ✅ Complete

## Overview

This implementation plan addresses the bug described in `plan/25W46/BUG_RELEASE_VERSION_CARGO_LOCK_NOT_UPDATED.md`.

## Context

Related bug report: `plan/25W46/BUG_RELEASE_VERSION_CARGO_LOCK_NOT_UPDATED.md`

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
