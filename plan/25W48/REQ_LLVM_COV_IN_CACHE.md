# REQ: Install cargo-llvm-cov in security job to include in cache

**Status**: ✅ Completed

## Overview
Install cargo-llvm-cov in the security job of the pull_request workflow so that it's included in the rust-cache, improving cache efficiency and reducing installation time in dependent jobs within the same workflow.

## Motivation
Currently, `cargo-llvm-cov` is installed in the `coverage` job of the `pull_request.yaml` workflow after `rust-cache` runs. This means cargo-llvm-cov is not included in the cache, and must be installed fresh on every run, adding unnecessary time to CI execution.

By installing cargo-llvm-cov in the security job (which runs first and uses rust-cache), we can:
- Include cargo-llvm-cov in the rust-cache
- Reduce installation time in the coverage job
- Improve overall CI efficiency
- Ensure consistent cargo-llvm-cov versions across jobs

## Current Behavior
In `.github/workflows/pull_request.yaml`:
- The `security` job runs first and uses rust-cache, but does not install cargo-llvm-cov
- The `coverage` job installs cargo-llvm-cov (step 162-163) after rust-cache runs
- Other jobs that may need cargo-llvm-cov must install it separately

The rust-cache action in the coverage job runs before cargo-llvm-cov is installed, so cargo-llvm-cov is not included in the cache for subsequent jobs.

## Proposed Behavior
Install `cargo-llvm-cov` in the `security` job (after rust-cache restoration) with a step name that includes "(for caching)" to indicate its purpose. This ensures:
- cargo-llvm-cov is available when rust-cache saves the cache in the security job
- The coverage job (and any other jobs) that install cargo-llvm-cov will benefit from the cache, making installations faster
- Other jobs continue to install cargo-llvm-cov as before, but with improved cache efficiency

## Use Cases
- Security job runs first, installs cargo-llvm-cov for caching, making it available in the cache for all subsequent jobs
- Coverage job benefits from cached cargo-llvm-cov, making its installation faster when cache is available
- All jobs using cargo-llvm-cov get consistent, cached versions, improving overall CI efficiency

## Implementation Considerations
- Need to understand how rust-cache handles cargo-installed binaries (typically in `~/.cargo/bin`)
- Install cargo-llvm-cov in the security job after rust-cache restoration so it's available when rust-cache saves the cache
- Should verify that rust-cache actually caches cargo-installed binaries
- Step name should include "(for caching)" to clearly indicate the purpose
- Other jobs (like coverage) will continue to install cargo-llvm-cov, but will benefit from the cache
- cargo-llvm-cov is used for code coverage reporting, so caching it will improve coverage job performance
- Note: cache-build.yaml is already fixed and should be excluded from this assessment

## Alternatives Considered
- **Current approach**: Install cargo-llvm-cov in coverage job after rust-cache (rejected - not cached)
- **Install in security job**: Install cargo-llvm-cov in security job after rust-cache restoration (✅ **PREFERRED** - ensures it's available when cache is saved, other jobs benefit from cache)
- **Remove from other jobs**: Install only in security job and remove from other jobs (rejected - less resilient, assumes cache is always available)
- **Separate cache for binaries**: Use a separate caching mechanism for cargo-installed binaries (rejected - adds complexity)
- **Install in all jobs**: Keep current approach but accept the overhead (rejected - inefficient)

## Impact
- **Breaking Changes**: No - this is an optimization that improves cache efficiency
- **Documentation**: May need to document the cache strategy and tool installation order
- **Testing**: Need to verify that cargo-llvm-cov is actually cached and available in dependent workflows
- **Dependencies**: No new dependencies required

## References
- Related issues: N/A
- Related PRs: N/A
- Related requirements:
  - REQ_NEXTEST_IN_CACHE.md (similar request for nextest)
- External references:
  - rust-cache action documentation: https://github.com/Swatinem/rust-cache
  - Target workflow: `.github/workflows/pull_request.yaml` (security job and coverage job)
