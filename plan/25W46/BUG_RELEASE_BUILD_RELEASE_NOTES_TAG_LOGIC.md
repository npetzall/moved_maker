# Investigation: Release Build Workflow - Release Notes Generation Logic

## Description

The release notes generation step in `.github/workflows/release-build.yaml` uses `git describe --tags --abbrev=0` to find the last tag, then generates notes from commits between that tag and `HEAD`. However, when the workflow is triggered by a tag push (which is the case for `release-build.yaml`), `HEAD` is the tag itself, which may cause the release notes to be empty or incorrect.

## Current State

**File**: `.github/workflows/release-build.yaml` (lines 182-214)

The release notes generation logic:
```yaml
- name: Generate release notes
  id: release_notes
  run: |
    # Get commits since last tag, or complete history if no tags (first release)
    if git describe --tags --abbrev=0 2>/dev/null; then
      LAST_TAG=$(git describe --tags --abbrev=0)
      NOTES=$(git log ${LAST_TAG}..HEAD --pretty=format:"- %s (%h)" --no-merges)
    else
      # First release: read complete history
      NOTES=$(git log --pretty=format:"- %s (%h)" --no-merges)
    fi
```

## Problem Analysis

### Workflow Trigger Context

The `release-build.yaml` workflow is triggered by:
```yaml
on:
  push:
    tags:
      - 'v*'
```

When a tag is pushed:
- `github.ref` = `refs/tags/v1.0.0` (the tag reference)
- `github.ref_name` = `v1.0.0` (the tag name)
- `HEAD` points to the commit that the tag references

### Issue Scenario

1. **Tag Creation**: The `release-version.yaml` workflow creates and pushes tag `v1.0.0` pointing to commit `ABC123`
2. **Workflow Trigger**: `release-build.yaml` is triggered by the tag push
3. **Checkout**: The workflow checks out the tag (commit `ABC123`)
4. **Release Notes Generation**:
   - `git describe --tags --abbrev=0` returns `v1.0.0` (the current tag)
   - `git log v1.0.0..HEAD` is empty because `HEAD` is the same commit as `v1.0.0`
   - Result: Empty release notes or "No significant changes"

### Expected Behavior

The release notes should contain commits between the **previous** tag and the **current** tag, not between the current tag and itself.

## Root Cause

The issue occurs because when the workflow is triggered by a tag push:
- `git describe --tags --abbrev=0` returns the current tag (the one that triggered the workflow)
- `git log ${LAST_TAG}..HEAD` is empty because `HEAD` points to the same commit as the current tag
- The workflow needs to compare the current tag with the previous tag, not with itself

## Testing Scenarios

### Scenario 1: First Release (No Previous Tag)
- **Setup**: No tags exist
- **Expected**: Show all commits (no-merges)
- **Current Behavior**: Should work (uses `else` branch)

### Scenario 2: Second Release (One Previous Tag)
- **Setup**: Tag `v1.0.0` exists, creating tag `v1.1.0`
- **Expected**: Show commits between `v1.0.0` and `v1.1.0`
- **Current Behavior**: May show empty if `HEAD` is `v1.1.0` and `git describe` returns `v1.1.0`

### Scenario 3: Multiple Tags
- **Setup**: Tags `v1.0.0`, `v1.1.0`, `v1.2.0` exist, creating `v1.3.0`
- **Expected**: Show commits between `v1.2.0` and `v1.3.0`
- **Current Behavior**: May show empty if `HEAD` is `v1.3.0` and `git describe` returns `v1.3.0`


## Related Implementation Plan

See `work/25W46/BUG_RELEASE_BUILD_RELEASE_NOTES_TAG_LOGIC.md` for the detailed implementation plan.
