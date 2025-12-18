# Implementation Plan: Remove unnecessary test steps from build-binaries job

**Status**: ✅ Complete

## Overview
Remove the unnecessary `cargo-nextest` installation and test summary generation steps from the `build-binaries` job in the pull request workflow, since no tests are executed in this job.

## Checklist Summary

### Phase 1: Remove unnecessary steps
- [x] 1/1 tasks completed

## Context
Reference: `plan/25W48/BUG_BUILD_BINARIES_UNNECESSARY_TEST_STEPS.md`

The `build-binaries` job in `.github/workflows/pull_request.yaml` includes two unnecessary steps:
1. Installing `cargo-nextest` (lines 321-322) - not used since no tests are run
2. Generating test summary (lines 324-330) - attempts to process non-existent test results

These steps waste CI time and add unnecessary complexity. Tests are properly executed in the `test-ubuntu` and `test-macos` jobs, which correctly include these steps.

## Goals
- Remove the "Install cargo-nextest" step from the `build-binaries` job
- Remove the "Generate test summary" step from the `build-binaries` job
- Ensure the job only includes steps necessary for building and uploading binaries

## Non-Goals
- Modifying test-related steps in other jobs (they are correct)
- Changing the binary build or upload process
- Adding new functionality

## Design Decisions

**Remove test-related steps from build-binaries job**: Remove both the `cargo-nextest` installation and test summary generation steps.
  - **Rationale**: The `build-binaries` job's purpose is to build and upload binaries, not to run tests. Tests are already properly handled in dedicated `test-ubuntu` and `test-macos` jobs.
  - **Alternatives Considered**:
    - Keeping the steps but making them conditional - rejected because they serve no purpose in this job
    - Moving test execution to build-binaries - rejected because it would duplicate test execution and slow down the workflow
  - **Trade-offs**: None - these steps are purely wasteful and provide no value

## Implementation Steps

### Phase 1: Remove unnecessary steps

**Objective**: Remove the unnecessary test-related steps from the `build-binaries` job

- [x] **Task 1**: Remove unnecessary test steps from build-binaries job
  - [x] Remove the "Install cargo-nextest" step (lines 321-322)
  - [x] Remove the "Generate test summary" step (lines 324-330)
  - **Files**: `.github/workflows/pull_request.yaml`
  - **Dependencies**: None
  - **Testing**: Verify the workflow file is valid YAML and that the job structure is correct
  - **Notes**: The steps to remove are between the "Create checksum" step and the "Upload binary and checksum as artifacts" step

## Files to Modify/Create
- **Modified Files**:
  - `.github/workflows/pull_request.yaml` - Remove lines 321-330 (Install cargo-nextest and Generate test summary steps)

## Testing Strategy
- **Manual Testing**: Verify the workflow YAML syntax is valid (can be done via GitHub Actions UI or yamllint)
- **Verification**: Confirm that the `build-binaries` job now only contains steps for:
  - Checkout code
  - Install Rust
  - Setup cache
  - Build release binary
  - Rename binary with version
  - Install uv
  - Create checksum
  - Upload binary and checksum

## Breaking Changes
None

## Migration Guide
N/A

## Documentation Updates
- [ ] N/A - No documentation changes needed

## Success Criteria
- The `build-binaries` job no longer includes the "Install cargo-nextest" step
- The `build-binaries` job no longer includes the "Generate test summary" step
- The workflow YAML is valid and the job structure is correct
- The job still successfully builds and uploads binaries

## Risks and Mitigations
- **Risk**: Accidentally removing necessary steps
  - **Mitigation**: Carefully review the job structure and ensure only the two identified steps are removed

## References
- Related BUG_ document: `plan/25W48/BUG_BUILD_BINARIES_UNNECESSARY_TEST_STEPS.md`
