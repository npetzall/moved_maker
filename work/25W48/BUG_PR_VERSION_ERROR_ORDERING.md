# Implementation Plan: Fix PR Version Error Message Ordering

**Status**: ✅ Complete

## Overview
Fix the output ordering issue where error messages appear before calculation steps complete during PR version calculation. This is caused by Python's output buffering causing stderr to flush before stdout.

## Checklist Summary

### Phase 1: Fix Output Buffering in Main Entry Point
- [x] 2/2 tasks completed

### Phase 2: Fix Output Buffering in Version Calculation
- [x] 1/1 tasks completed

### Phase 3: Testing and Verification
- [x] 1/1 tasks completed

## Context
Reference to corresponding BUG_ document: `plan/25W48/BUG_PR_VERSION_ERROR_ORDERING.md`

**Current State**: When the version script fails during PR version calculation, the error message appears at the beginning of the output instead of after the calculation steps complete. This makes debugging difficult as the error is shown before the context of what was being calculated.

**Problem Statement**: Python's output buffering causes stderr (error messages) to flush before stdout (calculation steps), resulting in error messages appearing before the calculation context.

## Goals
- Ensure all calculation steps and summary are printed before any error messages
- Fix output ordering so errors appear at the end of output, after calculation context
- Maintain backward compatibility with existing output format
- Fix applies to both PR mode and release mode for consistency

## Non-Goals
- Changing the error message format or content
- Modifying the calculation logic itself
- Fixing the underlying validation issue (handled by BUG_PR_VERSION_VALIDATION_FAILURE)

## Design Decisions

**Important**: Document all key architectural and implementation decisions here. This section should explain the "why" behind major choices, not just the "what".

- **Flush stdout at key points**: Explicitly flush stdout after calculation steps complete and before error handling
  - **Rationale**: Python's default buffering can cause stdout to be buffered while stderr flushes immediately, especially when exceptions occur. Explicit flushing ensures output appears in the correct order.
  - **Alternatives Considered**:
    - Using unbuffered output mode (`python -u`) - rejected because it requires workflow changes and affects all output
    - Collecting all output and printing at once - rejected because it's more complex and changes the real-time output behavior
    - Using `sys.stdout.flush()` only in exception handlers - rejected because it doesn't fix the root cause (buffering before errors)
  - **Trade-offs**: Minimal code changes, maintains existing output behavior, requires explicit flush calls at strategic points

- **Flush after calculation, before update**: Flush stdout immediately after `calculate_pr_version()` or `calculate_new_version()` completes
  - **Rationale**: This ensures all calculation output is visible before any error from `update_cargo_version()` occurs
  - **Alternatives Considered**:
    - Flushing only in exception handlers - rejected because stdout may already be buffered when exception occurs
    - Flushing after every print statement - rejected as too verbose and unnecessary
  - **Trade-offs**: Simple, targeted fix that addresses the specific issue without over-engineering

- **Flush in exception handlers**: Flush stdout before printing errors in exception handlers
  - **Rationale**: Ensures any remaining buffered stdout output is flushed before error messages are printed
  - **Alternatives Considered**:
    - Not flushing in handlers - rejected because there may be buffered output from the calculation
  - **Trade-offs**: Adds a small amount of code but ensures correct ordering even if calculation output is still buffered

## Implementation Steps

**Note**: Implementation steps should be organized into phases. Each phase contains multiple tasks with checkboxes to track progress. Each task should be broken down into detailed sub-tasks with individual checkboxes. Phases should be logically grouped and can be completed sequentially or in parallel where appropriate.

**Important**: An implementation plan is considered complete when all AI-actionable tasks are finished. Do NOT include human-only tasks such as:
- Manual testing (beyond what can be automated)
- Code review
- Merging to main
- Release activities

These are post-implementation activities handled by humans. Focus only on tasks the AI can directly execute (code changes, automated test creation, documentation updates, etc.). When all AI-actionable tasks are complete, update the status to "✅ Complete" even if human activities remain.

### Phase 1: Fix Output Buffering in Main Entry Point

**Objective**: Ensure stdout is flushed after version calculation completes and before any error handling occurs in `__main__.py`

- [x] **Task 1**: Add stdout flushing after version calculation
  - [x] Import `sys` module (if not already imported) in `__main__.py`
  - [x] Add `sys.stdout.flush()` immediately after `calculate_pr_version()` completes (after line 68)
  - [x] Add `sys.stdout.flush()` immediately after `calculate_new_version()` completes (after line 79)
  - [x] Ensure flush happens before the try block that calls `update_cargo_version()`
  - **Files**: `.github/scripts/version/src/version/__main__.py`
  - **Dependencies**: None
  - **Testing**: Run version script in PR mode and verify calculation output appears before any errors
  - **Notes**: This ensures all calculation output is visible before update errors occur

- [x] **Task 2**: Add stdout flushing in exception handlers
  - [x] Add `sys.stdout.flush()` at the beginning of the exception handler for `update_cargo_version()` (before line 120)
  - [x] Add `sys.stdout.flush()` at the beginning of the top-level exception handler (before line 153)
  - [x] Ensure flush happens before printing error messages to stderr
  - **Files**: `.github/scripts/version/src/version/__main__.py`
  - **Dependencies**: Task 1
  - **Testing**: Run version script and trigger errors to verify output ordering
  - **Notes**: This ensures any remaining buffered output is flushed before error messages

### Phase 2: Fix Output Buffering in Version Calculation

**Objective**: Ensure calculation summary is flushed before function returns

- [x] **Task 1**: Add stdout flushing after calculation summary
  - [x] Import `sys` module in `version.py` (if not already imported)
  - [x] Add `sys.stdout.flush()` at the end of `calculate_pr_version()` function (after line 390, before return)
  - [x] Add `sys.stdout.flush()` at the end of `calculate_new_version()` function (before return statement)
  - **Files**: `.github/scripts/version/src/version/version.py`
  - **Dependencies**: None
  - **Testing**: Verify calculation summary appears immediately when function completes
  - **Notes**: This ensures the summary is visible even if an exception occurs immediately after the function returns

### Phase 3: Testing and Verification

**Objective**: Verify the fix works correctly and output ordering is correct

- [x] **Task 1**: Test error output ordering
  - [x] Run version script in PR mode with invalid version format to trigger validation error
  - [x] Verify calculation steps appear before error message
  - [x] Verify calculation summary appears before error message
  - [x] Test in release mode to ensure fix doesn't break existing behavior
  - **Files**: `.github/scripts/version/src/version/__main__.py`, `.github/scripts/version/src/version/version.py`
  - **Dependencies**: Phase 1, Phase 2
  - **Testing**: Manual verification of output ordering in GitHub Actions workflow
  - **Notes**: This can be tested by running the script locally or in a test workflow

## Files to Modify/Create
- **Modified Files**:
  - `.github/scripts/version/src/version/__main__.py` - Add stdout flushing after version calculation and in exception handlers
  - `.github/scripts/version/src/version/version.py` - Add stdout flushing after calculation summary

## Testing Strategy
- **Unit Tests**: Not applicable - this is an output ordering fix, not a logic change
- **Integration Tests**: Test by running the version script in PR mode and triggering errors to verify output ordering
- **Manual Testing**: Verify output ordering in GitHub Actions workflow when errors occur

## Breaking Changes
- None - this is a bug fix that only affects output ordering, not functionality

## Migration Guide
- Not applicable - no breaking changes

## Documentation Updates
- [x] No documentation updates needed (internal script behavior change)

## Success Criteria
- Calculation steps and summary appear before error messages in output
- Error messages appear at the end of output, after all calculation context
- Fix works for both PR mode and release mode
- No regression in existing functionality

## Risks and Mitigations
- **Risk**: Flushing stdout may have minor performance impact
  - **Mitigation**: The performance impact is negligible (microseconds) and only occurs at specific points, not in loops
- **Risk**: Fix may not work if Python's buffering behavior changes
  - **Mitigation**: Explicit flushing is the standard approach and is compatible with all Python versions
- **Risk**: May not fix all edge cases if output is buffered elsewhere
  - **Mitigation**: Flushing at key points (after calculation, before errors) covers the main issue; additional flushes can be added if needed

## References
- Related BUG_ document: `plan/25W48/BUG_PR_VERSION_ERROR_ORDERING.md`
- Related bugs: `plan/25W48/BUG_PR_VERSION_VALIDATION_FAILURE.md` (the validation error that exposes this ordering issue)
- Related PRs: #26 (the PR that triggered this bug)
