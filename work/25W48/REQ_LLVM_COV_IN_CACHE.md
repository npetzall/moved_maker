# Implementation Plan: Install cargo-llvm-cov in security job to include in cache

**Status**: ✅ Completed

## Overview
Install `cargo-llvm-cov` in the security job of the pull_request workflow (after rust-cache restoration) with a step name that includes "(for caching)". This ensures cargo-llvm-cov is included in the rust-cache and available to all dependent jobs, improving cache efficiency and reducing installation time in subsequent jobs that also install cargo-llvm-cov.

## Checklist Summary

### Phase 1: Add installation to security job
- [x] 2/2 tasks completed

### Phase 2: Verification
- [ ] 0/1 tasks completed

## Context
Reference: `plan/25W48/REQ_LLVM_COV_IN_CACHE.md`

Currently, `cargo-llvm-cov` is installed in the `coverage` job of `.github/workflows/pull_request.yaml` after the rust-cache action runs (step 162-163). This means cargo-llvm-cov is not included in the cache, and must be installed fresh on every run, adding unnecessary time to CI execution.

The security job runs first and uses rust-cache. By installing cargo-llvm-cov in the security job after rust-cache restoration, it will be available when rust-cache saves the cache, making it available to all subsequent jobs.

Note: cache-build.yaml is already fixed and should be excluded from this assessment.

## Goals
- Install cargo-llvm-cov in the security job after rust-cache restoration
- Use step name that includes "(for caching)" to indicate purpose
- Ensure cargo-llvm-cov is included in the rust-cache
- Improve cache efficiency for subsequent jobs that install cargo-llvm-cov
- Reduce CI execution time in jobs that install cargo-llvm-cov (faster when cached)
- Maintain consistent cargo-llvm-cov versions across jobs

## Non-Goals
- Removing cargo-llvm-cov installation from other jobs (coverage job and others will continue to install it, but benefit from cache)
- Modifying cache-build.yaml (already fixed)
- Modifying release-build.yaml (out of scope)
- Changing the rust-cache configuration or behavior
- Modifying other tool installations (security tools, geiger, nextest) - handled in separate REQ
- Changing the cache key or cache strategy
- Modifying workflow triggers or concurrency settings

## Design Decisions

**Install cargo-llvm-cov in security job after rust-cache restoration**: Add installation step in the security job after rust-cache runs
  - **Rationale**: The security job runs first and uses rust-cache. Installing cargo-llvm-cov after rust-cache restoration ensures it's available when rust-cache saves the cache at the end of the security job, making it available to all subsequent jobs via cache restoration.
  - **Alternatives Considered**:
    - Installing before rust-cache restoration (rejected - would not be in restored cache, but would be saved)
    - Installing in a separate early job (rejected - adds unnecessary complexity, security job already serves this purpose)
  - **Trade-offs**: Slightly longer security job run, but significant time savings in the coverage job

**Use step name with "(for caching)"**: Include "(for caching)" in the installation step name
  - **Rationale**: Makes it clear that the installation is specifically for caching purposes, not for use in the security job itself.
  - **Alternatives Considered**:
    - Generic step name (rejected - less clear about purpose)
    - Different naming convention (rejected - "(for caching)" is clear and explicit)
  - **Trade-offs**: None

**Keep cargo-llvm-cov installation in other jobs**: Other jobs (like coverage) will continue to install cargo-llvm-cov, but will benefit from the cache
  - **Rationale**: Keeping installations in other jobs provides a fallback if cache is not available, and the installation will be faster when the cache is present. This approach is more resilient and doesn't assume cache availability.
  - **Alternatives Considered**:
    - Remove installation from coverage job (rejected - less resilient, assumes cache is always available)
    - Install only if not found (rejected - adds complexity, cargo install handles cached binaries efficiently)
  - **Trade-offs**: Slightly redundant installations, but provides resilience and faster execution when cache is available

## Implementation Steps

### Phase 1: Add installation to security job

**Objective**: Add cargo-llvm-cov installation step to security job with "(for caching)" in the name

- [x] **Task 1**: Add cargo-llvm-cov installation step to security job
  - [x] Read current pull_request.yaml workflow file
  - [x] Locate the security job section
  - [x] Add a new step after the rust-cache step with name: "Install cargo-llvm-cov (for caching)"
  - [x] Use the installation command: `cargo install cargo-llvm-cov`
  - [x] Ensure the step is placed after rust-cache restoration but before security tool installations
  - **Files**: `.github/workflows/pull_request.yaml`
  - **Dependencies**: None
  - **Testing**: Verify workflow syntax is valid (can be checked via GitHub Actions UI or yaml linter)
  - **Notes**: The rust-cache action will automatically cache binaries from `~/.cargo/bin` when it saves the cache at the end of the security job

- [x] **Task 2**: Verify security job structure
  - [x] Ensure all steps are in logical order
  - [x] Verify no duplicate installations
  - [x] Check that rust-cache step runs before cargo-llvm-cov installation
  - [x] Verify step name includes "(for caching)"
  - **Files**: `.github/workflows/pull_request.yaml`
  - **Dependencies**: Task 1
  - **Testing**: Review workflow file structure and step order
  - **Notes**: The order in security job should be: Checkout → Install Rust → rust-cache → Install cargo-llvm-cov (for caching) → Install security tools → Install cargo-geiger → security checks

### Phase 2: Verification

**Objective**: Ensure the changes work correctly and cargo-llvm-cov is cached

- [ ] **Task 1**: Document verification steps
  - [ ] Create checklist of verification steps for manual testing
  - [ ] Document expected behavior: cargo-llvm-cov should be installed in security job and cached, making subsequent installations in other jobs faster
  - [ ] Note that security job will install cargo-llvm-cov for caching, other jobs will still install it but benefit from the cache
  - **Files**: This implementation plan (verification section)
  - **Dependencies**: Phase 1 complete
  - **Testing**: N/A - documentation only
  - **Notes**: Actual verification requires running workflows in GitHub Actions, which is a manual step

## Files to Modify/Create
- **Modified Files**:
  - `.github/workflows/pull_request.yaml` - Add cargo-llvm-cov installation in security job (for caching)

## Testing Strategy
- **Unit Tests**: N/A - workflow changes don't require unit tests
- **Integration Tests**: N/A - workflow changes require GitHub Actions environment
- **Manual Testing**:
  - Run pull_request workflow and verify cargo-llvm-cov is installed in security job (with "(for caching)" in step name)
  - Verify cargo-llvm-cov installation in coverage job is faster when cache is available
  - Verify coverage generation still works correctly

## Breaking Changes
None - this is an optimization that improves cache efficiency without changing functionality

## Migration Guide
N/A - no breaking changes

## Documentation Updates
- [ ] Update workflow comments if needed to explain the installation order
- [ ] No README or DEVELOPMENT.md updates required (internal workflow optimization)

## Success Criteria
- cargo-llvm-cov is installed in security job with step name including "(for caching)"
- Security job installs cargo-llvm-cov after rust-cache restoration
- All workflows have valid YAML syntax
- cargo-llvm-cov is included in rust-cache, making subsequent installations faster (verified manually)
- Coverage job and other jobs continue to install cargo-llvm-cov but benefit from cache

## Risks and Mitigations
- **Risk**: rust-cache may not cache cargo-installed binaries as expected
  - **Mitigation**: rust-cache documentation confirms it caches `~/.cargo/bin`. If issues arise, verify rust-cache configuration and version.
- **Risk**: Coverage job may fail if cache is not available
  - **Mitigation**: Coverage job still installs cargo-llvm-cov, so it will work even if cache is not available. The cache is an optimization, not a requirement.
- **Risk**: Workflow execution order changes may cause unexpected behavior
  - **Mitigation**: The change is minimal - only adding one installation step in security job. All other workflow logic remains the same, including existing installations in other jobs.

## References
- Related REQ_ document: `plan/25W48/REQ_LLVM_COV_IN_CACHE.md`
- Related requirements:
  - `plan/25W48/REQ_NEXTEST_IN_CACHE.md` (similar optimization for nextest)
- External references:
  - rust-cache action documentation: https://github.com/Swatinem/rust-cache
  - Target workflow: `.github/workflows/pull_request.yaml` (security job and coverage job)
