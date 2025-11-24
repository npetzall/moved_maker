# Implementation Plan: Fix Test Reports Not Uploaded

**Status**: ✅ Complete

## Overview

Fix the incorrect JUnit XML output path in `.config/nextest.toml` that prevents test reports from being uploaded as artifacts in GitHub Actions workflows. The path contains a literal `{target}` prefix that causes nextest to generate files with the wrong name, which doesn't match the workflow's expected pattern.

## Checklist Summary

### Phase 1: Configuration Fix
- [x] 1/1 tasks completed

## Context

**Related Bug Document**: `plan/25W48/BUG_TEST_REPORTS_NOT_UPLOADED.md`

**Current State**: The `.config/nextest.toml` file has an incorrect JUnit path configuration:
```toml
[profile.default.junit]
path = "{target}-test-results.xml"
```

The `{target}` prefix is literal text (not a variable), causing nextest to generate files with names like `{target}-test-results.xml` instead of the expected `test-results.xml` in the `target/nextest/default/` directory.

**Workflow Expectation**: The GitHub Actions workflow (`.github/workflows/pull_request.yaml`) expects test results at `target/nextest/**/test-results.xml`.

**Previous Related Fix**: A previous bug (`plan/25W46/BUG_WORKFLOWS_TEST_REPORT_PATH.md`) showed that when the path is set to `test-results.xml` (relative), nextest automatically places it in `target/nextest/default/test-results.xml`, which matches the workflow's wildcard pattern.

## Goals

- Fix the JUnit XML output path in `.config/nextest.toml` to generate test results at the correct location
- Ensure test results are uploaded as artifacts in GitHub Actions workflows
- Restore visibility of test results for debugging purposes

## Non-Goals

- Changing the workflow configuration (it's already correct)
- Modifying nextest behavior beyond configuration
- Adding new features or enhancements

## Design Decisions

- **Use relative path `test-results.xml`**: Based on previous bug fixes and nextest behavior, using a relative path like `test-results.xml` causes nextest to automatically place the file in `target/nextest/default/test-results.xml`, which matches the workflow's expected pattern `target/nextest/**/test-results.xml`.
  - **Rationale**: This is the simplest fix and aligns with how nextest handles relative paths. The workflow already uses a wildcard pattern that will find the file in any subdirectory under `target/nextest/`.
  - **Alternatives Considered**:
    - Using an absolute path like `target/nextest/test-results.xml`: This might work but is less flexible and doesn't match nextest's default behavior of creating profile-specific subdirectories.
    - Changing the workflow pattern: This was rejected because the workflow pattern is already correct and flexible.
  - **Trade-offs**: None - this is a straightforward configuration fix.

## Implementation Steps

### Phase 1: Configuration Fix

**Objective**: Fix the JUnit XML output path in `.config/nextest.toml` to match the workflow's expected pattern.

- [x] **Task 1**: Fix the JUnit path configuration
  - [x] Remove the incorrect `{target}` prefix from the path
  - [x] Set the path to `test-results.xml` (relative path)
  - **Files**: `.config/nextest.toml`
  - **Dependencies**: None
  - **Testing**: Verify the configuration change is correct
  - **Notes**: Based on previous bug fixes, a relative path of `test-results.xml` will cause nextest to place the file in `target/nextest/default/test-results.xml`, which matches the workflow pattern.

## Files to Modify/Create

- **Modified Files**:
  - `.config/nextest.toml` - Fix the `path` in `[profile.default.junit]` section by removing the incorrect `{target}` prefix

## Testing Strategy

- **Configuration Verification**: Verify that the path is correctly set to `test-results.xml`
- **Local Testing**: Run `cargo nextest run` locally to verify the test results file is generated at the expected location (should be `target/nextest/default/test-results.xml`)
- **Workflow Testing**: The fix will be verified when the workflow runs in CI/CD, where it should successfully upload test results as artifacts

## Breaking Changes

None - this is a bug fix that restores expected behavior.

## Migration Guide

N/A - no breaking changes.

## Documentation Updates

- [ ] Update bug document status to reflect completion

## Success Criteria

- The `.config/nextest.toml` file has the correct JUnit path configuration (`path = "test-results.xml"`)
- Test results are generated at a location that matches the workflow's expected pattern (`target/nextest/**/test-results.xml`)
- GitHub Actions workflow successfully uploads test results as artifacts
- Test result artifacts are visible in workflow runs

## Risks and Mitigations

- **Risk**: The path might still not match if nextest behavior has changed
  - **Mitigation**: Based on previous bug fixes, the relative path approach has been verified to work. If issues persist, we can investigate nextest's current behavior and adjust accordingly.

## References

- Related BUG_ document: `plan/25W48/BUG_TEST_REPORTS_NOT_UPLOADED.md`
- Related previous bug: `plan/25W46/BUG_WORKFLOWS_TEST_REPORT_PATH.md` (shows correct configuration)
- Related previous bug: `plan/25W46/BUG_NEXTEST_JUNIT_XML_FLAG.md` (shows nextest configuration approach)
