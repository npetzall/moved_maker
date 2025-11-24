# Implementation Plan: Pull Request Workflow - Sequential Job Execution for Cache Efficiency

**Status**: ✅ Complete

## Overview
Implement sequential job execution in the pull request workflow to improve cache efficiency. Split the matrix-based `test` job into separate `test-ubuntu` and `test-macos` jobs, and add job dependencies so that jobs execute in a sequential order where each job can benefit from cache populated by previous jobs.

## Checklist Summary

### Phase 1: Workflow Restructuring
- [x] 3/3 tasks completed

## Context
Reference to corresponding REQ_ document: `plan/25W48/REQ_PULL_REQUEST_WORKFLOW_SEQUENTIAL_CACHE.md`

**Current State**: All jobs in `.github/workflows/pull_request.yaml` run in parallel with no dependencies. When there's no cache from main, all jobs try to create the cache simultaneously, causing them all to work without cache and making the whole process slow.

**Problem**: Without job dependencies, GitHub Actions runs all jobs in parallel. When multiple jobs use the same `shared-key: "rust-cache"` but start at the same time without an existing cache, all jobs attempt to restore cache simultaneously, none find a cache, all proceed to download dependencies and install tools, and no job benefits from cache created by another job.

## Goals
- Split the matrix-based `test` job into separate `test-ubuntu` and `test-macos` jobs
- Add job dependencies to create execution order: `security` → `test-ubuntu`/`test-macos` → `coverage`/`pre-commit`
- Ensure `test-ubuntu` and `test-macos` can run in parallel after `security` completes
- Ensure `coverage` and `pre-commit` depend only on `test-ubuntu` (not waiting for `test-macos`)
- Update artifact names to use fixed names instead of `${{ matrix.os }}`

## Non-Goals
- Changing the cache key strategy
- Modifying individual job steps (only job structure and dependencies)
- Changing the test execution logic
- Modifying other workflows

## Design Decisions

- **Split matrix job into separate jobs**: Instead of using a matrix strategy for the `test` job, split it into `test-ubuntu` and `test-macos` jobs
  - **Rationale**: This allows more granular control over job dependencies. `coverage` and `pre-commit` can depend only on `test-ubuntu` without waiting for `test-macos`, which is optimal since they only run on ubuntu anyway.
  - **Alternatives Considered**: Keeping the matrix and making all dependent jobs wait for both matrix jobs to complete. This was rejected because it would unnecessarily delay ubuntu-based jobs waiting for macos tests.
  - **Trade-offs**: Slightly more verbose workflow file, but better dependency control and faster feedback for ubuntu-based checks.

- **Sequential execution with parallel where appropriate**: `security` runs first, then `test-ubuntu` and `test-macos` run in parallel, then `coverage` and `pre-commit` run after `test-ubuntu`
  - **Rationale**: This ensures the first job (`security`) builds the cache once, and subsequent jobs can restore from cache immediately. `test-ubuntu` and `test-macos` can still run in parallel after `security` completes, which is optimal.
  - **Alternatives Considered**: Fully sequential execution (all jobs one after another). This was rejected because it would unnecessarily delay macos tests when they could run in parallel with ubuntu tests.
  - **Trade-offs**: Slightly longer total workflow time compared to full parallel execution, but significantly faster when starting without cache due to cache reuse.

## Implementation Steps

### Phase 1: Workflow Restructuring

**Objective**: Restructure the pull request workflow to implement sequential job execution with proper dependencies

- [x] **Task 1**: Split `test` job into `test-ubuntu` and `test-macos` jobs
  - [x] Remove the matrix-based `test` job (lines 48-82)
  - [x] Create `test-ubuntu` job with `needs: security` and `runs-on: ubuntu-latest`
  - [x] Create `test-macos` job with `needs: security` and `runs-on: macos-latest`
  - [x] Copy all steps from the original `test` job to both new jobs
  - [x] Update artifact name in `test-ubuntu` from `test-results-${{ matrix.os }}` to `test-results-ubuntu-latest`
  - [x] Update artifact name in `test-macos` from `test-results-${{ matrix.os }}` to `test-results-macos-latest`
  - **Files**: `.github/workflows/pull_request.yaml`
  - **Dependencies**: None
  - **Testing**: Verify workflow syntax is valid, check that both jobs are defined correctly
  - **Notes**: Both jobs should have identical steps except for the artifact name

- [x] **Task 2**: Add dependency to `coverage` job
  - [x] Add `needs: test-ubuntu` to the `coverage` job (after line 84)
  - **Files**: `.github/workflows/pull_request.yaml`
  - **Dependencies**: Task 1 must be completed
  - **Testing**: Verify workflow syntax is valid, check that `coverage` job has the dependency
  - **Notes**: `coverage` should only wait for `test-ubuntu`, not `test-macos`

- [x] **Task 3**: Add dependency to `pre-commit` job
  - [x] Add `needs: test-ubuntu` to the `pre-commit` job (after line 127)
  - **Files**: `.github/workflows/pull_request.yaml`
  - **Dependencies**: Task 1 must be completed
  - **Testing**: Verify workflow syntax is valid, check that `pre-commit` job has the dependency
  - **Notes**: `pre-commit` should only wait for `test-ubuntu`, not `test-macos`

## Files to Modify/Create
- **Modified Files**:
  - `.github/workflows/pull_request.yaml` - Split `test` job into `test-ubuntu` and `test-macos`, add `needs:` dependencies to `coverage` and `pre-commit` jobs, update artifact names

## Testing Strategy
- **Workflow Syntax Validation**: Verify the YAML syntax is valid using GitHub Actions workflow validation
- **Manual Testing**: Create a test PR to verify the workflow executes in the correct order (informational only, not part of AI tasks)

## Breaking Changes
None - this is an internal workflow optimization that doesn't affect external APIs or user-facing functionality.

## Migration Guide
N/A - no breaking changes

## Documentation Updates
- [x] Update REQ document status when implementation is complete

## Success Criteria
- `test` job is split into `test-ubuntu` and `test-macos` jobs
- `test-ubuntu` has `needs: security` dependency
- `test-macos` has `needs: security` dependency
- `coverage` has `needs: test-ubuntu` dependency
- `pre-commit` has `needs: test-ubuntu` dependency
- Artifact names are updated to use fixed names (`test-results-ubuntu-latest` and `test-results-macos-latest`)
- Workflow YAML syntax is valid
- Execution order matches the expected flow: `security` → `test-ubuntu`/`test-macos` (parallel) → `coverage`/`pre-commit` (after `test-ubuntu`)

## Risks and Mitigations
- **Risk**: Workflow syntax errors could break CI
  - **Mitigation**: Validate YAML syntax carefully, test workflow structure matches expected format
- **Risk**: Job dependencies might cause unexpected delays
  - **Mitigation**: Dependencies are designed to optimize cache usage while maintaining parallel execution where appropriate (`test-ubuntu` and `test-macos` still run in parallel)

## References
- Related REQ_ document: `plan/25W48/REQ_PULL_REQUEST_WORKFLOW_SEQUENTIAL_CACHE.md`
