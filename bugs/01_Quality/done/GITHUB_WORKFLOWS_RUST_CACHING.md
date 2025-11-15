# Bug: GitHub Actions workflows missing Rust/Cargo caching

## Description

No Rust/Cargo caching is implemented in any workflow, leading to slower CI runs, unnecessary network traffic, higher CI costs, and slower feedback loops.

## Current State

✅ **FIXED** - Rust/Cargo caching is now implemented in all workflows using `Swatinem/rust-cache@v2`.

Previously, no Rust/Cargo caching was implemented in any workflow, which caused:
- Slower CI runs
- Unnecessary network traffic
- Higher CI costs
- Slower feedback loops

## Expected State

Add caching after Rust installation using `Swatinem/rust-cache@v2`:

```yaml
- name: Install Rust
  uses: dtolnay/rust-toolchain@stable
  with:
    toolchain: 1.90.0
    components: clippy rustfmt

- uses: Swatinem/rust-cache@v2
```

**Reference:** https://github.com/Swatinem/rust-cache

## Impact

### Performance Impact
- **Severity**: Medium
- **Priority**: Medium

Without caching:
- CI runs are significantly slower
- Dependencies are downloaded and compiled on every run
- Increased CI minutes consumption

## Steps to Fix

Add caching step after Rust installation in all jobs that build/test:

```yaml
- name: Install Rust
  uses: dtolnay/rust-toolchain@stable
  with:
    toolchain: 1.90.0
    components: clippy rustfmt

- uses: Swatinem/rust-cache@v2
```

**Note:** The cache action should be placed after Rust installation but before any cargo commands.

## Affected Files

- `.github/workflows/pull_request.yaml`
  - `security` job (after line 17)
  - `test` job (after line 48)
  - `coverage` job (after line 76)
  - `pre-commit` job (after line 144)

- `.github/workflows/release.yaml`
  - `security` job (after line 18)
  - `build-and-release` job (after line 170)

## Example Fix

### Before (test job):
```yaml
- name: Install Rust
  uses: dtolnay/rust-toolchain@stable
  with:
    toolchain: 1.90.0
    components: clippy rustfmt

- name: Install cargo-nextest
  run: cargo install cargo-nextest
```

### After (test job):
```yaml
- name: Install Rust
  uses: dtolnay/rust-toolchain@stable
  with:
    toolchain: 1.90.0
    components: clippy rustfmt

- uses: Swatinem/rust-cache@v2

- name: Install cargo-nextest
  run: cargo install cargo-nextest
```

### Before (security job):
```yaml
- name: Install Rust
  uses: dtolnay/rust-toolchain@stable
  with:
    toolchain: 1.90.0

- name: Install security tools
  run: cargo install cargo-deny cargo-audit cargo-geiger cargo-auditable
```

### After (security job):
```yaml
- name: Install Rust
  uses: dtolnay/rust-toolchain@stable
  with:
    toolchain: 1.90.0

- uses: Swatinem/rust-cache@v2

- name: Install security tools
  run: cargo install cargo-deny cargo-audit cargo-geiger cargo-auditable
```

### Before (build-and-release job):
```yaml
- name: Install Rust
  uses: dtolnay/rust-toolchain@stable
  with:
    toolchain: 1.90.0
    targets: ${{ matrix.target }}

- name: Install cargo-nextest
  run: cargo install cargo-nextest
```

### After (build-and-release job):
```yaml
- name: Install Rust
  uses: dtolnay/rust-toolchain@stable
  with:
    toolchain: 1.90.0
    targets: ${{ matrix.target }}

- uses: Swatinem/rust-cache@v2

- name: Install cargo-nextest
  run: cargo install cargo-nextest
```

## References

- [rust-cache GitHub Action](https://github.com/Swatinem/rust-cache)

## Investigation

### rust-cache Action Overview

The `Swatinem/rust-cache@v2` action provides intelligent caching for Rust projects with sensible defaults. It automatically:
- Caches `~/.cargo/registry` (downloaded crates)
- Caches `~/.cargo/git` (git dependencies)
- Caches `target` directory (build artifacts)
- Generates cache keys based on Rust version, OS, and `Cargo.lock` hash

### Configuration Options

The action supports several optional parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prefix-key` | string | `""` | Custom prefix for cache keys (useful for separating caches by job type) |
| `cache-targets` | boolean | `false` | Cache target directories (useful for cross-compilation) |
| `cache-on-failure` | boolean | `true` | Save cache even if workflow fails |
| `cache-all-crates` | boolean | `false` | Cache all crates in workspace |
| `cache-workspace-crates` | boolean | `false` | Cache workspace crates |
| `save-if` | string | `"true"` | Condition for saving cache (e.g., `"${{ job.status == 'success' }}"`) |
| `lookup-only` | boolean | `false` | Only restore cache, don't save |
| `cache-provider` | string | `"github"` | Cache provider (`github`, `s3`, `gcs`, `azure`) |
| `cache-bin` | boolean | `true` | Cache Cargo binaries |

### Recommended Configuration

#### Basic Configuration (Most Jobs)

For most jobs (test, security, coverage, pre-commit), the default configuration is sufficient:

```yaml
- uses: Swatinem/rust-cache@v2
```

**Rationale:**
- Defaults handle dependency caching effectively
- Cache keys automatically include Rust version and `Cargo.lock` hash
- No need to cache on failure for most jobs (prevents caching broken builds)

#### Optimized Configuration (Test/Coverage Jobs)

For test and coverage jobs, consider disabling cache-on-failure to avoid caching broken builds:

```yaml
- uses: Swatinem/rust-cache@v2
  with:
    cache-on-failure: false
```

**Rationale:**
- Prevents caching artifacts from failed test runs
- Keeps cache clean and ensures only successful builds are cached

#### Cross-Compilation Configuration (Build-and-Release Job)

For the `build-and-release` job that uses multiple targets, enable `cache-targets`:

```yaml
- uses: Swatinem/rust-cache@v2
  with:
    cache-targets: true
    cache-on-failure: false
```

**Rationale:**
- `cache-targets: true` caches target-specific build artifacts for each cross-compilation target
- Significantly speeds up builds when switching between targets
- `cache-on-failure: false` prevents caching failed release builds

#### Optional: Job-Specific Cache Prefixes

If you want to separate caches by job type (useful for debugging or different cache strategies):

```yaml
# For security job
- uses: Swatinem/rust-cache@v2
  with:
    prefix-key: "security-"

# For test job
- uses: Swatinem/rust-cache@v2
  with:
    prefix-key: "test-"
```

**Note:** This is generally not necessary as the action already handles cache key uniqueness well.

### Cache Size Considerations

- GitHub Actions cache limit: **10 GB per repository**
- Caches are evicted after **7 days** of no access
- The action automatically manages cache size by using content-addressable keys
- Multiple targets in `build-and-release` will create separate cache entries per target

### Performance Expectations

With proper caching:
- **First run**: No cache hit, normal build time
- **Subsequent runs** (same dependencies): 50-80% faster builds
- **Dependency changes**: Partial cache hit, faster than no cache
- **Cross-compilation**: Significant speedup when switching between targets (with `cache-targets: true`)

### Implementation Recommendation

**Recommended approach:** Start with basic configuration for all jobs, then optimize based on observed performance:

1. **Phase 1**: Add basic `Swatinem/rust-cache@v2` to all jobs
2. **Phase 2**: Monitor cache hit rates and build times
3. **Phase 3**: Add `cache-targets: true` to `build-and-release` if cross-compilation is slow
4. **Phase 4**: Consider `cache-on-failure: false` for test/coverage jobs if needed

### Additional Resources

- [rust-cache GitHub Repository](https://github.com/Swatinem/rust-cache)
- [GitHub Actions Cache Documentation](https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows)
- [Rust CI Best Practices](https://github.com/actions-rs/meta/blob/master/recipes/quickstart.md)

### Cargo Install Caching

**Important:** The `rust-cache` action caches `~/.cargo/bin` by default (controlled by `cache-bin: true`), which means binaries installed via `cargo install` are automatically cached. This includes:
- `cargo-nextest` (installed in test, coverage, pre-commit, and build-and-release jobs)
- `cargo-deny`, `cargo-audit`, `cargo-geiger`, `cargo-auditable` (installed in security jobs)
- `cargo-llvm-cov` (installed in coverage job)

This significantly speeds up subsequent CI runs as these tools don't need to be recompiled.

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
