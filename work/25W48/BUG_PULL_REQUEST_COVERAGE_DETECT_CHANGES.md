# Implementation Plan: Fix Pull Request Coverage Job File Detection

**Status**: ✅ Completed

## Overview
Fix the "Detect changed files" step in the pull request workflow's coverage job to handle cases where there's no merge base between the PR branch and the base branch. The current implementation fails with "fatal: origin/main...HEAD: no merge base" when branches don't share a common ancestor. The solution is to use `fetch-depth: 2` in the checkout step and compare `HEAD^1` (the base branch parent of the merge commit) with `HEAD` (the merge commit itself).

## Checklist Summary

### Phase 1: Update Workflow Steps to Use HEAD^1 HEAD Comparison
- [x] 2/2 tasks completed

## Context
Reference to corresponding BUG_ document: `plan/25W48/BUG_PULL_REQUEST_COVERAGE_DETECT_CHANGES.md`

The "Detect changed files" step in `.github/workflows/pull_request.yaml` (lines 190-203) uses `git diff --name-only origin/${{ github.base_ref }}...HEAD` which requires a merge base between the two branches. When a PR branch doesn't share a common ancestor with the base branch (main), this command fails with "fatal: origin/main...HEAD: no merge base", causing the step to report "No changed Rust source files detected" even when files have been modified.

**Important Context**: GitHub Actions checkout behavior:
- The checkout action performs a shallow clone (`--depth=1` by default) and checks out `refs/remotes/pull/N/merge`, which is a merge commit created by GitHub that merges the PR branch into the base branch
- HEAD is in detached state at this merge commit, which has two parents: `HEAD^1` is the base branch (main) and `HEAD^2` is the PR branch tip
- When the PR branch has no common ancestor with main, git cannot compute a merge base between `origin/main` and `HEAD`, causing the three-dot notation to fail
- **Solution**: Use `fetch-depth: 2` to ensure we have the merge commit and its parent, then use `git diff --name-only HEAD^1 HEAD` to compare the base branch (first parent) with the merge commit directly

## Goals
- Set `fetch-depth: 2` in the checkout step to ensure we have the merge commit and its parent
- Use `git diff --name-only HEAD^1 HEAD` to compare the base branch (first parent) with the merge commit
- Ensure changed Rust source files are detected even when branches don't share a common ancestor
- Maintain backward compatibility with normal PR scenarios
- Preserve existing behavior for all other cases

## Non-Goals
- Changing the overall workflow structure or job dependencies
- Modifying other workflow steps beyond the "Checkout code" and "Detect changed files" steps
- Adding complex git history analysis or branch comparison logic
- Changing the output format or file structure (changed-files.txt)

## Design Decisions

**Use `fetch-depth: 2` and `HEAD^1 HEAD` comparison**: Set fetch depth to 2 in checkout step and use `git diff --name-only HEAD^1 HEAD` to compare the base branch with the merge commit
  - **Rationale**: Since GitHub Actions checks out the merge commit (`refs/remotes/pull/N/merge`), `HEAD` is the merge commit with two parents: `HEAD^1` is the base branch (main) and `HEAD^2` is the PR branch tip. By setting `fetch-depth: 2`, we ensure we have both the merge commit and its first parent. Using `git diff HEAD^1 HEAD` directly compares the base branch with the merge commit, showing all changes introduced by the PR. This works regardless of whether the branches share a common ancestor.
  - **Alternatives Considered**:
    - Fallback strategy with three-dot to two-dot notation - rejected because `HEAD^1 HEAD` is simpler and more direct
    - Use `git diff origin/main HEAD` - rejected because it requires fetching the base branch separately and may fail with no merge base
    - Use `git diff HEAD^2 HEAD` to compare PR branch with merge commit - rejected because we want changes compared to the base branch, not the PR branch itself
    - Use `git log` to find common ancestor manually - rejected as overly complex for this use case
  - **Trade-offs**: `HEAD^1 HEAD` will show all differences between the base branch and the merge commit, which is exactly what we want for detecting changed files in a PR. This is simpler and more reliable than the three-dot notation approach.

## Implementation Steps

### Phase 1: Update Workflow Steps to Use HEAD^1 HEAD Comparison

**Objective**: Modify the "Checkout code" step to use `fetch-depth: 2` and update the "Detect changed files" step to use `HEAD^1 HEAD` comparison

- [x] **Task 1**: Update "Checkout code" step to set fetch-depth
  - [x] Add `fetch-depth: 2` parameter to the checkout action
  - [x] Add comment explaining why fetch-depth: 2 is needed
  - **Files**: `.github/workflows/pull_request.yaml` (lines 150-151)
  - **Dependencies**: None

- [x] **Task 2**: Update "Detect changed files" step to use HEAD^1 HEAD
  - [x] Remove the `git fetch` command (no longer needed)
  - [x] Change `git diff --name-only origin/${{ github.base_ref }}...HEAD` to `git diff --name-only HEAD^1 HEAD`
  - [x] Ensure the rest of the step logic (file filtering, output generation) remains unchanged
  - [x] Add comments explaining that HEAD^1 is the base branch parent and HEAD is the merge commit
  - **Files**: `.github/workflows/pull_request.yaml` (lines 190-203)
  - **Dependencies**: Task 1 (fetch-depth: 2 must be set)
  - **Testing**:
    - Test with a normal PR (should detect changed files correctly)
    - Test with a PR branch that has no merge base (should detect changed files correctly)
    - Verify that changed Rust files are detected in both scenarios
    - Verify that the changed-files.txt file is created correctly
  - **Notes**: This approach is simpler and more reliable than the three-dot notation, and works in all scenarios since we're comparing the merge commit with its first parent (the base branch).

## Files to Modify/Create
- **Modified Files**:
  - `.github/workflows/pull_request.yaml` - Update the "Checkout code" step (lines 150-151) to add `fetch-depth: 2` and update the "Detect changed files" step (lines 190-203) to use `HEAD^1 HEAD` comparison

## Testing Strategy
- **Manual Testing**:
  - Create a test PR from a branch that shares a common ancestor with main (normal case) - should detect changed files using HEAD^1 HEAD
  - Create a test PR from a branch that doesn't share a common ancestor with main (edge case) - should detect changed files using HEAD^1 HEAD
  - Verify that changed Rust source files are detected in both scenarios
  - Verify that the changed-files.txt file contains the correct list of files
  - Verify that the coverage summary step can read the changed-files.txt file correctly
  - Test with PRs that have no Rust file changes - should create empty changed-files.txt

## Breaking Changes
- None - this is a bug fix that improves robustness without changing the interface or expected behavior

## Migration Guide
N/A - no breaking changes

## Documentation Updates
- None required - this is an internal workflow fix that doesn't affect user-facing functionality

## Success Criteria
- The checkout step uses `fetch-depth: 2` to ensure we have the merge commit and its parent
- The "Detect changed files" step uses `git diff --name-only HEAD^1 HEAD` instead of three-dot notation
- The "Detect changed files" step no longer fails with "fatal: origin/main...HEAD: no merge base" error
- Changed Rust source files are detected correctly even when PR branch has no merge base with base branch
- Normal PR workflows (with merge base) continue to work as before
- The changed-files.txt file is created correctly in all scenarios
- The coverage summary step can successfully read and process the changed-files.txt file

## Risks and Mitigations
- **Risk**: `fetch-depth: 2` might increase checkout time slightly
  - **Mitigation**: The increase is minimal (fetching one additional commit), and the reliability improvement is worth it. This is a standard practice for workflows that need to compare with parent commits.
- **Risk**: `HEAD^1 HEAD` might show more files than three-dot notation in some edge cases
  - **Mitigation**: This is acceptable because we're filtering for `src/*.rs` files anyway, and showing all changes in the merge commit is the correct behavior for PR coverage analysis.
- **Risk**: If HEAD is not a merge commit (unlikely in PR context), `HEAD^1` might not be the base branch
  - **Mitigation**: In GitHub Actions PR workflows, HEAD is always the merge commit created by GitHub (`refs/remotes/pull/N/merge`), so this is safe. We'll add a comment explaining this assumption.

## References
- Related BUG_ document: `plan/25W48/BUG_PULL_REQUEST_COVERAGE_DETECT_CHANGES.md`
- Git diff documentation: https://git-scm.com/docs/git-diff
- Git merge-base documentation: https://git-scm.com/docs/git-merge-base
- GitHub Actions workflow syntax: https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions
- GitHub Actions checkout behavior: https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#pull_request (checkout action checks out merge commit `refs/remotes/pull/N/merge`)
