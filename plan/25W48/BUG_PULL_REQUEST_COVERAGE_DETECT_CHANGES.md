# BUG: Pull request workflow coverage job doesn't detect changes in cli.rs

**Status**: ✅ Fixed

## Overview
The "Detect changed files" step in the pull request workflow's coverage job fails to detect changed Rust source files when there's no merge base between the PR branch and the base branch, resulting in "fatal: origin/main...HEAD: no merge base" error. The solution is to use `fetch-depth: 2` in the checkout step and compare `HEAD^1` (the base branch parent of the merge commit) with `HEAD` (the merge commit itself).

## Environment
- **OS**: GitHub Actions (ubuntu-latest)
- **Rust Version**: 1.90.0
- **Tool Version**: N/A (workflow issue)
- **Terraform Version**: N/A

## Steps to Reproduce
1. Create a pull request from a branch that doesn't share a common ancestor with the base branch (main)
2. Trigger the pull request workflow
3. Observe the "Detect changed files" step in the coverage job

## Expected Behavior
The workflow should detect changed Rust source files (e.g., `src/cli.rs`) even when there's no merge base between the branches. The step should handle this edge case gracefully and still identify changed files. Since GitHub Actions checks out the merge commit (`refs/remotes/pull/N/merge`), we can use `git diff HEAD^1 HEAD` to compare the base branch (first parent) with the merge commit.

## Actual Behavior
The `git diff --name-only origin/${{ github.base_ref }}...HEAD` command fails with "fatal: origin/main...HEAD: no merge base", causing the step to report "No changed Rust source files detected" even when files like `src/cli.rs` have been modified.

## Error Messages / Output
```
Run # Get changed Rust source files in PR for coverage summary
  # Get changed Rust source files in PR for coverage summary
  git fetch origin main:main || true
  CHANGED_FILES=$(git diff --name-only origin/main...HEAD | grep '\.rs$' | grep '^src/' || true)
  if [ -n "$CHANGED_FILES" ]; then
    echo "$CHANGED_FILES" > changed-files.txt
    echo "Changed files detected:"
    echo "$CHANGED_FILES"
  else
    touch changed-files.txt
    echo "No changed Rust source files detected"
  fi
  shell: /usr/bin/bash -e {0}
  env:
    CARGO_HOME: /home/runner/.cargo
    CARGO_INCREMENTAL: 0
    CARGO_TERM_COLOR: always
    CACHE_ON_FAILURE: false
From https://github.com/npetzall/moved_maker
 * [new branch]      main       -> main
 * [new branch]      main       -> origin/main
 * [new tag]         v0.1.8     -> v0.1.8
 * [new tag]         v0.2.0     -> v0.2.0
fatal: origin/main...HEAD: no merge base
No changed Rust source files detected
```

## Minimal Reproduction Case
The issue occurs in the workflow step at `.github/workflows/pull_request.yaml` lines 190-203. The `git diff` command using three-dot notation (`...`) requires a merge base, which may not exist in certain branch scenarios.

## Additional Context
- **Affected files**:
  - `.github/workflows/pull_request.yaml` (line 150-151, "Checkout code" step - needs `fetch-depth: 2`)
  - `.github/workflows/pull_request.yaml` (lines 190-203, "Detect changed files" step - needs to use `HEAD^1 HEAD`)
- **Root cause**: The `git diff --name-only origin/${{ github.base_ref }}...HEAD` command fails when there's no merge base between the branches. Since GitHub Actions checks out the merge commit, we can use `HEAD^1` (first parent = base branch) and `HEAD` (merge commit) directly.
- **Solution**: Set `fetch-depth: 2` in checkout step to ensure we have the merge commit and its parent, then use `git diff --name-only HEAD^1 HEAD` instead of the three-dot notation.
- **Impact**: Coverage summary for changed files is not generated when this error occurs, even though files like `src/cli.rs` may have been modified
- **Frequency**: Occurs when PR branch doesn't share a common ancestor with base branch
- **Workaround**: None currently - the step fails silently and creates an empty `changed-files.txt`

## Related Issues
- Related PRs: N/A
