# BUG: Workflows Missing Explicit Tool Availability Checks

**Status**: ✅ Complete

## Description

Multiple GitHub Actions workflows use `jq` and `gh` CLI tools without explicit checks to verify they are installed. While these tools are typically available on GitHub Actions runners, the workflows would benefit from explicit checks with clear error messages using workflow annotation commands to make failures highly visible in the GitHub Actions UI.

## Current State

### Missing `jq` Checks

**File**: `.github/workflows/release-build.yaml`
- **Line 83**: Uses `jq` to process coverage JSON without checking if it's installed
  ```yaml
  jq -r -e -f .config/coverage-threshold-check.jq coverage.json || exit 1
  ```
- **Impact**: If `jq` is missing, the error message is unclear and may be buried in logs

**File**: `.github/workflows/pull_request.yaml`
- **Line 109**: Uses `jq` to process coverage JSON without checking if it's installed
  ```yaml
  jq -r -e -f .config/coverage-threshold-check.jq coverage.json || exit 1
  ```
- **Impact**: If `jq` is missing, the error message is unclear and may be buried in logs

### Missing `gh` CLI Checks

**File**: `.github/workflows/release-build.yaml`
- **Line 225**: Uses `gh` CLI to create GitHub release without checking if it's installed
  ```yaml
  gh release create "${{ github.ref_name }}" \
    --title "Release ${{ github.ref_name }}" \
    --notes-file release_notes.md \
    --verify-tag \
    ...
  ```
- **Impact**: If `gh` CLI is missing, the error message is unclear and may be buried in logs

**File**: `.github/workflows/pr-label.yml`
- **Line 25**: Uses `gh` CLI to view PR commits without checking if it's installed
  ```yaml
  COMMITS=$(gh pr view $PR_NUM --json commits --jq '.commits[].message')
  ```
- **Lines 39, 43, 45**: Uses `gh` CLI to edit PR labels without checking if it's installed
  ```yaml
  gh pr edit $PR_NUM --remove-label "version: major" "version: minor" "version: patch" "breaking" "feature" 2>/dev/null || true
  gh pr edit $PR_NUM --add-label "$VERSION_LABEL"
  gh pr edit $PR_NUM --add-label "$ALT_LABEL"
  ```
- **Impact**: If `gh` CLI is missing, the error message is unclear and may be buried in logs

## Expected State

All tools should have explicit checks before use, with clear error messages using GitHub Actions workflow annotation commands (`::error::`, `::warning::`) to make failures highly visible in the GitHub Actions UI. Each workflow that uses `jq` or `gh` CLI should verify tool availability before attempting to use them.

## Impact

### Developer Experience Impact
- **Severity**: Medium
- **Priority**: Medium

- Unclear error messages when tools are missing
- Failures may be buried in long log outputs
- Difficult to diagnose issues quickly

### Workflow Reliability Impact
- **Severity**: Low (tools are typically available)
- **Priority**: Medium

- Workflow may fail with cryptic errors
- Hard to distinguish between tool missing vs. other errors
- No early failure detection


## Related Implementation Plan

See `work/25W46/BUG_RELEASE_BUILD_MISSING_TOOL_CHECKS.md` for the detailed implementation plan.
