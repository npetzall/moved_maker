# Implementation Plan: BUG_GITHUB_WORKFLOWS_RUST_CACHING

**Status**: ✅ Complete

## Overview

This implementation plan addresses the bug described in `plan/25W46/BUG_GITHUB_WORKFLOWS_RUST_CACHING.md`.

## Context

Related bug report: `plan/25W46/BUG_GITHUB_WORKFLOWS_RUST_CACHING.md`

## Detailed Implementation Plan

### Phase 1: Implementation Steps

#### Step 1: Update `.github/workflows/pull_request.yaml`

**File:** `.github/workflows/pull_request.yaml`

1. **Update `security` job (after line 17)**
   - [x] Locate the Rust installation step at line 14-17
   - [x] Add caching step immediately after Rust installation:
     ```yaml
     - uses: Swatinem/rust-cache@v2
     ```
   - [x] Verify step placement (should be after Rust installation, before security tool installation at line 19)
   - [x] Verify YAML indentation matches other steps

2. **Update `test` job (after line 48)**
   - [x] Locate the Rust installation step at line 44-48
   - [x] Add caching step immediately after Rust installation:
     ```yaml
     - uses: Swatinem/rust-cache@v2
       with:
         cache-on-failure: false
     ```
   - [x] Verify step placement (should be after Rust installation, before cargo-nextest installation at line 50)
   - [x] Verify YAML indentation matches other steps
   - [x] Note: Using `cache-on-failure: false` to avoid caching failed test runs

3. **Update `coverage` job (after line 76)**
   - [x] Locate the Rust installation step at line 72-76
   - [x] Add caching step immediately after Rust installation:
     ```yaml
     - uses: Swatinem/rust-cache@v2
       with:
         cache-on-failure: false
     ```
   - [x] Verify step placement (should be after Rust installation, before cargo-nextest installation at line 78)
   - [x] Verify YAML indentation matches other steps
   - [x] Note: Using `cache-on-failure: false` to avoid caching failed coverage runs

4. **Update `pre-commit` job (after line 144)**
   - [x] Locate the Rust installation step at line 140-144
   - [x] Add caching step immediately after Rust installation:
     ```yaml
     - uses: Swatinem/rust-cache@v2
     ```
   - [x] Verify step placement (should be after Rust installation, before cargo-nextest installation at line 149)
   - [x] Verify YAML indentation matches other steps

#### Step 2: Update `.github/workflows/release.yaml`

**File:** `.github/workflows/release.yaml`

1. **Update `security` job (after line 18)**
   - [x] Locate the Rust installation step at line 15-18
   - [x] Add caching step immediately after Rust installation:
     ```yaml
     - uses: Swatinem/rust-cache@v2
     ```
   - [x] Verify step placement (should be after Rust installation, before security tool installation at line 20)
   - [x] Verify YAML indentation matches other steps

2. **Update `build-and-release` job (after line 170)**
   - [x] Locate the Rust installation step at line 166-170
   - [x] Add caching step immediately after Rust installation:
     ```yaml
     - uses: Swatinem/rust-cache@v2
       with:
         cache-targets: true
         cache-on-failure: false
     ```
   - [x] Verify step placement (should be after Rust installation, before cargo-nextest installation at line 172)
   - [x] Verify YAML indentation matches other steps
   - [x] Note: Using `cache-targets: true` for cross-compilation targets, `cache-on-failure: false` to avoid caching failed builds

### Phase 2: Rollback Plan

If issues are encountered:

1. **Immediate Rollback**
   - Revert changes to affected workflow files
   - Remove `Swatinem/rust-cache@v2` steps from all jobs
   - Verify workflows return to working state
   - Investigate cache-related issues before retrying

2. **Partial Rollback**
   - If only specific jobs fail, remove caching from those jobs only
   - Investigate why specific jobs fail with caching
   - Consider job-specific cache configuration adjustments
   - Common issues:
     - Cache key conflicts
     - Cache size limits
     - Cache corruption

3. **Alternative Approach**
   - If `Swatinem/rust-cache@v2` causes issues, consider:
     - Using `actions/cache@v4` with manual cache configuration
     - Adjusting cache configuration parameters (e.g., `cache-on-failure`, `cache-targets`)
     - Using different cache keys per job with `prefix-key`
     - Disabling `cache-bin` if binary caching causes issues

### Implementation Order

1. **Start with `.github/workflows/pull_request.yaml`** (lower risk, easier to test)
   - Start with `test` job (most frequently run, easiest to verify)
   - Then `coverage` job
   - Then `security` job
   - Finally `pre-commit` job
   - Test each job via pull request before moving to next

2. **Test via pull request**
   - Create a test PR to verify all pull_request.yaml jobs work
   - Monitor cache hit rates and build times
   - Verify no regressions

3. **Update `.github/workflows/release.yaml`**
   - Once pull_request.yaml is verified, update release.yaml
   - Start with `security` job
   - Then `build-and-release` job (most complex due to cross-compilation)

4. **Final verification**
   - Test release workflow (can be done via test branch or after merge)
   - Verify all matrix targets in build-and-release job cache correctly
   - Monitor overall cache usage and performance

### Risk Assessment

- **Risk Level:** Low
- **Impact if Failed:**
  - Workflows might fail if cache action has issues (unlikely, well-maintained action)
  - Cache might not work as expected, but workflows should still function (caching is additive)
  - Potential cache size issues if multiple targets create large caches
- **Mitigation:**
  - Easy rollback (just remove cache steps)
  - Well-tested action with millions of downloads
  - Caching is non-blocking - if cache fails, workflow continues
  - Can test incrementally via pull requests
- **Testing:**
  - Can be fully tested via pull request before affecting main branch
  - Each job can be tested independently
  - Cache behavior can be verified through workflow logs
- **Dependencies:**
  - `Swatinem/rust-cache@v2` action must be available
  - GitHub Actions cache service must be available (standard service)
  - Sufficient cache quota (10 GB per repository limit)

### Expected Outcomes

After successful implementation:

- **Build Time Reduction:** 50-80% faster builds on cache hits
- **Network Traffic Reduction:** Dependencies and binaries cached, reducing downloads
- **CI Cost Reduction:** Faster builds = fewer CI minutes consumed
- **Improved Developer Experience:** Faster feedback loops on pull requests
- **Cross-Compilation Speedup:** Significant improvement for build-and-release job with multiple targets

## Status

✅ **FIXED** - Rust/Cargo caching implemented in all workflows using `Swatinem/rust-cache@v2`
