# Implementation Plan: Fix PR Version Error Message Ordering

**Status**: ✅ Complete

## Overview
Fix the output ordering issue where error messages printed to stderr appear before informational messages printed to stdout, causing confusing output when validation fails during PR version updates. The solution is to print all messages to stdout instead of stderr, ensuring consistent chronological ordering.

## Checklist Summary

### Phase 1: Update Error Messages to stdout
- [x] 3/3 tasks completed

### Phase 2: Remove Unnecessary Flush Calls
- [x] 1/1 tasks completed

### Phase 3: Testing and Verification
- [x] 1/1 tasks completed

## Context
Reference to corresponding BUG_ document: `plan/25W48/BUG_PR_VERSION_UPDATE_ERROR_ORDERING.md`

**Current State**: Error messages are printed to stderr while informational messages are printed to stdout. Because stderr is unbuffered and stdout is buffered, stderr output appears first even when stdout print statements execute earlier in the code. This causes the error message to appear before the "Updating Cargo.toml..." message, making the output confusing.

**Problem**: When validation fails during PR version update, users see:
```
Error updating Cargo.toml: Invalid version format...
Updating Cargo.toml with version 0.2.2-pr26+c5c00e2...
```

Instead of the expected:
```
Updating Cargo.toml with version 0.2.2-pr26+c5c00e2...
Error updating Cargo.toml: Invalid version format...
```

## Goals
- Ensure all output appears in chronological order matching code execution
- Fix the specific issue where error messages appear before the "Updating Cargo.toml..." message
- Simplify the code by removing unnecessary `sys.stdout.flush()` calls that were added as a workaround
- Maintain backward compatibility (no functional changes, only output ordering)

## Non-Goals
- Changing the actual error handling logic (only changing where errors are printed)
- Modifying the validation logic itself (that's handled in `BUG_PR_VERSION_VALIDATION_FAILURE.md`)
- Changing exit codes or error behavior

## Design Decisions

**Decision 1**: Print all messages to stdout instead of stderr
- **Rationale**: stdout and stderr have different buffering behavior (stdout is buffered, stderr is unbuffered), which causes ordering issues. By using stdout for all messages, we ensure consistent ordering. Since this is a script that runs in GitHub Actions, stdout is appropriate for all output including errors.
- **Alternatives Considered**:
  - Using `sys.stdout.flush()` before every stderr print: This is a workaround that doesn't solve the root cause and adds unnecessary complexity
  - Making stdout unbuffered: This could have performance implications and doesn't address the fundamental issue of mixing streams
- **Trade-offs**: Error messages will no longer be separated to stderr, but this is acceptable for a script that runs in CI/CD where all output is captured together anyway.

**Decision 2**: Remove `sys.stdout.flush()` calls added in previous bug fix
- **Rationale**: These flush calls were added as a workaround for the ordering issue. Once we fix the root cause by using stdout for all messages, these flush calls are no longer needed.
- **Alternatives Considered**:
  - Keeping the flush calls: This would be redundant and add unnecessary complexity
- **Trade-offs**: None - removing them simplifies the code.

## Implementation Steps

### Phase 1: Update Error Messages to stdout

**Objective**: Change all error and warning messages from stderr to stdout to ensure consistent output ordering.

- [x] **Task 1**: Update error messages in `__main__.py`
  - [x] Change line 22: Remove `file=sys.stderr` from GITHUB_TOKEN error
  - [x] Change line 28: Remove `file=sys.stderr` from GITHUB_REPOSITORY error
  - [x] Change line 36: Remove `file=sys.stderr` from GitHub client initialization error
  - [x] Change line 48: Remove `file=sys.stderr` from PR_NUMBER error
  - [x] Change line 54: Remove `file=sys.stderr` from Invalid PR_NUMBER error
  - [x] Change line 59: Remove `file=sys.stderr` from COMMIT_SHA error
  - [x] Change line 72: Remove `file=sys.stderr` from PR version calculation error
  - [x] Change line 77: Remove `file=sys.stderr` from unknown VERSION_MODE warning
  - [x] Change line 85: Remove `file=sys.stderr` from version calculation error
  - [x] Change line 102: Remove `file=sys.stderr` from package name warning
  - [x] Change line 103: Remove `file=sys.stderr` from default package name message
  - [x] Change line 117: Remove `file=sys.stderr` from Cargo.lock update error
  - [x] Change line 118: Remove `file=sys.stderr` from Cargo.lock stdout output
  - [x] Change line 119: Remove `file=sys.stderr` from Cargo.lock stderr output
  - [x] Change line 126: Remove `file=sys.stderr` from Cargo.toml update error
  - [x] Change line 147: Remove `file=sys.stderr` from GITHUB_OUTPUT write error
  - [x] Change line 161: Remove `file=sys.stderr` from top-level exception handler error
  - **Files**: `.github/scripts/version/src/version/__main__.py`
  - **Dependencies**: None
  - **Testing**: Run the script in PR mode and verify error messages appear after informational messages
  - **Notes**: All error messages should use `print()` without `file=sys.stderr` parameter

- [x] **Task 2**: Update error messages in `cargo.py`
  - [x] Change line 59: Remove `file=sys.stderr` from TOML parsing error in `read_cargo_version()`
  - [x] Change line 120: Remove `file=sys.stderr` from TOML parsing error in `update_cargo_version()`
  - **Files**: `.github/scripts/version/src/version/cargo.py`
  - **Dependencies**: None
  - **Testing**: Trigger validation errors and verify output ordering
  - **Notes**: These are the key error messages that cause the ordering issue

- [x] **Task 3**: Update error messages in `version.py` and `github_client.py`
  - [x] Change line 54 in `version.py`: Remove `file=sys.stderr` from tag retrieval error
  - [x] Change line 79 in `version.py`: Remove `file=sys.stderr` from tag timestamp error
  - [x] Change line 82 in `version.py`: Remove `file=sys.stderr` from timestamp parsing error
  - [x] Change line 131 in `version.py`: Remove `file=sys.stderr` from commit count error (first occurrence)
  - [x] Change line 134 in `version.py`: Remove `file=sys.stderr` from commit count error (second occurrence)
  - [x] Change line 137 in `version.py`: Remove `file=sys.stderr` from commit count parsing error
  - [x] Change line 212 in `version.py`: Remove `file=sys.stderr` from version calculation error
  - [x] Change line 37 in `github_client.py`: Remove `file=sys.stderr` from repository access error
  - [x] Change line 83 in `github_client.py`: Remove `file=sys.stderr` from merged PRs error
  - **Files**: `.github/scripts/version/src/version/version.py`, `.github/scripts/version/src/version/github_client.py`
  - **Dependencies**: None
  - **Testing**: Trigger various error conditions and verify output ordering
  - **Notes**: These ensure consistency across all error messages in the codebase

### Phase 2: Remove Unnecessary Flush Calls

**Objective**: Remove `sys.stdout.flush()` calls that were added as a workaround and are no longer needed.

- [x] **Task 1**: Remove flush calls from `__main__.py` and `version.py`
  - [x] Remove line 69-70 in `__main__.py`: Remove `sys.stdout.flush()` after PR version calculation
  - [x] Remove line 82-83 in `__main__.py`: Remove `sys.stdout.flush()` after release version calculation
  - [x] Remove line 124-125 in `__main__.py`: Remove `sys.stdout.flush()` before Cargo.toml error
  - [x] Remove line 159-160 in `__main__.py`: Remove `sys.stdout.flush()` in top-level exception handler
  - [x] Remove line 289-290 in `version.py`: Remove `sys.stdout.flush()` after version calculation summary
  - [x] Remove line 393-394 in `version.py`: Remove `sys.stdout.flush()` after PR version calculation summary
  - **Files**: `.github/scripts/version/src/version/__main__.py`, `.github/scripts/version/src/version/version.py`
  - **Dependencies**: Phase 1 must be complete
  - **Testing**: Verify output ordering is still correct without flush calls
  - **Notes**: These flush calls were added in `BUG_PR_VERSION_ERROR_ORDERING` and are no longer needed

### Phase 3: Testing and Verification

**Objective**: Verify that the fix works correctly and output ordering is correct.

- [x] **Task 1**: Test error message ordering
  - [x] Create a test scenario that triggers a validation error (e.g., PR version with build metadata)
  - [x] Run the version script in PR mode and capture output
  - [x] Verify that "Updating Cargo.toml with version..." appears before error message
  - [x] Verify that all output is in chronological order
  - [x] Test with successful version updates to ensure normal flow still works
  - **Files**: Test script or manual testing
  - **Dependencies**: Phases 1 and 2 must be complete
  - **Testing**: Manual testing in GitHub Actions or local environment
  - **Notes**: The test should reproduce the exact scenario from the bug report

## Files to Modify/Create
- **Modified Files**:
  - `.github/scripts/version/src/version/__main__.py` - Change all error/warning messages from stderr to stdout, remove flush calls
  - `.github/scripts/version/src/version/cargo.py` - Change error messages from stderr to stdout
  - `.github/scripts/version/src/version/version.py` - Change error messages from stderr to stdout, remove flush calls
  - `.github/scripts/version/src/version/github_client.py` - Change error messages from stderr to stdout

## Testing Strategy
- **Unit Tests**: Not applicable - this is primarily an output ordering fix
- **Integration Tests**: Test the version script with various error scenarios to verify output ordering
- **Manual Testing**:
  - Run the script in PR mode with a version that triggers validation error
  - Verify output order matches expected chronological order
  - Test successful scenarios to ensure no regressions

## Breaking Changes
None - this is a bug fix that only changes output ordering, not functionality or API.

## Migration Guide
N/A - no breaking changes.

## Documentation Updates
- [x] No documentation updates needed (internal script, no user-facing changes)

## Success Criteria
- Error messages appear after the "Updating Cargo.toml..." message when validation fails
- All output appears in chronological order matching code execution
- No `sys.stdout.flush()` calls remain in the codebase (except if needed for other reasons)
- Successful version updates continue to work correctly
- All error scenarios produce correctly ordered output

## Risks and Mitigations
- **Risk**: Changing error output from stderr to stdout might affect log parsing or filtering in CI/CD
  - **Mitigation**: This is acceptable for a script that runs in GitHub Actions where all output is captured together. The benefit of correct ordering outweighs this minor concern.
- **Risk**: Removing flush calls might cause buffering issues in edge cases
  - **Mitigation**: Since all output now goes to stdout with consistent buffering, flush calls are not needed. If issues arise, we can add targeted flushes, but this should not be necessary.

## References
- Related BUG_ document: `plan/25W48/BUG_PR_VERSION_UPDATE_ERROR_ORDERING.md`
- Related bugs: `plan/25W48/BUG_PR_VERSION_ERROR_ORDERING.md` (previous fix that added flush calls), `plan/25W48/BUG_PR_VERSION_VALIDATION_FAILURE.md` (the validation error that exposes this ordering issue)
- Related PRs: #26 (the PR that triggered this bug)
- Related requirements: `plan/25W48/REQ_PR_BINARY_BUILDS.md`
