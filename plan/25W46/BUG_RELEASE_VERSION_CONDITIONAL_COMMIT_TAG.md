# BUG: release-version workflow creates tag even when version doesn't change

**Status**: ✅ Complete

## Description

The `release-version` workflow always creates and pushes a git tag, even when the version in `Cargo.toml` hasn't changed. This can result in duplicate tags with the same version, or tags being created when no actual version bump occurred. The workflow should only commit and create a tag if `Cargo.toml` was actually modified.

## Current State

✅ **IMPLEMENTED** - Conditional commit and tag logic implemented. Ready for workflow testing.

**Previous (incorrect) state:**
- Workflow always attempted to commit `Cargo.toml` (would fail if no changes)
- Workflow always created and pushed a git tag
- No check if version actually changed
- Separate steps for commit and tag push
- If commit failed (no changes), tag step still ran (or workflow failed at commit step)

**Current (correct) state:**
- Workflow checks if `Cargo.toml` has changes using `git diff --quiet Cargo.toml`
- Check step outputs `changed=true` or `changed=false` to `GITHUB_OUTPUT`
- Commit and tag steps combined into single conditional step
- Conditional step only runs when `changed == 'true'`
- Workflow completes successfully even when version doesn't change (step is skipped, not failed)

**Previous workflow steps:**
```yaml
- name: Commit and push version update
  run: |
    git add Cargo.toml
    git commit -m "chore: bump version to ${{ steps.version.outputs.version }}"
    git push origin HEAD:main

- name: Create and push git tag
  run: |
    git tag -a "${{ steps.version.outputs.tag_name }}" -m "Release ${{ steps.version.outputs.tag_name }}"
    git push origin "${{ steps.version.outputs.tag_name }}"
```

**Current workflow steps:**
```yaml
- name: Check if version changed
  id: version-changed
  run: |
    if git diff --quiet Cargo.toml; then
      echo "changed=false" >> $GITHUB_OUTPUT
      echo "No version changes detected, skipping commit and tag"
    else
      echo "changed=true" >> $GITHUB_OUTPUT
      echo "Version changes detected, will commit and tag"
    fi

- name: Commit, push, and tag version update
  if: steps.version-changed.outputs.changed == 'true'
  run: |
    git add Cargo.toml
    git commit -m "chore: bump version to ${{ steps.version.outputs.version }}"
    git push origin HEAD:main
    git tag -a "${{ steps.version.outputs.tag_name }}" -m "Release ${{ steps.version.outputs.tag_name }}"
    git push origin "${{ steps.version.outputs.tag_name }}"
```

**Previous problems (now fixed):**
1. ✅ Commit step would fail if `Cargo.toml` hadn't changed (no staged changes) - **Fixed: Check step prevents commit when no changes**
2. ✅ Tag was created even if commit failed or was skipped - **Fixed: Combined conditional step ensures atomic operation**
3. ✅ No conditional logic to skip steps when version hasn't changed - **Fixed: Check step with conditional execution**
4. ✅ Two separate steps that should be atomic - **Fixed: Combined into single conditional step**

## Expected State

The workflow should:
1. Check if `Cargo.toml` has changes after the version calculation step
2. Only commit and push if changes exist
3. Only create and push tag if commit was successful
4. Combine commit and tag operations into a single conditional step
5. Skip both operations if version hasn't changed

**Expected workflow behavior:**
- If version changed: Commit Cargo.toml → Push commit → Create tag → Push tag
- If version unchanged: Skip all git operations, workflow completes successfully

## Impact

### Repository Hygiene Impact
- **Severity**: Medium
- **Priority**: Medium

Without conditional logic:
- Workflow may fail when version doesn't change (commit fails)
- Tags may be created unnecessarily
- Duplicate tags with same version may be created
- Git history may contain failed commit attempts

### Workflow Reliability Impact
- **Severity**: High
- **Priority**: High

- Workflow fails when version doesn't change (blocks other workflows)
- Unclear error messages when commit fails
- Inconsistent behavior (sometimes tags created, sometimes not)

### Developer Experience Impact
- **Severity**: Medium
- **Priority**: Medium

- Confusing workflow failures
- Need to manually check if version changed
- Unclear why workflow failed

## Root Cause

The workflow assumes the version will always change, but in reality:
- If no PRs were merged since last tag, version may not change
- If PRs don't have version labels, only patch bump occurs (may result in same version if already at that patch level)
- First run may use existing version from Cargo.toml (no change)

The workflow doesn't check if `Cargo.toml` was actually modified before attempting to commit.


## Related Implementation Plan

See `work/25W46/BUG_RELEASE_VERSION_CONDITIONAL_COMMIT_TAG.md` for the detailed implementation plan.
