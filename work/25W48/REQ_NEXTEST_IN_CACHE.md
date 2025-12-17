# Implementation Plan: Install nextest in security job to include in cache

**Status**: ✅ Done

## Overview
Install `cargo-nextest` in the security job of the pull_request workflow (after rust-cache restoration) with a step name that includes "(for caching)". This ensures cargo-nextest is included in the rust-cache and available to all dependent jobs. Existing installations in dependent jobs (test-ubuntu, test-macos, coverage, build-binaries, pre-commit) are kept as fallbacks to ensure cargo-nextest is installed if cache issues occur.

## Checklist Summary

### Phase 1: Add installation to security job
- [x] 2/2 tasks completed

### Phase 2: Verification
- [x] 1/1 tasks completed

## Context
Reference: `plan/25W48/REQ_NEXTEST_IN_CACHE.md`

Currently, `cargo-nextest` is installed in multiple jobs of `.github/workflows/pull_request.yaml` after the rust-cache action runs:
- `test-ubuntu` job (step 67-68)
- `test-macos` job (step 113-114)
- `coverage` job (step 159-160)
- `build-binaries` job (step 302-303)
- `pre-commit` job (step 349, combined with other tools)

This means cargo-nextest is not included in the cache, and must be installed fresh in each job, adding unnecessary time to CI execution.

The security job runs first and uses rust-cache. By installing cargo-nextest in the security job after rust-cache restoration, it will be available when rust-cache saves the cache, making it available to all subsequent jobs. Existing installations in dependent jobs are kept as fallbacks to ensure cargo-nextest is installed if cache issues occur.

Note: cache-build.yaml is already fixed and should be excluded from this assessment.

## Goals
- Install cargo-nextest in the security job after rust-cache restoration
- Use step name that includes "(for caching)" to indicate purpose
- Ensure cargo-nextest is included in the rust-cache
- Keep existing cargo-nextest installations in dependent jobs as fallbacks
- Reduce CI execution time across multiple jobs when cache is available
- Maintain consistent cargo-nextest versions across jobs

## Non-Goals
- Modifying cache-build.yaml (already fixed)
- Modifying release-build.yaml (out of scope)
- Changing the rust-cache configuration or behavior
- Modifying other tool installations (security tools, geiger, llvm-cov) - handled in separate REQ
- Changing the cache key or cache strategy
- Modifying workflow triggers or concurrency settings

## Design Decisions

**Install cargo-nextest in security job after rust-cache restoration**: Add installation step in the security job after rust-cache runs
  - **Rationale**: The security job runs first and uses rust-cache. Installing cargo-nextest after rust-cache restoration ensures it's available when rust-cache saves the cache at the end of the security job, making it available to all subsequent jobs via cache restoration.
  - **Alternatives Considered**:
    - Installing before rust-cache restoration (rejected - would not be in restored cache, but would be saved)
    - Installing in a separate early job (rejected - adds unnecessary complexity, security job already serves this purpose)
  - **Trade-offs**: Slightly longer security job run, but significant time savings across multiple jobs

**Use step name with "(for caching)"**: Include "(for caching)" in the installation step name
  - **Rationale**: Makes it clear that the installation is specifically for caching purposes, not for use in the security job itself.
  - **Alternatives Considered**:
    - Generic step name (rejected - less clear about purpose)
    - Different naming convention (rejected - "(for caching)" is clear and explicit)
  - **Trade-offs**: None

**Keep existing cargo-nextest installations in dependent jobs**: Maintain installation steps in test-ubuntu, test-macos, coverage, build-binaries, and pre-commit jobs
  - **Rationale**: While cargo-nextest will be cached in the security job and available via rust-cache restoration, keeping existing installations ensures cargo-nextest is available even if cache issues occur. This provides a safety net and ensures CI reliability.
  - **Alternatives Considered**:
    - Remove installations (rejected - could cause failures if cache is unavailable)
    - Install only if not found (rejected - adds complexity, existing approach is simpler)
  - **Trade-offs**: Slightly longer execution time in dependent jobs, but improved reliability and safety

## Implementation Steps

### Phase 1: Add installation to security job

**Objective**: Add cargo-nextest installation step to security job with "(for caching)" in the name

- [x] **Task 1**: Add cargo-nextest installation step to security job
  - [x] Read current pull_request.yaml workflow file
  - [x] Locate the security job section
  - [x] Add a new step after the rust-cache step with name: "Install cargo-nextest (for caching)"
  - [x] Use the installation command: `cargo install cargo-nextest`
  - [x] Ensure the step is placed after rust-cache restoration but before security tool installations
  - **Files**: `.github/workflows/pull_request.yaml`
  - **Dependencies**: None
  - **Testing**: Verify workflow syntax is valid (can be checked via GitHub Actions UI or yaml linter)
  - **Notes**: The rust-cache action will automatically cache binaries from `~/.cargo/bin` when it saves the cache at the end of the security job

- [x] **Task 2**: Verify security job structure
  - [x] Ensure all steps are in logical order
  - [x] Verify no duplicate installations
  - [x] Check that rust-cache step runs before cargo-nextest installation
  - [x] Verify step name includes "(for caching)"
  - **Files**: `.github/workflows/pull_request.yaml`
  - **Dependencies**: Task 1
  - **Testing**: Review workflow file structure and step order
  - **Notes**: The order in security job should be: Checkout → Install Rust → rust-cache → Install cargo-llvm-cov (for caching) → Install cargo-nextest (for caching) → Install security tools → Install cargo-geiger → security checks

### Phase 2: Verification

**Objective**: Ensure the changes work correctly and cargo-nextest is cached

- [x] **Task 1**: Document verification steps
  - [x] Create checklist of verification steps for manual testing
  - [x] Document expected behavior: cargo-nextest should be installed in security job and available in all dependent jobs from cache
  - [x] Note that security job will install cargo-nextest, all dependent jobs should use cached version when available, or fallback to installation if cache misses
  - **Files**: This implementation plan (verification section)
  - **Dependencies**: Phases 1 and 2 complete
  - **Testing**: N/A - documentation only
  - **Notes**: Actual verification requires running workflows in GitHub Actions, which is a manual step

## Files to Modify/Create
- **Modified Files**:
  - `.github/workflows/pull_request.yaml` - Add cargo-nextest installation in security job (keep existing installations in dependent jobs as fallbacks)

## Testing Strategy
- **Unit Tests**: N/A - workflow changes don't require unit tests
- **Integration Tests**: N/A - workflow changes require GitHub Actions environment
- **Manual Testing**:
  - Run pull_request workflow and verify cargo-nextest is installed in security job (with "(for caching)" in step name)
  - Verify cargo-nextest is available in test-ubuntu job (from cache when available, or from installation if cache misses)
  - Verify cargo-nextest is available in test-macos job (from cache when available, or from installation if cache misses)
  - Verify cargo-nextest is available in coverage job (from cache when available, or from installation if cache misses)
  - Verify cargo-nextest is available in build-binaries job (from cache when available, or from installation if cache misses)
  - Verify cargo-nextest is available in pre-commit job (from cache when available, or from combined installation if cache misses)
  - Verify all jobs that use cargo-nextest still work correctly

## Breaking Changes
None - this is an optimization that improves cache efficiency without changing functionality

## Migration Guide
N/A - no breaking changes

## Documentation Updates
- [x] Update workflow comments if needed to explain the installation order
- [x] No README or DEVELOPMENT.md updates required (internal workflow optimization)

## Success Criteria
- cargo-nextest is installed in security job with step name including "(for caching)"
- Existing cargo-nextest installation steps remain in test-ubuntu, test-macos, coverage, build-binaries, and pre-commit jobs as fallbacks
- All workflows have valid YAML syntax
- All jobs that use cargo-nextest can access it from cache when available (verified manually)
- All jobs that use cargo-nextest can still install it if cache is unavailable (fallback behavior)
- Security job installs cargo-nextest after rust-cache restoration

## Risks and Mitigations
- **Risk**: rust-cache may not cache cargo-installed binaries as expected
  - **Mitigation**: rust-cache documentation confirms it caches `~/.cargo/bin`. If issues arise, verify rust-cache configuration and version.
- **Risk**: Dependent jobs may fail if cache is not available
  - **Mitigation**: Existing installations in dependent jobs are kept as fallbacks, ensuring cargo-nextest is available even if cache is unavailable. This provides redundancy and improves reliability.
- **Risk**: Workflow execution order changes may cause unexpected behavior
  - **Mitigation**: The change is minimal - only adding one installation step in security job. All other workflow logic remains the same, including existing installations in dependent jobs.

## References
- Related REQ_ document: `plan/25W48/REQ_NEXTEST_IN_CACHE.md`
- Related requirements:
  - `plan/25W48/REQ_LLVM_COV_IN_CACHE.md` (similar optimization for llvm-cov)
- External references:
  - rust-cache action documentation: https://github.com/Swatinem/rust-cache
  - Target workflow: `.github/workflows/pull_request.yaml` (security job and all dependent jobs)
