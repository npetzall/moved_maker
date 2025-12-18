# Implementation Plan: Fix Checksum Creation in Pull Request Workflow

**Status**: ✅ Complete

## Overview
Fix the checksum creation step in the `pull_request.yaml` workflow by making the `mv` command verbose and using absolute paths for the checksum script to avoid path resolution issues.

## Checklist Summary

### Phase 1: Update Workflow Steps
- [x] 2/2 tasks completed

## Context
Reference to corresponding BUG_ document: `plan/25W48/BUG_CREATE_CHECKSUM_BINARY_NOT_FOUND.md`

The checksum creation step fails because it cannot find the renamed binary file. The issue is likely due to:
1. The `mv` command failing silently without verbose output
2. Relative path resolution issues when running the checksum script from `.github/scripts/create-checksum` directory

## Goals
- Make the `mv` command verbose to see what it's doing
- Use absolute paths in the checksum step to avoid path resolution issues
- Ensure the workflow fails early if the rename doesn't work

## Non-Goals
- Changing the checksum script itself (the script is working correctly)
- Modifying other workflow steps beyond the rename and checksum steps
- Adding additional validation beyond what's necessary to fix the issue

## Design Decisions

**Use `-v` flag for `mv` command**: Add verbose flag to `mv` command
  - **Rationale**: The `-v` flag will output what file is being moved and where, making it easier to debug if the rename fails
  - **Alternatives Considered**: Using `set -x` for full script debugging, but that's too verbose for production workflows
  - **Trade-offs**: Minimal - `-v` is a standard flag with no performance impact

**Use absolute paths with `${{ github.workspace }}`**: Prefix all paths in the checksum step with `${{ github.workspace }}`
  - **Rationale**: When the script changes directory to `.github/scripts/create-checksum`, relative paths like `../../target/...` may not resolve correctly. Using absolute paths ensures the paths are always correct regardless of the current working directory
  - **Alternatives Considered**:
    - Using `cd` back to workspace root before running checksum - rejected because it's more complex and error-prone
    - Using `realpath` or `readlink -f` - rejected because it requires additional commands and may not work on all systems
  - **Trade-offs**: None - absolute paths are more reliable and clearer

## Implementation Steps

### Phase 1: Update Workflow Steps

**Objective**: Update the rename and checksum steps in the pull_request.yaml workflow to be more robust

- [x] **Task 1**: Update rename step to use verbose `mv` command
  - [x] Add `-v` flag to the `mv` command in the "Rename binary with version" step
  - [x] Add error checking to verify the source file exists before attempting rename
  - [x] Add verification that the destination file exists after rename
  - **Files**: `.github/workflows/pull_request.yaml`
  - **Dependencies**: None
  - **Testing**: Verify the workflow runs successfully on a test PR
  - **Notes**: The verbose flag will help debug if the rename fails, and the error checking will ensure the job fails early if something goes wrong

- [x] **Task 2**: Update checksum step to use absolute paths
  - [x] Prefix the `--file` argument path with `${{ github.workspace }}`
  - [x] Prefix the `--output` argument path with `${{ github.workspace }}`
  - **Files**: `.github/workflows/pull_request.yaml`
  - **Dependencies**: Task 1 (should be done together, but can be independent)
  - **Testing**: Verify the checksum step can find the binary file and create the checksum successfully
  - **Notes**: This ensures paths are resolved correctly regardless of the current working directory when the script runs

## Files to Modify/Create
- **Modified Files**:
  - `.github/workflows/pull_request.yaml` - Update rename step to use `-v` flag and add error checking, update checksum step to use absolute paths

## Testing Strategy
- **Manual Testing**:
  - Create a test PR and verify the workflow completes successfully
  - Check that the rename step shows verbose output
  - Verify that the checksum file is created correctly
  - Verify that if the binary doesn't exist, the rename step fails with a clear error message

## Breaking Changes
- None - this is a bug fix that only affects internal workflow behavior

## Migration Guide
N/A - no breaking changes

## Documentation Updates
- None required - this is an internal workflow fix

## Success Criteria
- The rename step shows verbose output indicating what file is being moved
- The checksum step successfully finds the binary file using absolute paths
- The workflow completes successfully for PR builds
- If the binary doesn't exist, the rename step fails with a clear error message

## Risks and Mitigations
- **Risk**: Absolute paths might not work if `${{ github.workspace }}` is not set correctly
  - **Mitigation**: `github.workspace` is a standard GitHub Actions variable that is always available, so this risk is minimal
- **Risk**: The verbose `mv` output might be too noisy
  - **Mitigation**: The `-v` flag only outputs one line per file moved, which is minimal and helpful for debugging

## References
- Related BUG_ document: `plan/25W48/BUG_CREATE_CHECKSUM_BINARY_NOT_FOUND.md`
- Related requirements: `plan/25W48/REQ_PR_BINARY_BUILDS.md` (introduced PR binary builds)
- Related requirements: `plan/25W48/REQ_CREATE_CHECKSUM_PROJECT.md` (introduced checksum creation)
