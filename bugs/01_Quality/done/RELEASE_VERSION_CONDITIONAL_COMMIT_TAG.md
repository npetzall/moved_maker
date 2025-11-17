# Bug: release-version workflow creates tag even when version doesn't change

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

## Steps to Fix

1. Check if `Cargo.toml` has changes after version calculation
2. Combine commit and tag steps into a single conditional step
3. Only execute git operations if changes exist
4. Provide clear logging when skipping operations

## Affected Files

- `.github/workflows/release-version.yaml` (workflow file)

## Investigation Needed

1. [x] Confirm: Workflow fails when version doesn't change - **Confirmed, fixed with conditional logic**
2. [x] Verify: When does version not change? (no PRs, no labels, same version calculated) - **Verified: occurs when no PRs merged, no version labels, or same version calculated**
3. [x] Determine: Best way to check for Cargo.toml changes - **Decided: Use `git diff --quiet Cargo.toml`**
4. [ ] Test: Conditional logic works correctly for both scenarios - **Implementation complete, needs workflow testing**

## Status

✅ **IMPLEMENTED** - Conditional commit and tag logic implemented in workflow. Code changes complete, ready for workflow testing to verify behavior in both scenarios (version changed and version unchanged).

## Detailed Implementation Plan

### Phase 1: Implementation Steps

#### Step 1: Add check step for version changes

**File:** `.github/workflows/release-version.yaml`

1. **Add "Check if version changed" step after version calculation**
   - [x] Locate the "Calculate version from PR labels" step (around line 48-56)
   - [x] Add new step "Check if version changed" immediately after the version calculation step
   - [x] Set step `id: version-changed` to allow other steps to reference the output
   - [x] Use `git diff --quiet Cargo.toml` to check if file was modified
   - [x] Output `changed=false` to `GITHUB_OUTPUT` if no changes detected
   - [x] Output `changed=true` to `GITHUB_OUTPUT` if changes detected
   - [x] Add logging message: "No version changes detected, skipping commit and tag" when unchanged
   - [x] Add logging message: "Version changes detected, will commit and tag" when changed
   - [x] Verify the step runs after version calculation but before commit/tag steps

2. **Verify check step structure**
   - [x] Confirm `git diff --quiet` command is correct (returns 0 if no changes, non-zero if changes)
   - [x] Verify `GITHUB_OUTPUT` syntax is correct: `echo "changed=false" >> $GITHUB_OUTPUT`
   - [x] Ensure the step doesn't fail if no changes are detected (should succeed in both cases)
   - [x] Verify step placement in workflow (after version calculation, before commit/tag)

**Expected workflow change:**
```yaml
- name: Calculate version from PR labels
  id: version
  # ... existing step ...

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
```

#### Step 2: Replace commit and tag steps with combined conditional step

**File:** `.github/workflows/release-version.yaml`

1. **Locate existing commit and tag steps**
   - [x] Find "Commit and push version update" step (around line 58-62)
   - [x] Find "Create and push git tag" step (around line 64-67)
   - [x] Note the exact content and structure of both steps
   - [x] Verify these are the steps to be replaced

2. **Create combined conditional step**
   - [x] Remove "Commit and push version update" step
   - [x] Remove "Create and push git tag" step
   - [x] Add new step "Commit, push, and tag version update"
   - [x] Add `if: steps.version-changed.outputs.changed == 'true'` condition to the step
   - [x] Include `git add Cargo.toml` command from original commit step
   - [x] Include `git commit` command with message from original commit step
   - [x] Include `git push origin HEAD:main` command from original commit step
   - [x] Include `git tag -a` command from original tag step
   - [x] Include `git push origin` tag command from original tag step
   - [x] Verify all git operations are in the correct order (add → commit → push → tag → push tag)

3. **Verify conditional step structure**
   - [x] Confirm `if` condition syntax: `if: steps.version-changed.outputs.changed == 'true'`
   - [x] Verify step reference: `steps.version-changed.outputs.changed` matches the check step id
   - [x] Ensure the step is skipped (not failed) when condition is false
   - [x] Verify all git commands use correct variable references: `${{ steps.version.outputs.version }}` and `${{ steps.version.outputs.tag_name }}`

**Expected workflow change:**
```yaml
# Remove these two steps:
# - name: Commit and push version update
#   run: |
#     git add Cargo.toml
#     git commit -m "chore: bump version to ${{ steps.version.outputs.version }}"
#     git push origin HEAD:main
#
# - name: Create and push git tag
#   run: |
#     git tag -a "${{ steps.version.outputs.tag_name }}" -m "Release ${{ steps.version.outputs.tag_name }}"
#     git push origin "${{ steps.version.outputs.tag_name }}"

# Replace with:
- name: Commit, push, and tag version update
  if: steps.version-changed.outputs.changed == 'true'
  run: |
    git add Cargo.toml
    git commit -m "chore: bump version to ${{ steps.version.outputs.version }}"
    git push origin HEAD:main
    git tag -a "${{ steps.version.outputs.tag_name }}" -m "Release ${{ steps.version.outputs.tag_name }}"
    git push origin "${{ steps.version.outputs.tag_name }}"
```

#### Step 3: Verify workflow structure

**File:** `.github/workflows/release-version.yaml`

1. **Verify step order**
   - [x] Confirm "Calculate version from PR labels" step is before check step
   - [x] Confirm "Check if version changed" step is after version calculation
   - [x] Confirm "Commit, push, and tag version update" step is after check step
   - [x] Verify no other steps are between these related steps
   - [x] Check that workflow structure is valid YAML

2. **Verify step dependencies**
   - [x] Confirm check step references version step outputs correctly (if needed)
   - [x] Confirm commit/tag step references check step output: `steps.version-changed.outputs.changed`
   - [x] Confirm commit/tag step references version step outputs: `steps.version.outputs.version` and `steps.version.outputs.tag_name`
   - [x] Verify all variable references use correct syntax: `${{ steps.step-id.outputs.output-name }}`

3. **Verify conditional logic**
   - [x] Confirm check step always runs (no conditions)
   - [x] Confirm commit/tag step only runs when `changed == 'true'`
   - [x] Verify workflow completes successfully when check step outputs `changed=false` (syntax verified, needs workflow testing)
   - [x] Verify workflow executes commit/tag when check step outputs `changed=true` (syntax verified, needs workflow testing)

#### Step 4: Test implementation locally

1. **Test git diff command**
   - [x] Run `git diff --quiet Cargo.toml` when Cargo.toml has no changes (should return exit code 0)
   - [x] Modify Cargo.toml and run `git diff --quiet Cargo.toml` (should return non-zero exit code)
   - [x] Verify the command works correctly in both scenarios
   - [x] Test the command in a clean git state

2. **Test workflow syntax**
   - [x] Validate YAML syntax of the workflow file
   - [x] Check for any syntax errors in the new steps
   - [x] Verify all quotes and indentation are correct
   - [x] Confirm all step names and ids are unique

3. **Test conditional logic (if possible)**
   - [x] Simulate the check step logic locally
   - [x] Verify `GITHUB_OUTPUT` format is correct (if testing locally)
   - [x] Test the conditional expression logic

#### Step 5: Test in workflow

1. **Test with version change scenario**
   - [ ] Create a test branch with the workflow changes
   - [ ] Create a PR with a version label (e.g., `version:minor`)
   - [ ] Merge PR to trigger workflow on main branch
   - [ ] Monitor workflow execution logs
   - [ ] Verify "Check if version changed" step runs and outputs "Version changes detected"
   - [ ] Verify "Commit, push, and tag version update" step executes
   - [ ] Verify Cargo.toml is committed with version update
   - [ ] Verify tag is created and pushed
   - [ ] Verify workflow completes successfully

2. **Test without version change scenario**
   - [ ] Push a commit to main that doesn't change the version (e.g., documentation update)
   - [ ] Monitor workflow execution logs
   - [ ] Verify "Check if version changed" step runs and outputs "No version changes detected"
   - [ ] Verify "Commit, push, and tag version update" step is skipped (not failed)
   - [ ] Verify workflow completes successfully without errors
   - [ ] Confirm no commit or tag is created

3. **Test edge cases**
   - [ ] Test first run scenario (no previous tags, version may not change)
   - [ ] Test multiple PRs with same version label (should result in same version)
   - [ ] Test PRs without version labels (patch bump only, may result in same version if already at patch level)
   - [ ] Verify workflow handles all edge cases gracefully

### Phase 2: Rollback Plan

If issues are encountered:

1. **Immediate Rollback**
   - Revert workflow changes
   - Return to separate commit and tag steps
   - Accept that workflow may fail when version doesn't change

2. **Partial Rollback**
   - If `git diff --quiet` check fails, try alternative method (hashFiles function or git status --porcelain)
   - If step combination causes issues, keep steps separate but both conditional on the same check output
   - If logging is too verbose, reduce log output

3. **Alternative Approach**
   - Keep steps separate but both conditional
   - Use different condition for each step
   - Add explicit skip messages

### Implementation Order

1. **Add check step** (Step 1)
   - Add "Check if version changed" step after version calculation
   - Use `git diff --quiet Cargo.toml` to detect changes
   - Output `changed` status to `GITHUB_OUTPUT`
   - Add logging messages

2. **Replace commit and tag steps** (Step 2)
   - Remove existing "Commit and push version update" step
   - Remove existing "Create and push git tag" step
   - Add combined "Commit, push, and tag version update" step with conditional
   - Verify all git operations are included

3. **Verify workflow structure** (Step 3)
   - Confirm step order is correct
   - Verify step dependencies and variable references
   - Check conditional logic works correctly

4. **Test locally** (Step 4)
   - Test git diff command behavior
   - Validate workflow YAML syntax
   - Simulate conditional logic

5. **Test in workflow** (Step 5)
   - Test with version change scenario
   - Test without version change scenario
   - Test edge cases

### Risk Assessment

- **Risk Level:** Low
- **Impact if Failed:**
  - Conditional check may not work correctly (workflow still fails or creates unnecessary tags)
  - Git operations may still execute when they shouldn't
- **Mitigation:**
  - Can test locally with git commands
  - Can test in workflow on test branch
  - Easy rollback (revert workflow changes)
- **Testing:**
  - Can be tested in workflow on non-main branch
  - Can simulate version changes locally
- **Dependencies:**
  - None - standard git and GitHub Actions functionality

### Expected Outcomes

After successful implementation:

- **Workflow Reliability:** Workflow completes successfully even when version doesn't change
- **Repository Hygiene:** Tags only created when version actually changes
- **Clear Behavior:** Clear logging when operations are skipped or executed
- **Atomic Operations:** Commit and tag are created together or not at all

### Recommended Implementation

**Combined step with explicit check:**

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

**Note:** This approach:
- Explicitly checks for changes
- Provides clear logging
- Combines commit and tag into atomic operation
- Only executes when version actually changed
- Workflow completes successfully even when skipped

## Example Fix

### Before:
```yaml
- name: Commit and push version update
  run: |
    git add Cargo.toml
    git commit -m "chore: bump version to ${{ steps.version.outputs.version }}"  # ❌ Fails if no changes
    git push origin HEAD:main

- name: Create and push git tag
  run: |
    git tag -a "${{ steps.version.outputs.tag_name }}" -m "Release ${{ steps.version.outputs.tag_name }}"  # ❌ Always runs
    git push origin "${{ steps.version.outputs.tag_name }}"
```

### After:
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
  if: steps.version-changed.outputs.changed == 'true'  # ✅ Only runs if version changed
  run: |
    git add Cargo.toml
    git commit -m "chore: bump version to ${{ steps.version.outputs.version }}"
    git push origin HEAD:main
    git tag -a "${{ steps.version.outputs.tag_name }}" -m "Release ${{ steps.version.outputs.tag_name }}"
    git push origin "${{ steps.version.outputs.tag_name }}"
```

## References

- [GitHub Actions conditional execution](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#jobsjob_idif)
- [Git diff documentation](https://git-scm.com/docs/git-diff)
- [GitHub Actions `hashFiles` function](https://docs.github.com/en/actions/learn-github-actions/expressions#hashfiles)
