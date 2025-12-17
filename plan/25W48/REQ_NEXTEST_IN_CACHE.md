# REQ: Install nextest in security job to include in cache

**Status**: ✅ Done

## Overview
Install cargo-nextest in the security job of the pull_request workflow so that it's included in the rust-cache, improving cache efficiency and reducing installation time in dependent jobs within the same workflow.

## Motivation
Currently, `cargo-nextest` is installed in multiple jobs of the `pull_request.yaml` workflow (test-ubuntu, test-macos, coverage, build-binaries, pre-commit) after `rust-cache` runs. This means nextest is not included in the cache, and must be installed fresh in each job, adding unnecessary time to CI execution.

By installing cargo-nextest in the security job (which runs first and uses rust-cache), we can:
- Include cargo-nextest in the rust-cache
- Reduce installation time in all dependent jobs
- Improve overall CI efficiency
- Ensure consistent cargo-nextest versions across jobs

## Current Behavior
In `.github/workflows/pull_request.yaml`:
- The `security` job runs first and uses rust-cache, but does not install cargo-nextest
- Multiple jobs install cargo-nextest after rust-cache runs:
  - `test-ubuntu` job (step 67-68)
  - `test-macos` job (step 113-114)
  - `coverage` job (step 159-160)
  - `build-binaries` job (step 302-303)
  - `pre-commit` job (step 349, combined with other tools)

The rust-cache action in each job runs before cargo-nextest is installed, so cargo-nextest is not included in the cache for subsequent jobs.

## Proposed Behavior
Install `cargo-nextest` in the `security` job (after rust-cache restoration) with a step name that includes "(for caching)" to indicate its purpose. This ensures:
- cargo-nextest is available when rust-cache saves the cache in the security job
- All dependent jobs (test-ubuntu, test-macos, coverage, build-binaries, pre-commit) can use cargo-nextest from the cache when available
- Existing installation steps in dependent jobs are kept as fallbacks to ensure cargo-nextest is installed if cache issues occur

## Use Cases
- Security job runs first, installs cargo-nextest for caching, making it available to all subsequent jobs
- Test jobs (test-ubuntu, test-macos) benefit from cached cargo-nextest, reducing test execution time
- Coverage job benefits from cached cargo-nextest, reducing coverage report generation time
- Build-binaries and pre-commit jobs benefit from cached cargo-nextest
- All jobs using cargo-nextest get consistent, cached versions

## Implementation Considerations
- Need to understand how rust-cache handles cargo-installed binaries (typically in `~/.cargo/bin`)
- Install cargo-nextest in the security job after rust-cache restoration so it's available when rust-cache saves the cache
- Should verify that rust-cache actually caches cargo-installed binaries
- Step name should include "(for caching)" to clearly indicate the purpose
- Keep existing cargo-nextest installations in test-ubuntu, test-macos, coverage, build-binaries, and pre-commit jobs as fallbacks
- Note: cache-build.yaml is already fixed and should be excluded from this assessment

## Alternatives Considered
- **Current approach**: Install cargo-nextest in each job after rust-cache (rejected - not cached, inefficient)
- **Install in security job**: Install cargo-nextest in security job after rust-cache restoration (✅ **PREFERRED** - ensures it's available when cache is saved)
- **Separate cache for binaries**: Use a separate caching mechanism for cargo-installed binaries (rejected - adds complexity)
- **Install in all jobs**: Keep current approach but accept the overhead (rejected - inefficient)

## Impact
- **Breaking Changes**: No - this is an optimization that improves cache efficiency
- **Documentation**: May need to document the cache strategy and tool installation order
- **Testing**: Need to verify that nextest is actually cached and available in dependent workflows
- **Dependencies**: No new dependencies required

## References
- Related issues: N/A
- Related PRs: N/A
- Related requirements:
  - REQ_LLVM_COV_IN_CACHE.md (similar request for llvm-cov)
- External references:
  - rust-cache action documentation: https://github.com/Swatinem/rust-cache
  - Target workflow: `.github/workflows/pull_request.yaml` (security job and all dependent jobs)
